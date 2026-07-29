from backend.app.rag.vector_store import get_vector_store


def retrieve_documents(query: str, k: int = 4):
    """
    Retrieve the most relevant chunks with similarity scores.
    """

    db = get_vector_store()

    results = db.similarity_search_with_score(
        query=query,
        k=k,
    )

    return results