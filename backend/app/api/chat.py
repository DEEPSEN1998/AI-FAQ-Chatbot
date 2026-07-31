from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from backend.app.llm.model_registry import model_registry
from backend.app.llm.registry import provider_registry
from backend.app.models.chat import ChatRequest
from backend.app.services.chat_service import ChatService

router = APIRouter()
chat_service = ChatService()


@router.get("/models")
def get_models():
    """
    Endpoint listing all models across all providers grouped for model-centric frontend selector.
    """
    return [m.dict() for m in model_registry.get_all_models()]


@router.get("/providers")
def get_providers():
    """
    Backward-compatible endpoint for provider discovery.
    """
    return {"providers": [p.dict() for p in provider_registry.list_providers()]}


@router.post("/chat")
def chat(request: ChatRequest):
    """
    Synchronous POST chat endpoint.
    """
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    try:
        response_text = chat_service.process_message(
            session_id=request.session_id,
            message=request.message,
            model=request.model,
            provider=request.provider,
        )
        return {
            "response": response_text,
            "model": request.model,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
def chat_stream(request: ChatRequest):
    """
    Server-Sent Events (SSE) token streaming endpoint.
    """
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    def event_generator():
        try:
            for token in chat_service.process_message_stream(
                session_id=request.session_id,
                message=request.message,
                model=request.model,
                provider=request.provider,
            ):
                yield token
        except Exception as e:
            yield f"\n❌ System Error: {str(e)}"

    return StreamingResponse(event_generator(), media_type="text/event-stream")