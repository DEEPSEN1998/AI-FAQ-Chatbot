from app.rag.vector_store import get_vector_store


def retrieve_documents(query: str, k: int = 4):
    """
    Retrieve the most relevant chunks for a query.
    """

    db = get_vector_store()

    results = db.similarity_search(
        query=query,
        k=k,
    )

    return results