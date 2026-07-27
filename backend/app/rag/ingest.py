from app.rag.loader import load_documents
from app.rag.splitter import split_documents
from app.rag.vector_store import get_vector_store


def ingest_documents(reset_db=True):
    """
    Load, split, embed and store documents in ChromaDB.
    """

    print("Loading documents...")
    documents = load_documents()
    print(f"Loaded {len(documents)} documents")

    print("Splitting documents...")
    chunks = split_documents(documents)
    print(f"Created {len(chunks)} chunks")

    print("Loading vector store...")
    db = get_vector_store()

    if reset_db:
        print("Clearing existing database...")
        db.delete_collection()
        db = get_vector_store()

    print("Adding chunks...")
    db.add_documents(chunks)

    print(f"Stored {len(chunks)} chunks.")