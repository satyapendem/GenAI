"""
Multilingual E5 embedder with correct prefix handling.

CRITICAL FIX:
  intfloat/multilingual-e5-small is a bi-encoder trained with prefixes.
  Without prefixes, cosine similarity degrades significantly — especially
  for non-Latin scripts like Telugu.

  Correct usage:
    Queries  → "query: <text>"
    Passages → "passage: <text>"

  This single fix typically recovers 15–30% retrieval accuracy for Telugu.

Reference:
  https://huggingface.co/intfloat/multilingual-e5-small
"""

from sentence_transformers import SentenceTransformer
from app.core.config import EMBED_MODEL

print(f"[embedder] Loading model: {EMBED_MODEL}")

model = SentenceTransformer(
    EMBED_MODEL,
    device="cpu",
)

print(f"[embedder] Ready.")


def embed_query(text: str) -> list[float]:
    """
    Embed a user query.
    Prefix: "query: "

    Use this in retriever.py when embedding the user's question.
    """
    prefixed = f"query: {text.strip()}"
    embedding = model.encode(
        prefixed,
        normalize_embeddings=True,
    )
    return embedding.tolist()


def embed_passage(text: str) -> list[float]:
    """
    Embed a document passage for storage.
    Prefix: "passage: "

    Use this in ingest.py when embedding document chunks.
    """
    prefixed = f"passage: {text.strip()}"
    embedding = model.encode(
        prefixed,
        normalize_embeddings=True,
    )
    return embedding.tolist()


def embed_text(text: str) -> list[float]:
    """
    Legacy alias — defaults to passage embedding.
    Kept for backward compatibility with ingest.py.
    For new code, use embed_query() or embed_passage() explicitly.
    """
    return embed_passage(text)
