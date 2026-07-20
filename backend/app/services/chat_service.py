from backend.app.llm.ollama_service import call_ollama
from backend.app.services.prompt_builder import build_prompt

from backend.app.services.memory_service import (
    add_message,
    get_history
)


def chat_with_ai(session_id: str, message: str):

    add_message(session_id, "user", message)

    # Keep only the latest 10 messages
    history = get_history(session_id)[-10:]

    prompt = build_prompt(history)
    print(prompt)
    response = call_ollama(prompt) 

    add_message(session_id, "assistant", response)

    return response