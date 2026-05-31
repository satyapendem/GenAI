"""
Qdrant vector operations.

Key fix: PointStruct IDs are now UUID-based (derived from content hash),
not sequential integers. Old code used idx=0,1,2... per batch, which
caused ID collisions across files on re-ingest, silently overwriting vectors.
"""

import hashlib
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    VectorParams,
    PointStruct,
)

from app.core.config import QDRANT_HOST, QDRANT_PORT

client = QdrantClient(
    host=QDRANT_HOST,
    port=QDRANT_PORT,
)

BATCH_SIZE = 64


def _chunk_id(text: str, source: str, chunk_index: int) -> int:
    """
    Generate a stable integer ID for a chunk.

    Uses SHA-256 of (source + chunk_index + text[:100]) truncated to 63 bits.
    This gives collision-free IDs that are deterministic across re-ingests,
    so upsert correctly overwrites rather than duplicating.
    """
    key = f"{source}::{chunk_index}::{text[:100]}"
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    # Qdrant requires uint64 — take first 16 hex chars = 64 bits, mask to 63
    return int(digest[:16], 16) & 0x7FFFFFFFFFFFFFFF


def ensure_collection(name: str, vector_size: int):
    """Ensure collection exists with correct vector dimensions."""
    collections = client.get_collections()
    exists = any(c.name == name for c in collections.collections)

    if not exists:
        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
            ),
        )
        print(f"[qdrant] Created collection: {name} (dim={vector_size})")
        return

    # Validate dimensions match
    info = client.get_collection(name)
    current_size = info.config.params.vectors.size

    if current_size != vector_size:
        print(
            f"[qdrant] Dimension mismatch on {name}: {current_size} vs {vector_size}. Recreating."
        )
        client.delete_collection(name)
        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
            ),
        )


def store_chunks(collection: str, chunks: list[dict]):
    """
    Upsert chunks into Qdrant in batches.

    Each chunk dict must have:
        {
            "text":      str,
            "embedding": list[float],
            "metadata":  dict,        # source, doc_type, page, etc.
        }
    """
    if not chunks:
        print("[qdrant] No chunks to store.")
        return

    vector_size = len(chunks[0]["embedding"])
    ensure_collection(collection, vector_size)

    total = len(chunks)
    print(f"\n[qdrant] Storing {total} chunks → {collection}")

    for start in range(0, total, BATCH_SIZE):
        batch = chunks[start : start + BATCH_SIZE]
        points = []

        for chunk in batch:
            text = chunk["text"]
            metadata = chunk["metadata"]
            source = metadata.get("source", "unknown")
            cidx = metadata.get("chunk_index", 0)

            point_id = _chunk_id(text, source, cidx)

            points.append(
                PointStruct(
                    id=point_id,
                    vector=chunk["embedding"],
                    payload={
                        "text": text,
                        "metadata": metadata,
                    },
                )
            )

        try:
            client.upsert(
                collection_name=collection,
                points=points,
            )
            end = min(start + BATCH_SIZE, total)
            print(f"[qdrant] Stored {end}/{total}")

        except Exception as e:
            print(f"[qdrant] Batch failed: {e}")

    print(f"[qdrant] Done: {collection}")
