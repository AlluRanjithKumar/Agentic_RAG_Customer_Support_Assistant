from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
KNOWLEDGE_BASE_DIR = DATA_DIR / "Knowledge_Base"
EVALUATION_DIR = DATA_DIR / "evaluation"
VECTOR_STORE_DIR = PROJECT_ROOT / "vector_store"
CHECKPOINT_DATABASE_PATH = PROJECT_ROOT / "checkpoints.sqlite3"

# Model configuration
GOOGLE_API_KEY_ENV = "GOOGLE_API_KEY"
LLM_MODEL_NAME = "gemini-3.5-flash-lite"
LLM_TEMPERATURE = 0
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DEVICE = "cpu"
NORMALIZE_EMBEDDINGS = True
RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# Ingestion configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

# Vector-store configuration
CHROMA_COLLECTION_NAME = "ranjiths_tech_support"
CHROMA_DISTANCE_FUNCTION = "cosine"

# Retrieval configuration
COMPANY_CATEGORIES = ("policies", "troubleshooting", "faq")
PRODUCT_CATEGORIES = ("products",)
TICKET_CATEGORIES = ("tickets",)
DENSE_RETRIEVER_WEIGHT = 0.7
BM25_RETRIEVER_WEIGHT = 0.3
RETRIEVAL_CANDIDATE_COUNT = 8
FINAL_RESULT_COUNT = 3
RRF_CONSTANT = 60

# Interface configuration
APP_NAME = "Ranjith's Tech Support"
PAGE_TITLE = "Ranjith's Tech Support Agent"
PAGE_ICON = "🛠️"
PAGE_LAYOUT = "centered"
THREAD_ID_PREFIX = "chat"
THREAD_ID_LENGTH = 10
DEFAULT_CLI_THREAD_ID = "default-conversation"
CHECKPOINT_LIST_LIMIT = 500
AGENT_NODE_NAME = "support_agent"

# Human-review rules
SAFETY_TERMS = (
    "swollen",
    "swelling",
    "smoke",
    "smoking",
    "hissing",
    "leaking",
    "battery leak",
    "unusually hot",
    "overheating",
    "burning smell",
    "electric shock",
    "enclosure separation",
)

AUTHORIZATION_TERMS = (
    "approve",
    "authorize",
    "issue",
    "process",
    "create",
    "send",
)

CONTROLLED_ACTION_TERMS = (
    "refund",
    "replacement",
    "shipping label",
    "warranty exception",
)

INSUFFICIENT_EVIDENCE_TERMS = (
    "cannot confirm",
    "cannot determine",
    "insufficient information",
    "insufficient evidence",
    "knowledge base does not contain",
    "conflicting information",
)
