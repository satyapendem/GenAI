"""
Hybrid semantic + lexical retrieval for APGovAI.

Key fixes over original:
  1. Uses embed_query() — correct "query: " prefix for E5 model.
     Old code used embed_text() which applied "passage: " prefix to queries,
     causing asymmetric embedding space → poor cosine similarity for Telugu.

  2. MIN_SCORE lowered to 0.35.
     Telugu multilingual embeddings typically score 0.35–0.55.
     Old threshold of 0.55 silently dropped all Telugu results.

  3. Telugu-aware lexical tokenizer.
     Old re.findall(r'\w+') misses Telugu Unicode block U+0C00–U+0C7F
     in some Python builds. Explicit Unicode range added.

  4. source_count limit raised to 4 for budget documents.
     Budget PDFs need consecutive chunks to preserve table context.

  5. Metadata preserved fully in results for citation rendering.
"""

import re
from collections import defaultdict

from app.embedding.embedder import embed_query  # ← FIXED: was embed_text
from app.vector.qdrant_client import client
from app.core.config import COLLECTIONS, TOP_K

# ── Thresholds ────────────────────────────────────────────────────────────────

# Lowered from 0.55 → Telugu embeddings typically score 0.35–0.55
MIN_SCORE = 0.35

# Max chars per chunk sent to LLM context
MAX_TEXT_LENGTH = 2000

# How many chunks allowed per source document
MAX_CHUNKS_PER_SOURCE_DEFAULT = 3
MAX_CHUNKS_PER_SOURCE_BUDGET = 5  # budget docs need more consecutive context


# ── Telugu-aware tokenizer ────────────────────────────────────────────────────

# Matches: English words, Telugu syllables (U+0C00–U+0C7F), digits
_TOKEN_RE = re.compile(
    r"[\u0C00-\u0C7F]+|[a-zA-Z]+|\d+",
    re.UNICODE,
)


def tokenize(text: str) -> set[str]:
    """
    Extract tokens from Telugu+English mixed text.

    Old code used r'\w+' which in some Python builds does NOT match
    Telugu codepoints — causing 0.0 lexical score for all Telugu queries.
    """
    return set(_TOKEN_RE.findall(text.lower()))


# ── Chunk cleaner ─────────────────────────────────────────────────────────────


def clean_chunk(text: str) -> str:
    """Remove OCR noise and excessive whitespace."""
    if not text:
        return ""

    text = " ".join(text.split())

    for pat in ["====", "____", "-----", "||||", "***"]:
        text = text.replace(pat, " ")

    return text.strip()


# ── Lexical overlap ───────────────────────────────────────────────────────────


def lexical_overlap_score(query: str, text: str) -> float:
    """
    Token overlap ratio between query and chunk.
    Telugu-safe: uses explicit Unicode range tokenizer.
    """
    q_tokens = tokenize(query)
    t_tokens = tokenize(text)

    if not q_tokens:
        return 0.0

    overlap = q_tokens & t_tokens
    return len(overlap) / len(q_tokens)


# ── Main retrieval ────────────────────────────────────────────────────────────


def retrieve_documents(query: str) -> list[dict]:
    """
    Hybrid semantic + lexical retrieval across all Qdrant collections.

    Returns ranked, deduplicated list of chunk dicts:
        {
            "score":          float,   # hybrid final score
            "semantic_score": float,
            "lexical_score":  float,
            "text":           str,
            "metadata":       dict,    # source, doc_type, page, go_number, etc.
        }
    """

    # ── Step 1: embed query with correct prefix ──────────────────────────────
    query_vector = embed_query(query)  # "query: <text>" prefix

    raw_results = []

    # ── Step 2: search all collections ──────────────────────────────────────
    for col_name, cfg in COLLECTIONS.items():
        try:
            response = client.query_points(
                collection_name=cfg["collection"],
                query=query_vector,
                limit=TOP_K * 2,  # fetch more, filter after
            )

            for r in response.points:
                semantic_score = r.score
                payload = r.payload
                text = payload.get("text", "")
                metadata = payload.get("metadata", {})

                text = clean_chunk(text)

                if not text:
                    continue

                text = text[:MAX_TEXT_LENGTH]

                lexical_score = lexical_overlap_score(query, text)

                # Hybrid: semantic dominates, lexical boosts exact-term matches
                final_score = (semantic_score * 0.80) + (lexical_score * 0.20)

                if final_score < MIN_SCORE:
                    continue

                raw_results.append(
                    {
                        "score": final_score,
                        "semantic_score": semantic_score,
                        "lexical_score": lexical_score,
                        "text": text,
                        "metadata": metadata,
                        "collection": col_name,
                    }
                )

        except Exception as e:
            print(f"[retriever] Collection {col_name} error: {e}")

    # ── Step 3: sort by score ────────────────────────────────────────────────
    raw_results.sort(key=lambda x: x["score"], reverse=True)

    # ── Step 4: deduplicate ──────────────────────────────────────────────────
    unique = []
    seen = set()

    for r in raw_results:
        key = r["metadata"].get("source", "") + r["text"][:150]
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)

    # ── Step 5: balance per-source (budget docs get more) ───────────────────
    balanced = []
    source_count = defaultdict(int)

    for r in unique:
        source = r["metadata"].get("source", "unknown")
        col = r.get("collection", "")
        limit = (
            MAX_CHUNKS_PER_SOURCE_BUDGET
            if col == "budgets"
            else MAX_CHUNKS_PER_SOURCE_DEFAULT
        )

        if source_count[source] >= limit:
            continue

        source_count[source] += 1
        balanced.append(r)

    final = balanced[:TOP_K]

    # ── Debug log ────────────────────────────────────────────────────────────
    print()
    print("=" * 50)
    print(f"[retriever] Query: {query[:80]}")
    print(f"[retriever] Raw={len(raw_results)} Unique={len(unique)} Final={len(final)}")
    print()

    for i, r in enumerate(final, 1):
        print(
            f"  [{i}] score={r['score']:.3f} "
            f"sem={r['semantic_score']:.3f} "
            f"lex={r['lexical_score']:.3f} "
            f"src={r['metadata'].get('source','?')}"
        )

    print("=" * 50)

    return final
