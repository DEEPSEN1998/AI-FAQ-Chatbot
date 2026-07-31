from typing import List, Optional, Tuple
from langchain_core.documents import Document

from backend.app.rag.vector_store import get_vector_store


class DocumentRetriever:
    """
    Production-grade Document Retriever for Knowledge Base RAG pipeline.

    Key Features:
    - Filters weak vector similarity matches using max_distance threshold.
    - Deduplicates identical or highly overlapping document chunks.
    - Preserves rich metadata (source_file, page_number, section_name, chunk_id).
    - Modular architecture supporting custom vector stores via Dependency Injection.

    Follows SOLID principles:
    - Single Responsibility: Exclusively responsible for searching, filtering, and deduplicating context documents.
    """

    def __init__(
        self,
        vector_store=None,
        max_distance: float = 1.00,
    ):
        """
        Initialize DocumentRetriever.

        Args:
            vector_store: ChromaDB vector store instance (defaults to persistent store).
            max_distance (float): Maximum vector distance threshold allowed (results with distance > max_distance are filtered out).
        """
        self.vector_store = vector_store or get_vector_store()
        self.max_distance = max_distance

    def retrieve(
        self,
        query: str,
        k: int = 4,
        max_distance: Optional[float] = None,
    ) -> List[Tuple[Document, float]]:
        """
        Retrieve, filter, and deduplicate top k relevant documents with similarity scores.

        Args:
            query (str): Search query string.
            k (int): Number of top matches to return.
            max_distance (Optional[float]): Threshold override for filtering weak matches.

        Returns:
            List[Tuple[Document, float]]: Deduplicated, score-filtered list of (Document, distance) tuples.
        """
        clean_query = query.strip()
        if not clean_query:
            return []

        effective_max_distance = (
            max_distance if max_distance is not None else self.max_distance
        )

        # Retrieve a expanded candidate pool to allow room for filtering & deduplication
        fetch_k = max(k * 2, 8)
        raw_results = self.vector_store.similarity_search_with_score(
            query=clean_query,
            k=fetch_k,
        )

        filtered_results: List[Tuple[Document, float]] = []
        seen_contents = set()
        seen_chunk_ids = set()

        for doc, distance in raw_results:
            # 1. Filter out weak similarity matches (distance > threshold)
            if distance > effective_max_distance:
                continue

            chunk_id = doc.metadata.get("chunk_id", doc.metadata.get("id"))
            content_snippet = doc.page_content.strip()[:150]

            # 2. Deduplicate identical chunk IDs or exact text snippets
            if chunk_id and chunk_id in seen_chunk_ids:
                continue
            if content_snippet in seen_contents:
                continue

            if chunk_id:
                seen_chunk_ids.add(chunk_id)
            seen_contents.add(content_snippet)

            filtered_results.append((doc, float(distance)))

            # Limit output to requested k top matches
            if len(filtered_results) >= k:
                break

        return filtered_results


# Default module instance for backward compatibility
_default_retriever = DocumentRetriever()


def retrieve_documents(query: str, k: int = 4) -> List[Tuple[Document, float]]:
    """
    Backward-compatible functional interface for document retrieval.
    """
    return _default_retriever.retrieve(query=query, k=k)