from app.config import KNOWLEDGE_DIR
from app.rag.loader import load_documents

print("Knowledge Directory:", KNOWLEDGE_DIR)
print("Exists:", KNOWLEDGE_DIR.exists())

documents = load_documents()

print(f"Total Documents: {len(documents)}")

for i, doc in enumerate(documents[:3], start=1):
    print(f"\n----- Document {i} -----")
    print("Source:", doc.metadata.get("source"))
    print("Characters:", len(doc.page_content))
    print(doc.page_content[:300])