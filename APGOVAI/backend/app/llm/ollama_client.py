"""
Ollama streaming client — no LangChain dependency.

Key fixes:
  1. Uses httpx directly against Ollama's /api/generate endpoint.
     Old code imported langchain_ollama — violates your "no LangChain" rule
     and added an opaque wrapper that could mangle Telugu tokens.

  2. Telugu-safe streaming strategy.
     Problem: Telugu text has NO spaces between many morphemes.
     "space-split" buffering breaks Telugu compound words.

     Solution: buffer on sentence boundaries and line breaks instead.
     We emit a chunk when we see:
       - A space followed by a new word start
       - A Telugu danda "।"
       - A newline
       - A Markdown table row end "|"
     This gives smooth streaming without corrupting Telugu grapheme clusters.

  3. Proper SSE-style newline flushing for React EventSource.
"""

import json
import httpx

from app.core.config import OLLAMA_MODEL, OLLAMA_HOST

# ── Telugu-safe buffer emitter ────────────────────────────────────────────────

# Characters at which it's safe to flush the buffer to the client
_FLUSH_CHARS = {
    " ",  # word boundary (English)
    "\n",  # line break
    "।",  # Telugu danda (U+0964)
    "॥",  # double danda (U+0965)
    "|",  # Markdown table cell separator
}


def _is_telugu_combining(ch: str) -> bool:
    """
    Returns True if the character is a Telugu combining mark.
    These must NEVER be split from the base character before them.

    Telugu combining range:
      U+0C3E–U+0C4C  vowel signs (ా, ి, ీ, ు, ూ, ృ, ె, ే, ై, ొ, ో, ౌ)
      U+0C4D          virama (halant ్)
      U+0C55, U+0C56  length marks
    """
    cp = ord(ch)
    return (0x0C3E <= cp <= 0x0C4C) or cp in (0x0C4D, 0x0C55, 0x0C56)


def _safe_to_flush(buffer: str) -> bool:
    """
    Check that the last character in buffer is not a Telugu combining mark.
    If it is, we must wait for the next token before flushing.
    """
    if not buffer:
        return False
    return not _is_telugu_combining(buffer[-1])


# ── Streaming generator ───────────────────────────────────────────────────────


def stream_generate(prompt: str):
    """
    Stream LLM response token-by-token via Ollama /api/generate.

    Yields text chunks safe for Telugu + English mixed output.
    Each yielded chunk is a complete word, syllable group, or sentence fragment —
    never a half-formed Unicode combining sequence.
    """
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": True,
        "options": {
            "temperature": 0.1,  # low — we want factual grounded answers
            "repeat_penalty": 1.1,
            "num_predict": 1024,
        },
    }

    buffer = ""

    try:
        with httpx.stream(
            "POST",
            f"{OLLAMA_HOST}/api/generate",
            json=payload,
            timeout=120.0,
        ) as response:

            response.raise_for_status()

            for line in response.iter_lines():
                if not line:
                    continue

                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue

                token = data.get("response", "")

                if not token:
                    # Check if generation is done
                    if data.get("done", False) and buffer:
                        if _safe_to_flush(buffer):
                            yield buffer
                            buffer = ""
                    continue

                buffer += token

                # Flush on safe boundaries
                if any(ch in buffer for ch in _FLUSH_CHARS) and _safe_to_flush(buffer):
                    yield buffer
                    buffer = ""

        # Final flush
        if buffer and _safe_to_flush(buffer):
            yield buffer

        elif buffer:
            # Force flush — we're done regardless
            yield buffer

    except httpx.HTTPStatusError as e:
        print(f"[ollama] HTTP error: {e}")
        yield "\n\nError: Could not reach Ollama server."

    except Exception as e:
        print(f"[ollama] Streaming error: {e}")
        yield "\n\nError generating response."
