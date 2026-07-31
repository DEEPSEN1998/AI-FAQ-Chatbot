import hashlib
import re
from pathlib import Path
from typing import List, Tuple

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class SectionAwareTextSplitter:
    """
    Semantic & Section-Aware Document Splitter.

    Splits documents along logical section headings (e.g., ABOUT, SERVICES, TEAM, PORTFOLIO, CONTACT,
    or Markdown headers #, ##) and enriches each resulting chunk with metadata:
    - source_file
    - page_number
    - section_name
    - chunk_id
    """

    KNOWN_SECTION_HEADINGS = [
        "ABOUT",
        "SERVICES",
        "TEAM",
        "PORTFOLIO",
        "CONTACT",
        "LEADERSHIP",
        "PROJECTS",
        "TECHNOLOGIES",
        "PRICING",
        "OVERVIEW",
        "COMPANY PROFILE",
        "DEVELOPERS",
    ]

    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 80):
        """
        Initialize SectionAwareTextSplitter.

        Args:
            chunk_size (int): Max character length per chunk fallback.
            chunk_overlap (int): Overlap character count.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self._fallback_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        # Regex to capture section headers
        self._heading_pattern = re.compile(
            r"^(?:\#+\s*|===+\s*|---+\s*)?([A-Z0-9\s]{3,40})(?:\:|\s*\n|$)",
            re.MULTILINE,
        )

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into semantic section-aware chunks with metadata.

        Args:
            documents (List[Document]): Raw loaded documents.

        Returns:
            List[Document]: Metadata-enriched document chunks.
        """
        enriched_chunks: List[Document] = []

        for doc in documents:
            raw_source = doc.metadata.get("source", doc.metadata.get("file_name", "Unknown"))
            source_file = Path(raw_source).name
            page_number = int(doc.metadata.get("page", doc.metadata.get("page_number", 1)))

            # 1. Split content by logical section headings
            sections = self._split_by_sections(doc.page_content)

            # 2. Sub-chunk each section cleanly without crossing section boundaries
            for section_title, section_text in sections:
                if not section_text.strip():
                    continue

                sub_chunks = self._fallback_splitter.create_documents(
                    texts=[section_text],
                    metadatas=[doc.metadata],
                )

                for idx, sub_chunk in enumerate(sub_chunks):
                    # Generate unique, deterministic chunk ID
                    chunk_hash = hashlib.md5(
                        f"{source_file}_{page_number}_{section_title}_{idx}_{sub_chunk.page_content[:30]}".encode()
                    ).hexdigest()[:10]

                    chunk_id = f"chunk_{source_file}_p{page_number}_{chunk_hash}"

                    enriched_metadata = dict(sub_chunk.metadata)
                    enriched_metadata.update({
                        "source_file": source_file,
                        "source": source_file,
                        "page_number": page_number,
                        "page": page_number,
                        "section_name": section_title,
                        "chunk_id": chunk_id,
                        "id": chunk_id,
                    })

                    enriched_chunks.append(
                        Document(
                            page_content=sub_chunk.page_content.strip(),
                            metadata=enriched_metadata,
                        )
                    )

        return enriched_chunks

    def _split_by_sections(self, content: str) -> List[Tuple[str, str]]:
        """
        Extract section titles and associated text blocks from document content.
        """
        lines = content.splitlines()
        sections: List[Tuple[str, str]] = []
        current_title = "General Context"
        current_lines: List[str] = []

        for line in lines:
            stripped = line.strip()
            heading_match = self._heading_pattern.match(stripped)

            if heading_match and (
                stripped.isupper()
                or stripped.startswith("#")
                or any(keyword in stripped.upper() for keyword in self.KNOWN_SECTION_HEADINGS)
            ):
                if current_lines:
                    sections.append((current_title, "\n".join(current_lines)))
                    current_lines = []
                current_title = heading_match.group(1).strip()
            else:
                current_lines.append(line)

        if current_lines:
            sections.append((current_title, "\n".join(current_lines)))

        return sections


# Module instance for backward compatibility
_default_splitter = SectionAwareTextSplitter()


def split_documents(documents: List[Document]) -> List[Document]:
    """
    Functional interface for section-aware document splitting.
    """
    return _default_splitter.split_documents(documents)