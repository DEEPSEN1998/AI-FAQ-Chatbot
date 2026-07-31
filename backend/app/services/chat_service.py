from typing import Iterator, List, Optional
from langchain_core.documents import Document

from backend.app.llm.factory import LLMFactory
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
    4. On Cache Miss: RAG Document Retrieval -> Prompt Assembly -> LLM Provider Invocation -> Store Cache.
    5. Save assistant response into memory and return final answer.

    Follows SOLID principles:
    - Single Responsibility: Pipeline orchestration only.
    - Decoupled Model Selection: Resolves LLM provider automatically from selected model ID.
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
        self.query_router = query_router or QueryRouter()
        self.cache_service = cache_service or SemanticCacheService()
        self.memory_service = memory_service or _default_memory_service
        self.retriever = retriever or DocumentRetriever()
        self.prompt_builder = prompt_builder or PromptBuilder()

    def process_message(
        self,
        session_id: str,
        message: str,
        model: Optional[str] = None,
        provider: Optional[str] = None,
    ) -> str:
        """
        Synchronously process user message and return complete response.
        """
        clean_message = message.strip()
        if not clean_message:
            return "Please provide a valid message."

        # 1. Store user message in memory
        self.memory_service.add_message(session_id, "user", clean_message)

        # 2. Classify intent via Query Router
        category, direct_response = self.query_router.classify_and_route(clean_message)
        if category != QueryCategory.COMPANY_QUESTION and direct_response is not None:
            return self._handle_direct_response(session_id, direct_response)

        # 3. Check Semantic Cache
        cached_result = self.cache_service.get_cached_answer(clean_message)
        if cached_result is not None:
            return self._store_response(session_id, cached_result.answer)

        # 4. RAG Retrieval & Prompt Assembly
        prompt, source_files, chunk_ids = self._assemble_rag_context(session_id, clean_message)

        # 5. Resolve provider automatically from model ID
        llm_provider = (
            LLMFactory.get_provider_for_model(model)
            if model
            else LLMFactory.get_provider(provider)
        )
        response = llm_provider.generate(prompt=prompt, model=model)

        # 6. Cache & Save Response
        if response and response.strip() and not response.startswith("❌ Error:"):
            self.cache_service.store_cached_answer(
                question=clean_message,
                answer=response,
                source_files=source_files,
                chunk_ids=chunk_ids,
            )

        return self._store_response(session_id, response)

    def process_message_stream(
        self,
        session_id: str,
        message: str,
        model: Optional[str] = None,
        provider: Optional[str] = None,
    ) -> Iterator[str]:
        """
        Stream tokens chunk-by-chunk for real-time typing animation.
        """
        clean_message = message.strip()
        if not clean_message:
            yield "Please provide a valid message."
            return

        # 1. Store user message
        self.memory_service.add_message(session_id, "user", clean_message)

        # 2. Intent Router Direct Response
        category, direct_response = self.query_router.classify_and_route(clean_message)
        if category != QueryCategory.COMPANY_QUESTION and direct_response is not None:
            self._store_response(session_id, direct_response)
            yield direct_response
            return

        # 3. Semantic Answer Cache Check
        cached_result = self.cache_service.get_cached_answer(clean_message)
        if cached_result is not None:
            self._store_response(session_id, cached_result.answer)
            yield cached_result.answer
            return

        # 4. RAG Context Assembly
        prompt, source_files, chunk_ids = self._assemble_rag_context(session_id, clean_message)

        # 5. Resolve provider automatically from model ID
        llm_provider = (
            LLMFactory.get_provider_for_model(model)
            if model
            else LLMFactory.get_provider(provider)
        )

        full_response_chunks = []

        for token in llm_provider.stream_generate(prompt=prompt, model=model):
            full_response_chunks.append(token)
            yield token

        full_response = "".join(full_response_chunks).strip()

        # 6. Cache & Save Response
        if full_response and not full_response.startswith("❌ Error:"):
            self.cache_service.store_cached_answer(
                question=clean_message,
                answer=full_response,
                source_files=source_files,
                chunk_ids=chunk_ids,
            )
            self._store_response(session_id, full_response)

    def _assemble_rag_context(self, session_id: str, query: str):
        """
        Private helper for RAG retrieval and prompt assembly.
        """
        message_lower = query.lower()
        k = 10 if any(keyword in message_lower for keyword in self.LIST_KEYWORDS) else 4

        doc_results = self.retriever.retrieve(query, k=k)
        documents: List[Document] = [doc for doc, score in doc_results]

        source_files = list(
            {doc.metadata.get("source_file", doc.metadata.get("source", "unknown")) for doc in documents}
        )
        chunk_ids = [
            doc.metadata.get("chunk_id", doc.metadata.get("id", f"chunk_{i}")) for i, doc in enumerate(documents)
        ]

        history = self.memory_service.get_history(session_id, limit=10)
        prompt = self.prompt_builder.build_prompt(
            history=history,
            documents=documents,
            question=query,
        )

        return prompt, source_files, chunk_ids

    def _handle_direct_response(self, session_id: str, response: str) -> str:
        return self._store_response(session_id, response)

    def _store_response(self, session_id: str, response: str) -> str:
        self.memory_service.add_message(session_id, "assistant", response)
        return response


# Global singleton instance for module-level compatibility
_default_chat_service = ChatService()


def chat_with_ai(
    session_id: str,
    message: str,
    model: Optional[str] = None,
    provider: Optional[str] = None,
) -> str:
    return _default_chat_service.process_message(
        session_id=session_id, message=message, model=model, provider=provider
    )