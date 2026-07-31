import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from langchain_chroma import Chroma
from backend.app.config import (
    CACHE_COLLECTION_NAME,
    CACHE_DEDUPLICATION_THRESHOLD,
    CACHE_DISTANCE_THRESHOLD,
    CACHE_MAX_RESULTS,
    KB_VERSION,
    VECTOR_DB_DIR,
)
from backend.app.models.cache import CacheResult
from backend.app.rag.embeddings import get_embeddings


class SemanticCacheService:
    """
    Production-ready Semantic Answer Cache Service using ChromaDB.

    Key Capabilities:
    - Semantic similarity matching using BAAI/bge-small-en-v1.5 embeddings.
    - Prevents cache pollution via deduplication check before insertion.
    - Lightweight provenance metadata tracking (source_files, chunk_ids, kb_version).
    - Metadata-filtered queries targeting only current knowledge-base version (preventing stale responses).
    - Cache invalidation and collection reset support using 100% public LangChain APIs.

    Follows SOLID principles:
    - Single Responsibility: Exclusively manages semantic answer cache logic and lifecycle.
    - Open/Closed: Thresholds, collection names, and knowledge base versions are injected via config/params.
    - Interface Segregation: Returns strongly-typed CacheResult dataclass instances.
    """

    def __init__(
        self,
        collection_name: str = CACHE_COLLECTION_NAME,
        distance_threshold: float = CACHE_DISTANCE_THRESHOLD,
        deduplication_threshold: float = CACHE_DEDUPLICATION_THRESHOLD,
        max_results: int = CACHE_MAX_RESULTS,
        kb_version: str = KB_VERSION,
        persist_directory: Optional[Path] = None,
    ):
        """
        Initialize SemanticCacheService with configurable thresholds and parameters.

        Args:
            collection_name (str): ChromaDB collection name for caching.
            distance_threshold (float): L2 distance threshold for cache hits (lower distance = higher similarity).
            deduplication_threshold (float): L2 distance threshold for identifying existing identical questions.
            max_results (int): Max number of cache lookup candidates.
            kb_version (str): Knowledge base version tag.
            persist_directory (Optional[Path]): Storage directory for ChromaDB vector persistent storage.
        """
        self.collection_name = collection_name
        self.distance_threshold = distance_threshold
        self.deduplication_threshold = deduplication_threshold
        self.max_results = max_results
        self.kb_version = kb_version
        self.persist_directory = str(persist_directory or VECTOR_DB_DIR)
        self.embeddings = get_embeddings()

        self._vector_store = Chroma(
            collection_name=self.collection_name,
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
        )

    def exists(self, question: str, threshold: Optional[float] = None) -> bool:
        """
        Check if an equivalent or semantically identical question already exists in the cache.

        Args:
            question (str): User question to check.
            threshold (Optional[float]): Custom distance threshold for deduplication. Defaults to self.deduplication_threshold.

        Returns:
            bool: True if an equivalent question exists within the deduplication threshold, False otherwise.
        """
        clean_question = question.strip()
        if not clean_question:
            return False

        effective_threshold = threshold if threshold is not None else self.deduplication_threshold

        # Filter by current knowledge-base version using standard public filter API
        results = self._vector_store.similarity_search_with_score(
            query=clean_question,
            k=1,
            filter={"kb_version": self.kb_version},
        )

        if not results:
            return False

        _, distance = results[0]
        return distance <= effective_threshold

    def get_cached_answer(self, query: str) -> Optional[CacheResult]:
        """
        Look up a semantically matching cached answer for the given user query.

        Args:
            query (str): Incoming user message or question.

        Returns:
            Optional[CacheResult]: Strongly-typed CacheResult if similarity distance is within threshold and
            kb_version matches, otherwise None.
        """
        clean_query = query.strip()
        if not clean_query:
            return None

        # Filter candidates by current knowledge base version to avoid stale cached answers
        results = self._vector_store.similarity_search_with_score(
            query=clean_query,
            k=self.max_results,
            filter={"kb_version": self.kb_version},
        )

        if not results:
            return None

        doc, distance = results[0]

        if distance <= self.distance_threshold:
            current_hit_count = doc.metadata.get("hit_count", 0) + 1
            cache_id = doc.metadata.get("cache_id")

            # Parse metadata lists securely
            source_files_raw = doc.metadata.get("source_files", "")
            source_files = source_files_raw.split(",") if source_files_raw else []

            chunk_ids_raw = doc.metadata.get("chunk_ids", "")
            chunk_ids = chunk_ids_raw.split(",") if chunk_ids_raw else []

            # Prepare updated metadata for hit count tracking
            updated_metadata = dict(doc.metadata)
            updated_metadata["hit_count"] = current_hit_count
            updated_metadata["last_accessed"] = datetime.now(timezone.utc).isoformat()

            # Update hit count using standard public LangChain Chroma API (add_texts with existing ID upserts entry)
            if cache_id:
                try:
                    self._vector_store.add_texts(
                        texts=[doc.page_content],
                        metadatas=[updated_metadata],
                        ids=[cache_id],
                    )
                except Exception:
                    # Non-blocking hit count update fallback
                    pass

            return CacheResult(
                question=doc.metadata.get("question", doc.page_content),
                answer=doc.metadata.get("answer", ""),
                score=float(distance),
                timestamp=doc.metadata.get("timestamp", ""),
                hit_count=current_hit_count,
                kb_version=doc.metadata.get("kb_version", self.kb_version),
                source_files=source_files,
                chunk_ids=chunk_ids,
            )

        return None

    def store_cached_answer(
        self,
        question: str,
        answer: str,
        source_files: Optional[List[str]] = None,
        chunk_ids: Optional[List[str]] = None,
    ) -> Optional[str]:
        """
        Store a new Q&A pair along with lightweight metadata into the semantic cache.

        Args:
            question (str): Original user question.
            answer (str): Generated answer from LLM.
            source_files (Optional[List[str]]): List of source filename references.
            chunk_ids (Optional[List[str]]): List of document chunk IDs used to build answer.

        Returns:
            Optional[str]: Unique cache entry ID if saved successfully, or None if skipped due to deduplication.
        """
        clean_question = question.strip()
        clean_answer = answer.strip()

        if not clean_question or not clean_answer:
            return None

        # Prevent duplicate entries via dedicated deduplication check
        if self.exists(clean_question):
            return None

        cache_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        source_files_str = ",".join(source_files) if source_files else ""
        chunk_ids_str = ",".join(chunk_ids) if chunk_ids else ""

        metadata = {
            "cache_id": cache_id,
            "question": clean_question,
            "answer": clean_answer,
            "kb_version": self.kb_version,
            "timestamp": timestamp,
            "hit_count": 1,
            "source_files": source_files_str,
            "chunk_ids": chunk_ids_str,
        }

        self._vector_store.add_texts(
            texts=[clean_question],
            metadatas=[metadata],
            ids=[cache_id],
        )

        return cache_id

    def clear_cache(self) -> None:
        """
        Safely invalidate and reset the entire answer cache collection using standard public API.
        """
        try:
            self._vector_store.delete_collection()
            # Re-instantiate empty collection vector store reference
            self._vector_store = Chroma(
                collection_name=self.collection_name,
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to clear semantic cache collection: {str(e)}") from e

    def invalidate_cache(self) -> None:
        """
        Alias for clear_cache to support full knowledge base re-indexing invalidation workflows.
        """
        self.clear_cache()
