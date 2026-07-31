from typing import Dict, List, Optional


class MemoryService:
    """
    Session Conversation Memory Management Service.

    Follows SOLID principles:
    - Single Responsibility: Manages in-memory message history per user session.
    """

    def __init__(self, max_history_per_session: int = 20):
        """
        Initialize MemoryService.

        Args:
            max_history_per_session (int): Maximum number of messages to retain per session.
        """
        self.max_history_per_session = max_history_per_session
        self._memory_store: Dict[str, List[Dict[str, str]]] = {}

    def get_history(self, session_id: str, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Get conversation history for a session ID.

        Args:
            session_id (str): Unique session identifier.
            limit (Optional[int]): Optional max count of recent history entries to return.

        Returns:
            List[Dict[str, str]]: List of history message dictionaries.
        """
        history = self._memory_store.get(session_id, [])
        if limit is not None and limit > 0:
            return history[-limit:]
        return list(history)

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """
        Add a message to the session history.

        Args:
            session_id (str): Unique session identifier.
            role (str): Role name ('user' or 'assistant').
            content (str): Message content.
        """
        if session_id not in self._memory_store:
            self._memory_store[session_id] = []

        self._memory_store[session_id].append({
            "role": role,
            "content": content,
        })

        # Trim excess history entries to bound memory usage
        if len(self._memory_store[session_id]) > self.max_history_per_session:
            self._memory_store[session_id] = self._memory_store[session_id][-self.max_history_per_session:]

    def clear_history(self, session_id: str) -> None:
        """
        Clear conversation history for a specific session.

        Args:
            session_id (str): Session identifier to clear.
        """
        self._memory_store.pop(session_id, None)


# Default singleton instance for module-level access
_default_memory_service = MemoryService()


def get_history(session_id: str, limit: Optional[int] = None) -> List[Dict[str, str]]:
    """Functional wrapper for getting session history."""
    return _default_memory_service.get_history(session_id=session_id, limit=limit)


def add_message(session_id: str, role: str, content: str) -> None:
    """Functional wrapper for adding session message."""
    _default_memory_service.add_message(session_id=session_id, role=role, content=content)


def clear_history(session_id: str) -> None:
    """Functional wrapper for clearing session history."""
    _default_memory_service.clear_history(session_id=session_id)