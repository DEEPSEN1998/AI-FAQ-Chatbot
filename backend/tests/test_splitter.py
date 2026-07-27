from app.rag.loader import load_documents
from app.rag.splitter import split_documents

documents = load_documents()
chunks = split_documents(documents)

print(f"Original Documents : {len(documents)}")
print(f"Total Chunks       : {len(chunks)}")

print("\n================ First Chunk ================\n")

print(chunks[0].page_content)

print("\nMetadata:")
print(chunks[0].metadata)