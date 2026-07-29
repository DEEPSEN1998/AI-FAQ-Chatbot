from langchain_chroma import Chroma

from backend.app.config import VECTOR_DB_DIR
from backend.app.rag.embeddings import get_embeddings


def get_vector_store():
    """
    Return a persistent ChromaDB instance.
    """

    embeddings = get_embeddings()

    vector_store = Chroma(
        persist_directory=str(VECTOR_DB_DIR),
        embedding_function=embeddings,
    )

    return vector_store