from collections.abc import Sequence

from langchain_core.documents import Document
from langchain_core.tools import tool

from src.config import FINAL_RESULT_COUNT
from src.prompts import (
    NO_RELEVANT_INFORMATION_MESSAGE,
    SEARCH_ALL_KNOWLEDGE_DESCRIPTION,
    SEARCH_HISTORICAL_TICKETS_DESCRIPTION,
    SEARCH_PRODUCTS_AND_PLANS_DESCRIPTION,
    SEARCH_SUPPORT_KNOWLEDGE_DESCRIPTION,
)
from src.retrieval.retriever import (
    search_company_knowledge,
    search_knowledge_base,
    search_product_catalog,
    search_similar_tickets,
)


def format_documents(documents: Sequence[Document]) -> str:
    if not documents:
        return "No relevant information was found in the knowledge base."

    formatted_documents = []

    for rank, document in enumerate(documents, start=1):
        metadata = document.metadata

        source = metadata.get("source", "Unknown source")
        document_id = metadata.get("document_id", "Not available")
        record_id = metadata.get("record_id")
        record_type = metadata.get("record_type", "Unknown")
        effective_date = metadata.get("effective_date", "Not available")

        reference_parts = [
            f"Result: {rank}",
            f"Source: {source}",
            f"Document ID: {document_id}",
            f"Record type: {record_type}",
            f"Effective date: {effective_date}",
        ]

        if record_id:
            reference_parts.append(f"Record ID: {record_id}")

        reference_parts.append("Content:")
        reference_parts.append(document.page_content)

        formatted_documents.append("\n".join(reference_parts))

    return "\n\n---\n\n".join(formatted_documents)


@tool(description=SEARCH_SUPPORT_KNOWLEDGE_DESCRIPTION)
def search_support_knowledge(query: str) -> str:
    documents = search_company_knowledge(
        query=query,
        k=FINAL_RESULT_COUNT,
    )

    return format_documents(documents)


@tool(description=SEARCH_PRODUCTS_AND_PLANS_DESCRIPTION)
def search_products_and_plans(query: str) -> str:
    documents = search_product_catalog(
        query=query,
        k=FINAL_RESULT_COUNT,
    )

    return format_documents(documents)


@tool(description=SEARCH_HISTORICAL_TICKETS_DESCRIPTION)
def search_historical_tickets(query: str) -> str:
    documents = search_similar_tickets(
        query=query,
        k=FINAL_RESULT_COUNT,
    )

    return format_documents(documents)


@tool(description=SEARCH_ALL_KNOWLEDGE_DESCRIPTION)
def search_all_knowledge(query: str) -> str:
    documents = search_knowledge_base(
        query=query,
        k=FINAL_RESULT_COUNT,
    )

    return format_documents(documents)


RETRIEVAL_TOOLS = [
    search_support_knowledge,
    search_products_and_plans,
    search_historical_tickets,
    search_all_knowledge,
]
