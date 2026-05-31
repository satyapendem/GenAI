"""
Unicode-safe semantic chunker for Telugu + English government documents.

Problems with the old chunker:
  1. Character-level slicing breaks Telugu grapheme clusters.
     Telugu syllables span 3–6 codepoints. Cutting at char position 800
     can split a syllable mid-character, producing garbage like "బడ్జె" → "బడ్" + "జె".
  2. No sentence-awareness — splits mid-sentence.
  3. Metadata not attached to chunks.
  4. CHUNK_SIZE mismatch between .env (1500) and hardcoded config (800).

Fix strategy:
  1. Split on sentence boundaries first (Telugu "।" and ". " and "\n\n").
  2. Accumulate sentences until CHUNK_SIZE is approached.
  3. Overlap by re-including last N chars of previous chunk.
  4. Never split inside a Unicode grapheme cluster.

Telugu sentence boundaries:
  - "।"  (Devanagari/Telugu danda U+0964)
  - "॥"  (double danda U+0965)
  - "\n" (line breaks common in GOs)
  - ". " (English sentences)
"""

import re
import unicodedata
from app.core.config import CHUNK_SIZE, CHUNK_OVERLAP

# ── Sentence splitter ─────────────────────────────────────────────────────────

# Splits on: Telugu dandas, double newlines, ".\n", ". " followed by capital/Telugu
_SENTENCE_SPLIT = re.compile(
    r"(?<=[।॥])\s*"  # after Telugu danda
    r"|(?<=\.)\s+(?=[A-Z\u0C00-\u0C7F])"  # after ". " before capital/Telugu
    r"|\n{2,}"  # paragraph breaks
    r"|\n(?=[A-Z\u0C00-\u0C7F])",  # newline before capital/Telugu
    re.UNICODE,
)


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences, preserving Telugu structure."""
    parts = _SENTENCE_SPLIT.split(text)
    return [p.strip() for p in parts if p.strip()]


# ── Safe character boundary ───────────────────────────────────────────────────


def _safe_truncate(text: str, max_chars: int) -> str:
    """
    Truncate text without splitting a Unicode combining sequence.
    Telugu vowel signs (U+0C3E–U+0C4C) and virama (U+0C4D) are
    combining characters — we must not break before them.
    """
    if len(text) <= max_chars:
        return text

    # Walk back from max_chars until we're not mid-combining-sequence
    i = max_chars
    while i > 0:
        ch = text[i]
        cat = unicodedata.category(ch)
        # Mn = non-spacing mark (vowel signs, virama)
        # Mc = spacing combining mark
        if cat not in ("Mn", "Mc"):
            break
        i -= 1

    return text[:i]


# ── Main chunking function ────────────────────────────────────────────────────


def chunk_text(
    text: str,
    metadata: dict | None = None,
) -> list[dict]:
    """
    Split document text into overlapping chunks.

    Returns list of dicts:
        {
            "text": str,          # chunk content
            "metadata": dict,     # inherited + chunk-level keys
            "chunk_index": int,   # position within document
        }

    Args:
        text:     Full extracted document text.
        metadata: Document-level metadata to attach to every chunk.
    """
    if not text or not text.strip():
        return []

    metadata = metadata or {}
    sentences = _split_sentences(text)

    chunks = []
    current = ""
    chunk_idx = 0
    overlap_tail = ""  # last N chars of previous chunk for overlap

    for sentence in sentences:
        # Would adding this sentence exceed CHUNK_SIZE?
        candidate = (overlap_tail + " " + current + " " + sentence).strip()

        if len(candidate) <= CHUNK_SIZE:
            current = (current + " " + sentence).strip()
        else:
            # Flush current chunk
            if current:
                safe_chunk = _safe_truncate(current, CHUNK_SIZE)
                chunks.append(
                    {
                        "text": safe_chunk,
                        "metadata": {**metadata, "chunk_index": chunk_idx},
                        "chunk_index": chunk_idx,
                    }
                )
                chunk_idx += 1

                # Build overlap tail from end of this chunk
                overlap_tail = (
                    safe_chunk[-CHUNK_OVERLAP:]
                    if len(safe_chunk) > CHUNK_OVERLAP
                    else safe_chunk
                )

            # Start new chunk with overlap
            current = (overlap_tail + " " + sentence).strip()

    # Flush final chunk
    if current.strip():
        safe_chunk = _safe_truncate(current.strip(), CHUNK_SIZE)
        chunks.append(
            {
                "text": safe_chunk,
                "metadata": {**metadata, "chunk_index": chunk_idx},
                "chunk_index": chunk_idx,
            }
        )

    return chunks
