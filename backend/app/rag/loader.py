from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
)

from app.config import KNOWLEDGE_DIR


def load_documents():
    """
    Load all PDF, DOCX and TXT documents
    from the knowledge directory.
    """

    documents = []

    # PDF
    pdf_dir = KNOWLEDGE_DIR / "pdf"
    if pdf_dir.exists():
        for file in pdf_dir.glob("*.pdf"):
            loader = PyPDFLoader(str(file))
            documents.extend(loader.load())

    # DOCX
    docx_dir = KNOWLEDGE_DIR / "docx"
    if docx_dir.exists():
        for file in docx_dir.glob("*.docx"):
            loader = Docx2txtLoader(str(file))
            documents.extend(loader.load())

    # TXT
    txt_dir = KNOWLEDGE_DIR / "txt"
    if txt_dir.exists():
        for file in txt_dir.glob("*.txt"):
            loader = TextLoader(str(file), encoding="utf-8")
            documents.extend(loader.load())

    return documents