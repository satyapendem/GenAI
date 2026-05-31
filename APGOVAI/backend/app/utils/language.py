"""
Language detection for Telugu and English.

Telugu Unicode block: U+0C00–U+0C7F
We count Telugu codepoints directly — no external library needed.
This is faster and more reliable than langdetect for short queries.
"""

import unicodedata

# Telugu Unicode range
TELUGU_START = 0x0C00
TELUGU_END = 0x0C7F


def count_telugu_chars(text: str) -> int:
    """Count characters in Telugu Unicode block."""
    return sum(1 for ch in text if TELUGU_START <= ord(ch) <= TELUGU_END)


def detect_language(text: str) -> str:
    """
    Detect whether query is Telugu or English.

    Returns:
        "telugu"  — if >10% of non-space chars are Telugu codepoints
        "english" — otherwise

    Threshold is intentionally low (10%) because mixed queries like
    "GO number 123 బడ్జెట్ గురించి చెప్పండి" are Telugu-intent queries.
    """
    if not text:
        return "english"

    stripped = text.replace(" ", "")

    if not stripped:
        return "english"

    telugu_count = count_telugu_chars(stripped)
    ratio = telugu_count / len(stripped)

    language = "telugu" if ratio > 0.10 else "english"

    print(f"[language] detected={language} telugu_ratio={ratio:.2f} query={text[:60]}")

    return language
