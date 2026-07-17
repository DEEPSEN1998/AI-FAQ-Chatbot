from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="AI FAQ Chatbot API",
    description="Backend API for the AI FAQ Chatbot",
    version="1.0.0"
)

class ChatRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {
        "status": "success",
        "message": "AI FAQ Chatbot Backend is Running 🚀"
    }


@app.post("/chat")
def chat(request: ChatRequest):
    return {
        "user_message": request.message,
        "bot_reply": f"You said: {request.message}"
    }