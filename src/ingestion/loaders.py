import re
from pathlib import Path

from langchain_community.document_loaders import (
    DirectoryLoader,
    JSONLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)
from langchain_core.documents import Document

from src.config import KNOWLEDGE_BASE_DIR


DOCUMENT_ID_PATTERN = re.compile(
    r"Document ID:\*{0,2}\s*([A-Z0-9.-]+)",
    re.IGNORECASE,
)

EFFECTIVE_DATE_PATTERN = re.compile(
    r"Effective date:\*{0,2}\s*(\d{4}-\d{2}-\d{2})",
    re.IGNORECASE,
)


def enrich_text_documents(
    documents: list[Document],
) -> list[Document]:
    """
    Add portable and domain-specific metadata to Markdown/TXT files.
    """

    for document in documents:
        source_path = Path(document.metadata["source"])
        relative_path = source_path.relative_to(
            KNOWLEDGE_BASE_DIR
        )

        document.metadata.update(
            {
                "source": relative_path.as_posix(),
                "file_name": source_path.name,
                "file_type": source_path.suffix.removeprefix("."),
                "category": source_path.parent.name,
                "record_type": "text",
            }
        )

        document_id = DOCUMENT_ID_PATTERN.search(
            document.page_content
        )

        if document_id:
            document.metadata["document_id"] = (
                document_id.group(1)
            )

        effective_date = EFFECTIVE_DATE_PATTERN.search(
            document.page_content
        )

        if effective_date:
            document.metadata["effective_date"] = (
                effective_date.group(1)
            )

    return documents


def product_metadata(
    record: dict,
    metadata: dict,
) -> dict:
    metadata.update(
        {
            "category": "products",
            "record_type": "product",
            "document_id": record["document_id"],
            "effective_date": record["effective_date"],
            "product_name": record["name"],
            "product_family": record["family"],
            "sku": record["sku"],
        }
    )

    return metadata


def plan_metadata(
    record: dict,
    metadata: dict,
) -> dict:
    metadata.update(
        {
            "category": "products",
            "record_type": "plan",
            "document_id": record["document_id"],
            "effective_date": record["effective_date"],
            "plan_name": record["name"],
        }
    )

    return metadata


def faq_metadata(
    record: dict,
    metadata: dict,
) -> dict:
    metadata.update(
        {
            "category": "faq",
            "record_type": "faq",
            "document_id": record["document_id"],
            "effective_date": record["effective_date"],
            "record_id": record["id"],
            "tags": ",".join(record.get("tags", [])),
        }
    )

    return metadata


def ticket_metadata(
    record: dict,
    metadata: dict,
) -> dict:
    metadata.update(
        {
            "category": "tickets",
            "record_type": "historical_ticket",
            "document_id": record["ticket_id"],
            "product_name": record["product"],
            "ticket_category": record["category"],
            "status": record["status"],
        }
    )

    return metadata


def load_markdown_documents() -> list[Document]:
    loader = DirectoryLoader(
        path=str(KNOWLEDGE_BASE_DIR),
        glob="**/*.md",
        loader_cls=UnstructuredMarkdownLoader,
        loader_kwargs={
            "mode": "single",
        },
        recursive=True,
    )

    return enrich_text_documents(loader.load())


def load_text_documents() -> list[Document]:
    loader = DirectoryLoader(
        path=str(KNOWLEDGE_BASE_DIR),
        glob="**/*.txt",
        loader_cls=TextLoader,
        loader_kwargs={
            "encoding": "utf-8",
        },
        recursive=True,
    )

    return enrich_text_documents(loader.load())


def load_product_documents() -> list[Document]:
    file_path = (
        KNOWLEDGE_BASE_DIR
        / "products"
        / "product_catalog.json"
    )

    product_loader = JSONLoader(
        file_path=file_path,
        jq_schema="""
        . as $root
        | $root.products[]
        | . + {
            "document_id": $root.document_id,
            "effective_date": $root.effective_date
        }
        """,
        text_content=False,
        metadata_func=product_metadata,
    )

    plan_loader = JSONLoader(
        file_path=file_path,
        jq_schema="""
        . as $root
        | $root.plans[]
        | . + {
            "document_id": $root.document_id,
            "effective_date": $root.effective_date
        }
        """,
        text_content=False,
        metadata_func=plan_metadata,
    )

    return (
        product_loader.load()
        + plan_loader.load()
    )


def load_faq_documents() -> list[Document]:
    file_path = (
        KNOWLEDGE_BASE_DIR
        / "faq"
        / "customer_faq.json"
    )

    loader = JSONLoader(
        file_path=file_path,
        jq_schema="""
        . as $root
        | $root.items[]
        | . + {
            "document_id": $root.document_id,
            "effective_date": $root.effective_date
        }
        """,
        text_content=False,
        metadata_func=faq_metadata,
    )

    return loader.load()


def load_ticket_documents() -> list[Document]:
    file_path = (
        KNOWLEDGE_BASE_DIR
        / "tickets"
        / "historical_tickets.jsonl"
    )

    loader = JSONLoader(
        file_path=file_path,
        jq_schema=".",
        text_content=False,
        json_lines=True,
        metadata_func=ticket_metadata,
    )

    return loader.load()


def load_knowledge_base() -> list[Document]:
    return [
        *load_markdown_documents(),
        *load_text_documents(),
        *load_product_documents(),
        *load_faq_documents(),
        *load_ticket_documents(),
    ]