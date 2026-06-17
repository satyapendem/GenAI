"""
Unicode-safe semantic chunker for Telugu, English, and mixed documents.

The chunker avoids cutting Telugu combining sequences, preserves paragraph
boundaries from extraction, and stores chunk-level language metadata.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Optional

from app.core.config import CHUNK_SIZE, CHUNK_OVERLAP
from app.utils.language import (
    document_language_metadata,
)

_SENTENCE_SPLIT = re.compile(
    r"(?<=[।॥.!?])\s+(?=[A-Z0-9\u0C00-\u0C7F])"
    r"|(?<=[।॥.!?])\n+"
    r"|\n{2,}"
    r"|\n(?=\[PAGE\s+\d+\])"
    r"|\n(?=\[SHEET\s+.+?\])",
    re.UNICODE,
)

_PREFERRED_BREAKS = (
    "\n",
    ". ",
    "? ",
    "! ",
    "। ",
    "॥ ",
    "; ",
    ", ",
    " ",
)


def _is_combining_mark(
    ch: str,
) -> bool:
    if not ch:
        return False

    return unicodedata.category(ch) in (
        "Mn",
        "Mc",
        "Me",
    )


def _is_unsafe_boundary(
    text: str,
    index: int,
) -> bool:
    """
    Return True if cutting at index would split a Unicode cluster.

    Telugu vowel signs often follow the base character. A virama (U+0C4D)
    also joins with the following consonant, so a chunk must not end there.
    """
    if index <= 0 or index >= len(text):
        return False

    previous = text[index - 1]
    current = text[index]

    return (
        _is_combining_mark(current)
        or previous == "\u0c4d"
        or previous == "\u200d"
        or current == "\u200d"
    )


def _safe_boundary(
    text: str,
    index: int,
) -> int:
    """Move index backward until it is safe to cut."""
    index = min(
        max(index, 1),
        len(text),
    )

    while index > 1 and _is_unsafe_boundary(
        text,
        index,
    ):
        index -= 1

    return index


def _safe_truncate(
    text: str,
    max_chars: int,
) -> str:
    """Truncate text without splitting a Unicode combining sequence."""
    if len(text) <= max_chars:
        return text

    boundary = _safe_boundary(
        text,
        max_chars,
    )

    return text[:boundary].rstrip()


def _safe_tail(
    text: str,
    max_chars: int,
) -> str:
    """Return a suffix that does not start with a combining mark."""
    if len(text) <= max_chars:
        return text

    start = len(text) - max_chars

    while start < len(text) and _is_combining_mark(text[start]):
        start += 1

    return text[start:].lstrip()


def _find_split_index(
    text: str,
    max_chars: int,
) -> int:
    """Find a readable split point at or before max_chars."""
    window = text[:max_chars]
    best = -1

    for marker in _PREFERRED_BREAKS:
        position = window.rfind(marker)

        if position > best:
            best = position + len(marker)

    if best >= int(max_chars * 0.45):
        return _safe_boundary(
            text,
            best,
        )

    return _safe_boundary(
        text,
        max_chars,
    )


def _split_long_segment(
    segment: str,
    max_chars: int,
) -> list[str]:
    """Split a long sentence/paragraph without losing text."""
    remaining = segment.strip()
    parts = []

    while len(remaining) > max_chars:
        split_at = _find_split_index(
            remaining,
            max_chars,
        )

        if split_at <= 0:
            split_at = max_chars

        part = remaining[:split_at].strip()

        if part:
            parts.append(part)

        remaining = remaining[split_at:].strip()

    if remaining:
        parts.append(remaining)

    return parts


def _split_sentences(
    text: str,
) -> list[str]:
    """Split text into Telugu/English sentence-like segments."""
    parts = _SENTENCE_SPLIT.split(text)
    segments = []

    for part in parts:
        part = part.strip()

        if not part:
            continue

        if len(part) > CHUNK_SIZE:
            segments.extend(
                _split_long_segment(
                    part,
                    CHUNK_SIZE,
                )
            )
        else:
            segments.append(part)

    return segments


def _chunk_metadata(
    base_metadata: dict,
    chunk_text_value: str,
    chunk_idx: int,
) -> dict:
    """Build metadata for a single chunk."""
    language_metadata = document_language_metadata(
        chunk_text_value,
    )

    return {
        **base_metadata,
        **language_metadata,
        "document_language": base_metadata.get(
            "document_language",
            base_metadata.get("language", language_metadata["language"]),
        ),
        "chunk_index": chunk_idx,
    }


def chunk_text(
    text: str,
    metadata: Optional[dict] = None,
) -> list[dict]:
    """
    Split document text into overlapping chunks.

    Returns:
        [
            {
                "text": str,
                "metadata": dict,
                "chunk_index": int,
            }
        ]
    """
    if not text or not text.strip():
        return []

    metadata = metadata or {}
    sentences = _split_sentences(text)

    chunks = []
    current = ""
    chunk_idx = 0
    overlap_tail = ""

    for sentence in sentences:
        candidate_parts = [
            part
            for part in (
                overlap_tail,
                current,
                sentence,
            )
            if part
        ]
        candidate = " ".join(candidate_parts).strip()

        if len(candidate) <= CHUNK_SIZE:
            current = " ".join(
                part
                for part in (
                    current,
                    sentence,
                )
                if part
            ).strip()
            continue

        if current:
            safe_chunk = _safe_truncate(
                current,
                CHUNK_SIZE,
            )

            chunks.append(
                {
                    "text": safe_chunk,
                    "metadata": _chunk_metadata(
                        metadata,
                        safe_chunk,
                        chunk_idx,
                    ),
                    "chunk_index": chunk_idx,
                }
            )
            chunk_idx += 1
            overlap_tail = _safe_tail(
                safe_chunk,
                CHUNK_OVERLAP,
            )

        current = " ".join(
            part
            for part in (
                overlap_tail,
                sentence,
            )
            if part
        ).strip()

        while len(current) > CHUNK_SIZE:
            safe_chunk = _safe_truncate(
                current,
                CHUNK_SIZE,
            )

            chunks.append(
                {
                    "text": safe_chunk,
                    "metadata": _chunk_metadata(
                        metadata,
                        safe_chunk,
                        chunk_idx,
                    ),
                    "chunk_index": chunk_idx,
                }
            )
            chunk_idx += 1
            overlap_tail = _safe_tail(
                safe_chunk,
                CHUNK_OVERLAP,
            )
            current = " ".join(
                part
                for part in (
                    overlap_tail,
                    current[len(safe_chunk) :].strip(),
                )
                if part
            ).strip()

    if current.strip():
        safe_chunk = _safe_truncate(
            current.strip(),
            CHUNK_SIZE,
        )

        chunks.append(
            {
                "text": safe_chunk,
                "metadata": _chunk_metadata(
                    metadata,
                    safe_chunk,
                    chunk_idx,
                ),
                "chunk_index": chunk_idx,
            }
        )

    return chunks
