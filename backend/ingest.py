"""Command-line entry point for indexing files from knowledge/ into ChromaDB."""

import argparse

from backend.app.rag import index_knowledge


def main() -> None:
    """Index the knowledge base; --reset removes stale chunks first."""
    parser = argparse.ArgumentParser(description="Index knowledge files into ChromaDB using NVIDIA NIM embeddings.")
    parser.add_argument("--reset", action="store_true", help="Remove old chunks before indexing.")
    args = parser.parse_args()
    count = index_knowledge(reset=args.reset)
    print(f"Indexed {count} chunks into ChromaDB.")


if __name__ == "__main__":
    main()
