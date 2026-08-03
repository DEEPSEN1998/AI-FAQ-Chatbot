"""Central configuration loaded from environment variables.

Only this module reads environment variables. Keeping configuration in one
place makes local development and container deployment behave the same way.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
# The project-root .env is the documented location. The backend/.env fallback
# preserves compatibility with the previous project layout during migration.
ENV_FILE = PROJECT_ROOT / ".env"
if not ENV_FILE.exists():
    legacy_env_file = PROJECT_ROOT / "backend" / ".env"
    ENV_FILE = legacy_env_file if legacy_env_file.exists() else ENV_FILE
load_dotenv(ENV_FILE)


def _csv_setting(name: str, default: str) -> list[str]:
    """Return a comma-separated environment setting as a clean list."""
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


# App settings
APP_NAME = os.getenv("APP_NAME", "K8ight AI Chat Bot Assistant")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
DEBUG = ENVIRONMENT == "development"
ALLOWED_ORIGINS = _csv_setting("ALLOWED_ORIGINS", "http://localhost:8000")
ALLOWED_HOSTS = _csv_setting("ALLOWED_HOSTS", "localhost,127.0.0.1")

# Generated runtime data is deliberately outside source code and not committed.
DATA_DIR = Path(os.getenv("DATA_DIR", PROJECT_ROOT / "data"))
CHROMA_DIR = DATA_DIR / "chroma"
SQLITE_PATH = DATA_DIR / "app.db"
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"

# NVIDIA NIM settings. The same API key is used for chat and embeddings.
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "").strip()
NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1").rstrip("/")
NVIDIA_CHAT_MODEL = os.getenv("NVIDIA_CHAT_MODEL", "meta/llama-3.1-8b-instruct")
NVIDIA_EMBEDDING_MODEL = os.getenv("NVIDIA_EMBEDDING_MODEL", "nvidia/nv-embedqa-e5-v5")
NVIDIA_TIMEOUT_SECONDS = float(os.getenv("NVIDIA_TIMEOUT_SECONDS", "60"))

# RAG settings. A smaller context keeps latency and NIM cost predictable.
CHROMA_COLLECTION = "company_knowledge"
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "900"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))
RETRIEVAL_LIMIT = int(os.getenv("RETRIEVAL_LIMIT", "4"))
MAX_CONTEXT_CHARACTERS = int(os.getenv("MAX_CONTEXT_CHARACTERS", "7000"))
