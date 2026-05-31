"""
Central configuration for APGovAI.

All values are read from environment variables with sensible defaults.
Set overrides in your .env file.
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ── LLM ──────────────────────────────────────────────────────────────────────

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct-q4_K_M")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")


# ── Embedding ─────────────────────────────────────────────────────────────────

EMBED_MODEL = os.getenv("EMBED_MODEL", "intfloat/multilingual-e5-small")
RERANK_MODEL = os.getenv("RERANK_MODEL", "BAAI/bge-reranker-v2-m3")


# ── Paths ─────────────────────────────────────────────────────────────────────

DATA_ROOT = os.getenv("DATA_ROOT", "./training_data")
PROCESSED_ROOT = os.getenv("PROCESSED_ROOT", "./processed")


# ── Qdrant ────────────────────────────────────────────────────────────────────

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))


# ── Retrieval ─────────────────────────────────────────────────────────────────

TOP_K = int(os.getenv("TOP_K", "8"))
RERANK_TOP = int(os.getenv("RERANK_TOP", "3"))

# Read from .env — was hardcoded to 800, .env had 1500 → mismatch fixed
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1200"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))


POSTGRES_HOST = os.getenv(
    "POSTGRES_HOST",
    "localhost",
)

POSTGRES_PORT = int(
    os.getenv(
        "POSTGRES_PORT",
        "5432",
    )
)

POSTGRES_DB = os.getenv(
    "POSTGRES_DB",
    "apgovai",
)

POSTGRES_USER = os.getenv(
    "POSTGRES_USER",
    "apgovai",
)

POSTGRES_PASSWORD = os.getenv(
    "POSTGRES_PASSWORD",
    "apgovai123",
)


JWT_SECRET = os.getenv(
    "JWT_SECRET",
)

JWT_ALGORITHM = os.getenv(
    "JWT_ALGORITHM",
    "HS256",
)

JWT_EXPIRE_MINUTES = int(
    os.getenv(
        "JWT_EXPIRE_MINUTES",
        "1440",
    )
)

# ── Collections ───────────────────────────────────────────────────────────────

COLLECTIONS = {
    "gos": {
        "data": f"{DATA_ROOT}/gos",
        "processed": f"{PROCESSED_ROOT}/gos",
        "collection": "gos",
        "doc_type": "government_order",
    },
    "budgets": {
        "data": f"{DATA_ROOT}/budgets",
        "processed": f"{PROCESSED_ROOT}/budgets",
        "collection": "budgets",
        "doc_type": "budget",
    },
    "reports": {
        "data": f"{DATA_ROOT}/reports",
        "processed": f"{PROCESSED_ROOT}/reports",
        "collection": "reports",
        "doc_type": "report",
    },
    "datasets": {
        "data": f"{DATA_ROOT}/datasets",
        "processed": f"{PROCESSED_ROOT}/datasets",
        "collection": "datasets",
        "doc_type": "dataset",
    },
}
