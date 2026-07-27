from app.rag.embeddings import get_embeddings

embeddings = get_embeddings()

vector = embeddings.embed_query("Hello, this is my first embedding.")

print(f"Vector Dimension: {len(vector)}")
print(vector[:10])