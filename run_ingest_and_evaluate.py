import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.rag.ingest import ingest_documents
from backend.app.rag.vector_store import get_vector_store


def main():
    print("=" * 80)
    print("1. RE-INGESTING DOCUMENTS INTO CHROMADB...")
    print("=" * 80)
    ingest_documents(reset_db=True)

    print("\n" + "=" * 80)
    print("2. COMPUTING DISTANCE DISTRIBUTION FOR TARGET VS NOISE QUERIES...")
    print("=" * 80)

    db = get_vector_store()

    target_queries = [
        "Who is the founder?",
        "Who is Sounak Kar?",
        "Who is Deep Sen?",
        "List portfolio projects.",
        "What services do you provide?",
        "What is the backend tech stack?",
    ]

    noise_queries = [
        "What is the capital of France?",
        "How do I bake a chocolate cake?",
        "Tell me a joke about astronauts.",
    ]

    print("\n--- TARGET QUERIES (RELEVANT MATCHES) ---")
    target_scores = []
    for q in target_queries:
        results = db.similarity_search_with_score(query=q, k=2)
        print(f"\nQuery: '{q}'")
        for rank, (doc, score) in enumerate(results, start=1):
            target_scores.append(score)
            source_file = doc.metadata.get("source_file", "unknown")
            section = doc.metadata.get("section_name", "unknown")
            snippet = doc.page_content.strip()[:100].replace("\n", " ")
            print(f"  Rank #{rank} | L2 Distance: {score:.4f} | Section: {section} | Content: {snippet}...")

    print("\n--- UNRELATED NOISE QUERIES ---")
    noise_scores = []
    for q in noise_queries:
        results = db.similarity_search_with_score(query=q, k=2)
        print(f"\nQuery: '{q}'")
        for rank, (doc, score) in enumerate(results, start=1):
            noise_scores.append(score)
            snippet = doc.page_content.strip()[:100].replace("\n", " ")
            print(f"  Rank #{rank} | L2 Distance: {score:.4f} | Content: {snippet}...")

    min_target = min(target_scores) if target_scores else 0
    max_target = max(target_scores) if target_scores else 0
    min_noise = min(noise_scores) if noise_scores else 0
    max_noise = max(noise_scores) if noise_scores else 0

    print("\n" + "=" * 80)
    print("SUMMARY DISTANCE METRICS:")
    print("=" * 80)
    print(f"Target Queries L2 Distance Range : {min_target:.4f} to {max_target:.4f}")
    print(f"Noise Queries L2 Distance Range  : {min_noise:.4f} to {max_noise:.4f}")


if __name__ == "__main__":
    main()
