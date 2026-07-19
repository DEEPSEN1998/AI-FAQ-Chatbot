from fastapi import FastAPI
from pydantic import BaseModel
from backend.app.llm.ollama_service import call_ollama
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="AI FAQ Chatbot API",
    description="Backend API for the AI FAQ Chatbot",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {
        "status": "success",
        "message": "Backend is Running 🚀"
    }


@app.post("/chat")
def chat(request: ChatRequest):
    answer = call_ollama(request.message)
    
    return {
        
        "response": answer
    }