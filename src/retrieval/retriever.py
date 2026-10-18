from functools import lru_cache

from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_classic.retrievers import EnsembleRetriever

from src.config import (
    BM25_RETRIEVER_WEIGHT,
    COMPANY_CATEGORIES,
    DENSE_RETRIEVER_WEIGHT,
    FINAL_RESULT_COUNT,
    PRODUCT_CATEGORIES,
    RETRIEVAL_CANDIDATE_COUNT,
    RRF_CONSTANT,
    TICKET_CATEGORIES,
)
from src.ingestion.indexer import get_vector_store
from src.retrieval.reranker import rerank_documents


@lru_cache(maxsize=1)
def get_all_documents() -> tuple[Document, ...]:
    stored = get_vector_store().get(
        include=[
            "documents",
            "metadatas",
        ]
    )

    return tuple(
        Document(
            page_content=content,
            metadata=metadata,
        )
        for content, metadata in zip(
            stored["documents"],
            stored["metadatas"],
            strict=True,
        )
    )


def create_category_filter(
    categories: tuple[str, ...] | None,
) -> dict | None:
    if not categories:
        return None

    if len(categories) == 1:
        return {
            "category": categories[0],
        }

    return {
        "category": {
            "$in": list(categories),
        }
    }


def filter_documents(
    categories: tuple[str, ...] | None,
) -> list[Document]:
    documents = get_all_documents()

    if not categories:
        return list(documents)

    return [
        document
        for document in documents
        if document.metadata.get("category") in categories
    ]


@lru_cache(maxsize=4)
def create_hybrid_retriever(
    categories: tuple[str, ...] | None = None,
    candidate_k: int = RETRIEVAL_CANDIDATE_COUNT,
) -> EnsembleRetriever:
    vector_store = get_vector_store()

    dense_retriever = vector_store.as_retriever(
        search_kwargs={
            "k": candidate_k,
            "filter": create_category_filter(categories),
        }
    )

    bm25_retriever = BM25Retriever.from_documents(
        filter_documents(categories)
    )

    bm25_retriever.k = candidate_k

    return EnsembleRetriever(
        retrievers=[
            dense_retriever,
            bm25_retriever,
        ],
        weights=[
            DENSE_RETRIEVER_WEIGHT,
            BM25_RETRIEVER_WEIGHT,
        ],
        c=RRF_CONSTANT,
        id_key="chunk_id",
    )


def search_knowledge_base(
    query: str,
    k: int = FINAL_RESULT_COUNT,
) -> list[Document]:
    retriever = create_hybrid_retriever()

    candidates = retriever.invoke(query)

    return rerank_documents(
        query=query,
        documents=candidates,
        top_n=k,
    )


def search_company_knowledge(
    query: str,
    k: int = FINAL_RESULT_COUNT,
) -> list[Document]:
    retriever = create_hybrid_retriever(
        categories=COMPANY_CATEGORIES,
    )

    candidates = retriever.invoke(query)

    return rerank_documents(
        query=query,
        documents=candidates,
        top_n=k,
    )


def search_similar_tickets(
    query: str,
    k: int = FINAL_RESULT_COUNT,
) -> list[Document]:
    retriever = create_hybrid_retriever(
        categories=TICKET_CATEGORIES,
    )

    candidates = retriever.invoke(query)

    return rerank_documents(
        query=query,
        documents=candidates,
        top_n=k,
    )


def search_product_catalog(
    query: str,
    k: int = FINAL_RESULT_COUNT,
) -> list[Document]:
    retriever = create_hybrid_retriever(
        categories=PRODUCT_CATEGORIES,
    )

    candidates = retriever.invoke(query)

    return rerank_documents(
        query=query,
        documents=candidates,
        top_n=k,
    )
