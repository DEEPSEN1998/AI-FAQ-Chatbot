# backend/app/services/memory_service.py

memory_store = {}


def get_history(session_id: str):
    """Return conversation history for a session."""
    return memory_store.get(session_id, [])


def add_message(session_id: str, role: str, content: str):
    """Add a message to the session history."""
    if session_id not in memory_store:
        memory_store[session_id] = []

    memory_store[session_id].append({
        "role": role,
        "content": content
    })


def clear_history(session_id: str):
    """Clear conversation for one session."""
    memory_store.pop(session_id, None)