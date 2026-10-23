# Ranjith's Tech Agentic RAG Support Assistant

An AI-powered customer-support assistant built with LangChain, LangGraph, Gemini, Chroma, BM25, and cross-encoder reranking. The application answers questions about Ranjith's Tech products, policies, troubleshooting procedures, FAQs, protection plans, and historical support cases.

The project uses a single tool-calling agent, persistent conversation threads, source-grounded responses, and human approval for safety-critical or authorization-sensitive answers.

## Features

- Loads Markdown, text, JSON, and JSONL knowledge-base files.
- Preserves domain metadata such as document ID, category, effective date, product name, and record type.
- Splits documents into overlapping chunks with stable SHA-256 chunk IDs.
- Stores embeddings, text, and metadata in a persistent Chroma vector database.
- Combines dense semantic retrieval with BM25 lexical retrieval.
- Fuses rankings with Reciprocal Rank Fusion and deduplicates by `chunk_id`.
- Reranks candidates with a cross-encoder before returning the final evidence.
- Exposes retrieval pipelines as LangChain tools.
- Uses Gemini 3.5 Flash-Lite to select one or more tools and synthesize a grounded answer.
- Persists conversations and graph execution state with SQLite checkpoints.
- Supports human-in-the-loop approval, editing, and rejection using LangGraph interrupts.
- Streams Gemini response chunks through LangGraph into the Streamlit interface.
- Keeps different conversations isolated through unique LangGraph thread IDs.

## Setup

### 1. Create and activate a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 3. Configure Gemini

Copy the example environment file:

```powershell
Copy-Item .env.example .env
```

Add your own Google API key to `.env`:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

The real `.env` file is ignored by Git and must not be committed.

### 4. Build the vector store

```powershell
python ingest.py
```

This command loads the knowledge base, adds metadata, creates chunks and
embeddings, and persists the Chroma collection in `vector_store/`.

### 5. Start the application

```powershell
python -m streamlit run streamlit_app.py
```

## Workflows

### Ingestion workflow

```text
Files -> loaders -> LangChain Documents -> metadata enrichment
      -> normalization -> chunking -> embeddings -> Chroma
```

Run ingestion when knowledge-base files are added, changed, or removed. Ingestion is not performed for every customer query.

### Query workflow

```text
Question -> agent selects tool -> metadata-filtered hybrid search
         -> RRF -> deduplication -> cross-encoder reranking
         -> agent generates sourced response -> review decision
         -> normal completion or human-review interrupt
```

The Streamlit interface uses LangGraph's `stream_mode="messages"` to display
Gemini output progressively. Retrieval results, raw tool calls, and internal
metadata are not displayed as customer-facing messages.

### Retrieval configuration

The current defaults are centralized in `src/config.py`:

| Setting | Value |
|---|---:|
| Chunk size | 1,000 characters |
| Chunk overlap | 150 characters |
| Dense candidate count | 8 |
| BM25 candidate count | 8 |
| Dense/BM25 weights | 0.7 / 0.3 |
| RRF constant | 60 |
| Final reranked results | 3 |

These values are initial design settings. The evaluation questions in
`data/evaluation/questions.json` can be used to compare chunk sizes and
retrieval configurations without adding evaluation data to the knowledge base.

## Retrieval Tools

| Tool | Purpose |
|---|---|
| `search_support_knowledge` | Policies, troubleshooting guides, safety procedures, and FAQs |
| `search_products_and_plans` | Product specifications, comparisons, compatibility, and protection plans |
| `search_historical_tickets` | Similar historical incidents and recorded resolutions |
| `search_all_knowledge` | Multi-topic, ambiguous, or fallback searches across the complete knowledge base |

Historical tickets are treated as examples, not as official policy. Official policy and troubleshooting documents have higher authority.

## Human-in-the-Loop

The graph evaluates every completed draft. It interrupts the workflow for
human review when it detects:

- safety-critical symptoms such as battery swelling, smoke, leaking, hissing, unusual heat, or electric shock;
- requests to authorize controlled actions such as refunds, replacements, shipping labels, or warranty exceptions;
- insufficient or conflicting evidence.

The reviewer can:

- **Approve** the generated draft;
- **Edit** and replace the draft;
- **Reject** the automated response and escalate the request.

LangGraph's `interrupt()` pauses execution, while the SQLite checkpointer saves the complete state. The same conversation is resumed with `Command(resume=...)`.

The review decision occurs after the draft has been generated. In the current
Streamlit implementation, that draft is streamed in the internal support
interface before the review panel appears. A customer-facing production system
should buffer review-sensitive drafts until a reviewer approves them.

## Knowledge Base

```text
data/
├── Knowledge_Base/
│   ├── faq/
│   │   └── customer_faq.json
│   ├── policies/
│   │   ├── returns_refunds.txt
│   │   ├── shipping_replacement.md
│   │   └── warranty_policy.md
│   ├── products/
│   │   └── product_catalog.json
│   ├── tickets/
│   │   └── historical_tickets.jsonl
│   └── troubleshooting/
│       ├── audio_devices.md
│       ├── connectivity_guide.md
│       └── laptop_battery.md
└── evaluation/
    └── questions.json
```

The knowledge base is fictional and was created for this student project. The company name is Ranjith's Tech.

## Project Structure

```text
Agentic_AI_Project/
├── streamlit_app.py             # Streamlit chat interface
├── ingest.py                    # Offline ingestion entry point
├── requirements.txt
├── data/
├── src/
│   ├── config.py                # Paths and model configuration
│   ├── prompts.py               # Agent prompts and tool descriptions
│   ├── agents/
│   │   └── tools.py             # LangChain retrieval tools
│   ├── graph/
│   │   ├── state.py             # LangGraph state definition
│   │   └── workflow.py          # Agent, routing, checkpoints, and HITL
│   ├── ingestion/
│   │   ├── loaders.py           # Multi-format document loading
│   │   ├── normalizer.py        # Chunking and stable chunk IDs
│   │   └── indexer.py           # Embeddings and Chroma indexing
│   └── retrieval/
│       ├── retriever.py         # Dense + BM25 hybrid retrieval
│       └── reranker.py          # Cross-encoder reranking
└── vector_store/                # Generated Chroma database; Git ignored
```

## Technology Stack

- Python 3.12
- LangChain and LangGraph
- Google Gemini 3.5 Flash-Lite
- Hugging Face Sentence Transformers
- `sentence-transformers/all-MiniLM-L6-v2` for dense embeddings
- `cross-encoder/ms-marco-MiniLM-L-6-v2` for reranking
- Chroma for persistent vector storage
- BM25 through `rank-bm25`
- SQLite for LangGraph checkpoints
- Streamlit for the web interface

## Generated Local Data

The following runtime artifacts are intentionally excluded from Git:

- `.env` -- private API credentials;
- `venv/` -- the local Python environment;
- `vector_store/` -- the generated Chroma database;
- `checkpoints.sqlite3*` -- local LangGraph conversations and checkpoints;
- `__pycache__/` -- generated Python bytecode.

Another user should create their own `.env`, run `python ingest.py`, and then
start Streamlit. Their local conversation database will begin independently.

