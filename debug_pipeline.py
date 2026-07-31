import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.rag.loader import load_documents
from backend.app.rag.splitter import split_documents
from backend.app.rag.vector_store import get_vector_store
from backend.app.rag.retriever import DocumentRetriever
from backend.app.services.prompt_builder import build_prompt
from backend.app.llm.ollama_service import call_ollama


def run_debug():
    print("=" * 80)
    print("STEP 1: VERIFY DOCUMENT INGESTION")
    print("=" * 80)

    docs = load_documents()
    print(f"Total raw documents loaded: {len(docs)}")

    keywords = ["Sounak Kar", "Deep Sen", "RideOM", "Pandey Coaching", "GoAhead AI", "founder", "Leadership"]

    for i, doc in enumerate(docs):
        file_name = doc.metadata.get("source", doc.metadata.get("file_name", "Unknown"))
        page_num = doc.metadata.get("page", 1)
        text_len = len(doc.page_content)
        print(f"\nDocument #{i+1}: File={file_name}, Page={page_num}, Text Length={text_len}")
        print("Sample Content (First 300 chars):")
        print(doc.page_content[:300])
        print("-" * 50)

        print("Keyword presence check in raw extracted document text:")
        for kw in keywords:
            found = kw.lower() in doc.page_content.lower()
            print(f"  - '{kw}': {'FOUND' if found else 'NOT FOUND'}")

    print("\n" + "=" * 80)
    print("STEP 2: VERIFY CHUNKING")
    print("=" * 80)

    chunks = split_documents(docs)
    print(f"Total chunks created: {len(chunks)}")

    for i, chunk in enumerate(chunks):
        chunk_id = chunk.metadata.get("chunk_id", f"chunk_{i}")
        section = chunk.metadata.get("section_name", "General")
        page = chunk.metadata.get("page_number", 1)
        source = chunk.metadata.get("source_file", "Unknown")

        print(f"\n--- Chunk #{i+1} ---")
        print(f"Chunk ID : {chunk_id}")
        print(f"Section  : {section}")
        print(f"Page     : {page}")
        print(f"Source   : {source}")
        print(f"Text Length: {len(chunk.page_content)}")
        print("Text Content:")
        print(chunk.page_content)
        print("-" * 50)

    print("\n" + "=" * 80)
    print("STEP 3: VERIFY CHROMADB")
    print("=" * 80)

    db = get_vector_store()
    try:
        col = db._collection
        count = col.count()
        print(f"ChromaDB Collection Name: {col.name}")
        print(f"Total stored items in default vector db collection: {count}")
        peek_data = col.peek(limit=5)
        print("Sample Metadatas in DB:", peek_data.get("metadatas"))
    except Exception as e:
        print(f"Error inspecting ChromaDB directly: {e}")

    print("\n" + "=" * 80)
    print("STEP 4: VERIFY RETRIEVAL FOR TEST QUERIES")
    print("=" * 80)

    retriever = DocumentRetriever(max_distance=2.0)  # High threshold to observe all scores

    test_queries = [
        "Who is the founder?",
        "Who is Sounak Kar?",
        "Who is Deep Sen?",
        "List portfolio projects.",
        "What services do you provide?",
    ]

    for q in test_queries:
        print(f"\n" + "#" * 60)
        print(f"QUERY: '{q}'")
        print("#" * 60)

        results = retriever.retrieve(q, k=4, max_distance=2.0)
        print(f"Retrieved {len(results)} chunks:")

        for idx, (doc, score) in enumerate(results, start=1):
            print(f"\n  Match #{idx}:")
            print(f"  Similarity Score (L2 Distance): {score:.4f}")
            print(f"  Chunk ID    : {doc.metadata.get('chunk_id')}")
            print(f"  Section     : {doc.metadata.get('section_name')}")
            print(f"  Page        : {doc.metadata.get('page_number')}")
            print(f"  Source File : {doc.metadata.get('source_file')}")
            print(f"  Text Content:\n{doc.page_content}")
            print("  " + "-" * 40)

    print("\n" + "=" * 80)
    print("STEP 5 & 6: VERIFY PROMPT BUILDER AND OLLAMA OUTPUT")
    print("=" * 80)

    sample_query = "Who is the founder?"
    results = retriever.retrieve(sample_query, k=4, max_distance=2.0)
    sample_docs = [doc for doc, score in results]
    history = []

    prompt = build_prompt(history=history, documents=sample_docs, question=sample_query)
    print("\nEXACT PROMPT SENT TO OLLAMA:\n")
    print(prompt)

    print("\n" + "-" * 50)
    print("CALLING OLLAMA WITH PROMPT...")
    try:
        raw_response = call_ollama(prompt)
        print("\nRAW OLLAMA RESPONSE:\n")
        print(raw_response)
    except Exception as e:
        print(f"\nOllama call result: {e}")


if __name__ == "__main__":
    run_debug()
