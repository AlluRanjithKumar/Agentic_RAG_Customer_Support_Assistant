import hashlib

from langchain_core.documents import Document
from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
)

from src.config import CHUNK_OVERLAP, CHUNK_SIZE


def create_chunk_id(
    document: Document,
) -> str:
    identity = "|".join(
        [
            document.metadata.get("source", ""),
            document.metadata.get("document_id", ""),
            document.metadata.get("record_id", ""),
            document.metadata.get("product_name", ""),
            document.page_content,
        ]
    )

    return hashlib.sha256(
        identity.encode("utf-8")
    ).hexdigest()


def normalize_documents(
    documents: list[Document],
) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.MARKDOWN,
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        add_start_index=True,
    )

    chunks = splitter.split_documents(documents)

    for chunk in chunks:
        chunk.metadata["chunk_id"] = create_chunk_id(chunk)

    return chunks
