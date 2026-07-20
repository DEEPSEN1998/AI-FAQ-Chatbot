from fastapi import APIRouter
from backend.app.models.chat import ChatRequest
from backend.app.services.chat_service import chat_with_ai

router = APIRouter()

@router.post("/chat")
def chat(request: ChatRequest):
    return {
        "response": chat_with_ai(
            request.session_id,
            request.message
        )
    }