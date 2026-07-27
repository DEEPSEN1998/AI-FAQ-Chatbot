from app.rag.retriever import retrieve_documents

results = retrieve_documents(
    "Who is the founder of K8ight Web Services?"
)

print(f"Found {len(results)} documents\n")

for i, doc in enumerate(results, start=1):
    print("=" * 60)
    print(f"Result {i}")
    print("=" * 60)
    print(doc.page_content[:500])
    print()