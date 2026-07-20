from backend.app.llm.ollama_service import call_ollama

def chat_with_ai(message: str):
    return call_ollama(message)