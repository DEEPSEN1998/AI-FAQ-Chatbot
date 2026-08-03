"""HTTP API and static-site entry point for the FAQ assistant."""

import logging
from contextlib import asynccontextmanager
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app.config import ALLOWED_HOSTS, ALLOWED_ORIGINS, APP_NAME, DEBUG, PROJECT_ROOT
from backend.app.database import create_lead, initialize_database
from backend.app.models import ChatRequest, ChatResponse, LeadCreate, LeadResponse
from backend.app.rag import answer_question


logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)
logger = logging.getLogger(__name__)
FRONTEND_DIR = PROJECT_ROOT / "frontend"


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Create the SQLite schema before the application accepts traffic."""
    initialize_database()
    yield


app = FastAPI(title=APP_NAME, version="2.0.0", docs_url="/docs" if DEBUG else None, lifespan=lifespan)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS)
# File previews have the browser origin `null`; allow it only in development.
# Production allows only the explicitly configured HTTPS origins.
cors_origins = [*ALLOWED_ORIGINS, "null"] if DEBUG else ALLOWED_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1):\d+$" if DEBUG else None,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Attach a request ID, safe browser headers, and structured request logging."""
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    started_at = perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; script-src 'self'"
    logger.info("%s %s -> %s in %.3fs", request.method, request.url.path, response.status_code, perf_counter() - started_at)
    return response


@app.get("/health")
def health() -> dict[str, str]:
    """Load-balancer health check. It does not call the paid NVIDIA API."""
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    """Answer one company question using Chroma retrieval and NVIDIA NIM."""
    try:
        answer, sources = answer_question(payload.message)
        return ChatResponse(answer=answer, sources=sources)
    except RuntimeError as error:
        # Configuration/upstream errors are safe to show because their messages are curated.
        raise HTTPException(status_code=503, detail=str(error)) from error
    except Exception as error:
        logger.exception("Unexpected chat failure")
        raise HTTPException(status_code=500, detail="The assistant could not answer right now. Please try again.") from error


@app.post("/api/leads", response_model=LeadResponse, status_code=201)
def submit_lead(payload: LeadCreate) -> LeadResponse:
    """Validate and persist a lead in SQLite; no lead data is sent to NVIDIA."""
    try:
        lead_id = create_lead(payload)
        return LeadResponse(id=lead_id, message="Thanks - we will be in touch soon.")
    except Exception as error:
        logger.exception("Lead persistence failure")
        raise HTTPException(status_code=500, detail="We could not save your request. Please try again.") from error


# Keep CSS and JavaScript available with the same relative paths used by the
# standalone frontend, so the UI also works in a simple local static server.
app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="js")


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    """Serve the small, dependency-free browser client."""
    return FileResponse(FRONTEND_DIR / "index.html")
