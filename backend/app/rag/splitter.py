from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
    separators=["\n\n", "\n", ".", " ", ""],
)


def split_documents(documents):
    """
    Split documents into smaller chunks.
    """
    return text_splitter.split_documents(documents)