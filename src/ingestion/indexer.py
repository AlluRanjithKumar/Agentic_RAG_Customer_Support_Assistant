from functools import lru_cache

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from src.config import (
    CHROMA_COLLECTION_NAME,
    CHROMA_DISTANCE_FUNCTION,
    EMBEDDING_DEVICE,
    EMBEDDING_MODEL_NAME,
    NORMALIZE_EMBEDDINGS,
    VECTOR_STORE_DIR,
)


@lru_cache(maxsize=1)
def get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={
            "device": EMBEDDING_DEVICE,
        },
        encode_kwargs={
            "normalize_embeddings": NORMALIZE_EMBEDDINGS,
        },
    )


@lru_cache(maxsize=1)
def get_vector_store() -> Chroma:
    return Chroma(
        collection_name=CHROMA_COLLECTION_NAME,
        embedding_function=get_embeddings(),
        persist_directory=str(VECTOR_STORE_DIR),
        collection_metadata={
            "hnsw:space": CHROMA_DISTANCE_FUNCTION,
        },
    )


def rebuild_vector_store(
    documents: list[Document],
) -> Chroma:
    existing_store = get_vector_store()
    existing_store.delete_collection()

    return Chroma.from_documents(
        documents=documents,
        ids=[
            document.metadata["chunk_id"]
            for document in documents
        ],
        embedding=get_embeddings(),
        collection_name=CHROMA_COLLECTION_NAME,
        persist_directory=str(VECTOR_STORE_DIR),
        collection_metadata={
            "hnsw:space": CHROMA_DISTANCE_FUNCTION,
        },
    )
