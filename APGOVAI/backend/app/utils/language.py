"""
Language helpers for English and Telugu chat requests.

Telugu Unicode block: U+0C00-U+0C7F.
Counting Telugu code points is reliable for short government document queries
and avoids adding another runtime dependency to the request path.
"""

from __future__ import annotations

from typing import Optional

TELUGU_START = 0x0C00
TELUGU_END = 0x0C7F

SUPPORTED_LANGUAGES = {
    "english": {
        "code": "en",
        "label": "English",
    },
    "telugu": {
        "code": "te",
        "label": "తెలుగు",
    },
}

DOCUMENT_LANGUAGES = {
    "english",
    "telugu",
    "mixed",
}

LANGUAGE_ALIASES = {
    "auto": "auto",
    "": "auto",
    "en": "english",
    "eng": "english",
    "english": "english",
    "te": "telugu",
    "telugu": "telugu",
    "తెలుగు": "telugu",
}


def count_telugu_chars(text: str) -> int:
    """Count characters in the Telugu Unicode block."""
    return sum(1 for ch in text if TELUGU_START <= ord(ch) <= TELUGU_END)


def count_english_chars(text: str) -> int:
    """Count Latin alphabetic characters used in English text."""
    return sum(1 for ch in text if ("a" <= ch.lower() <= "z"))


def language_stats(text: str) -> dict:
    """Return script counts and ratios for English/Telugu/mixed text."""
    telugu_count = count_telugu_chars(text)
    english_count = count_english_chars(text)
    script_total = telugu_count + english_count

    if script_total == 0:
        return {
            "telugu_chars": telugu_count,
            "english_chars": english_count,
            "script_chars": script_total,
            "telugu_ratio": 0.0,
            "english_ratio": 0.0,
        }

    return {
        "telugu_chars": telugu_count,
        "english_chars": english_count,
        "script_chars": script_total,
        "telugu_ratio": telugu_count / script_total,
        "english_ratio": english_count / script_total,
    }


def classify_document_language(text: str) -> str:
    """
    Classify document/chunk text as english, telugu, or mixed.

    Mixed is intentionally script-based: many AP government documents contain
    English identifiers, GO numbers, names, and Telugu body text in the same
    page. The classification is metadata for retrieval/debugging, not a
    requirement to translate the source.
    """
    if not text:
        return "english"

    stats = language_stats(text)
    telugu_ratio = stats["telugu_ratio"]
    english_ratio = stats["english_ratio"]

    if stats["script_chars"] == 0:
        return "english"

    if telugu_ratio >= 0.15 and english_ratio >= 0.15:
        return "mixed"

    if telugu_ratio > 0:
        return "telugu"

    return "english"


def detect_language(text: str) -> str:
    """
    Detect the best response language for a user query.

    Returns "telugu" when Telugu is present with meaningful weight; otherwise
    returns "english". Mixed queries with Telugu script should generally receive
    Telugu responses, while mixed source documents are classified separately via
    classify_document_language().
    """
    if not text:
        return "english"

    stats = language_stats(text)

    if stats["script_chars"] == 0:
        return "english"

    language = "telugu" if stats["telugu_ratio"] > 0.10 else "english"

    preview = (
        text[:60]
        .encode(
            "unicode_escape",
            errors="backslashreplace",
        )
        .decode("ascii")
    )

    print(
        f"[language] detected={language} "
        f"telugu_ratio={stats['telugu_ratio']:.2f} "
        f"english_ratio={stats['english_ratio']:.2f} "
        f"query={preview}"
    )

    return language


def document_language_metadata(text: str) -> dict:
    """Build language metadata for an ingested document or chunk."""
    stats = language_stats(text)

    return {
        "language": classify_document_language(text),
        "telugu_ratio": round(stats["telugu_ratio"], 4),
        "english_ratio": round(stats["english_ratio"], 4),
        "telugu_chars": stats["telugu_chars"],
        "english_chars": stats["english_chars"],
    }


def normalize_language(value: Optional[str]) -> str:
    """Normalize API language input to english, telugu, or auto."""
    if value is None:
        return "auto"

    key = value.strip().lower()
    language = LANGUAGE_ALIASES.get(key)

    if not language:
        return "auto"

    return language


def resolve_language(requested_language: Optional[str], text: str) -> str:
    """Resolve a requested language, falling back to query detection for auto."""
    language = normalize_language(requested_language)

    if language == "auto":
        return detect_language(text)

    return language
