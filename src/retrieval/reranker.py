from collections.abc import Sequence
from functools import lru_cache

from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain_core.documents import Document
from langchain_classic.retrievers.document_compressors import (
    CrossEncoderReranker,
)

from src.config import FINAL_RESULT_COUNT, RERANKER_MODEL_NAME


@lru_cache(maxsize=1)
def get_cross_encoder() -> HuggingFaceCrossEncoder:
    return HuggingFaceCrossEncoder(
        model_name=RERANKER_MODEL_NAME,
    )


def rerank_documents(
    query: str,
    documents: Sequence[Document],
    top_n: int = FINAL_RESULT_COUNT,
) -> list[Document]:
    if not documents:
        return []

    reranker = CrossEncoderReranker(
        model=get_cross_encoder(),
        top_n=min(top_n, len(documents)),
    )

    return list(
        reranker.compress_documents(
            documents=documents,
            query=query,
        )
    )
