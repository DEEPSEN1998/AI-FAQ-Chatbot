from typing import List, Optional
from langchain_core.documents import Document

from backend.app.llm.ollama_service import call_ollama
from backend.app.models.cache import CacheResult
from backend.app.rag.retriever import DocumentRetriever
from backend.app.services.cache_service import SemanticCacheService
from backend.app.services.memory_service import MemoryService, _default_memory_service
from backend.app.services.prompt_builder import PromptBuilder
from backend.app.services.query_router import QueryCategory, QueryRouter


class ChatService:
    """
    Orchestration service for the AI FAQ Chatbot pipeline.

    Flow:
    1. Record incoming user message into session memory.
    2. Intent Routing (Greetings, Farewells, Thanks, Small Talk -> Direct Response).
    3. Semantic Answer Cache check (Cache Hit -> Immediate Return).
    4. On Cache Miss: RAG Document Retrieval -> Prompt Assembly -> LLM Invocation -> Store Cache.
    5. Save assistant response into memory and return final answer.

    Follows SOLID principles:
    - Single Responsibility: Pipeline orchestration only. Delegates sub-tasks to dedicated services.
    - Open/Closed & Dependency Injection: Services can be replaced or mocked via constructor parameters.
    """

    LIST_KEYWORDS = [
        "portfolio",
        "projects",
        "project",
        "all",
        "list",
        "show",
        "services",
        "technologies",
        "team",
        "developers",
        "employees",
    ]

    def __init__(
        self,
        query_router: Optional[QueryRouter] = None,
        cache_service: Optional[SemanticCacheService] = None,
        memory_service: Optional[MemoryService] = None,
        retriever: Optional[DocumentRetriever] = None,
        prompt_builder: Optional[PromptBuilder] = None,
    ):
        """
        Initialize ChatService with optional sub-service overrides for dependency injection.
        """
        self.query_router = query_router or QueryRouter()
        self.cache_service = cache_service or SemanticCacheService()
        self.memory_service = memory_service or _default_memory_service
        self.retriever = retriever or DocumentRetriever()
        self.prompt_builder = prompt_builder or PromptBuilder()

    def process_message(self, session_id: str, message: str) -> str:
        """
        Process incoming user message through the orchestration pipeline.

        Args:
            session_id (str): Session identifier.
            message (str): User message.

        Returns:
            str: Final response string.
        """
        clean_message = message.strip()
        if not clean_message:
            return "Please provide a valid message."

        # 1. Store user message in memory history
        self.memory_service.add_message(session_id, "user", clean_message)

        # 2. Classify intent via Query Router
        category, direct_response = self.query_router.classify_and_route(clean_message)

        # 3. Handle direct conversational responses immediately
        if category != QueryCategory.COMPANY_QUESTION and direct_response is not None:
            return self._handle_direct_response(session_id, direct_response)

        # 4. Check Semantic Cache for existing Q&A match
        cached_result = self._handle_cache(clean_message)
        if cached_result is not None:
            return self._store_response(session_id, cached_result.answer)

        # 5. Generate LLM response on cache miss via RAG pipeline
        llm_response = self._generate_llm_response(session_id, clean_message)

        # 6. Save final assistant response and return
        return self._store_response(session_id, llm_response)

    def _handle_direct_response(self, session_id: str, response: str) -> str:
        """
        Handle direct responses (Greetings, Farewells, Thanks, Small Talk) without LLM/RAG calls.
        """
        return self._store_response(session_id, response)

    def _handle_cache(self, query: str) -> Optional[CacheResult]:
        """
        Query the semantic cache for an existing answer.
        """
        return self.cache_service.get_cached_answer(query)

    def _generate_llm_response(self, session_id: str, query: str) -> str:
        """
        Execute RAG document retrieval, prompt synthesis, LLM generation, and cache storage.
        """
        # Determine retrieval k based on query keywords
        message_lower = query.lower()
        k = 10 if any(keyword in message_lower for keyword in self.LIST_KEYWORDS) else 4

        # Retrieve top documents from vector store
        doc_results = self.retriever.retrieve(query, k=k)
        documents: List[Document] = [doc for doc, score in doc_results]

        # Collect source and chunk references for provenance caching
        source_files = list(
            {doc.metadata.get("source_file", doc.metadata.get("source", "unknown")) for doc in documents}
        )
        chunk_ids = [doc.metadata.get("chunk_id", doc.metadata.get("id", f"chunk_{i}")) for i, doc in enumerate(documents)]

        # Retrieve session conversation history
        history = self.memory_service.get_history(session_id, limit=10)

        # Build prompt and invoke Ollama LLM
        prompt = self.prompt_builder.build_prompt(
            history=history,
            documents=documents,
            question=query,
        )
        response = call_ollama(prompt)

        # Cache generated response for future queries
        if response and response.strip():
            self.cache_service.store_cached_answer(
                question=query,
                answer=response,
                source_files=source_files,
                chunk_ids=chunk_ids,
            )

        return response

    def _store_response(self, session_id: str, response: str) -> str:
        """
        Save assistant response into session memory history.
        """
        self.memory_service.add_message(session_id, "assistant", response)
        return response


# Global singleton instance for module-level compatibility
_default_chat_service = ChatService()


def chat_with_ai(session_id: str, message: str) -> str:
    """
    Module-level function interface for chatting with AI assistant.
    """
    return _default_chat_service.process_message(session_id=session_id, message=message)