from src.ingestion.indexer import rebuild_vector_store
from src.ingestion.loaders import load_knowledge_base
from src.ingestion.normalizer import normalize_documents


def run_ingestion() -> None:
    documents = load_knowledge_base()
    chunks = normalize_documents(documents)
    rebuild_vector_store(chunks)


if __name__ == "__main__":
    run_ingestion()