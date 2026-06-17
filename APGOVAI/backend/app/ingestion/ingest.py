"""
Document ingestion pipeline.

Key fixes:
  1. Passes metadata to chunk_text() — every chunk carries doc_type,
     department, source, year, go_number, page info.
  2. Uses embed_passage() — correct "passage: " prefix for E5 model.
  3. Chunk dicts now include metadata inline (not just source + collection).
  4. store_chunks called once per collection with all accumulated chunks.
"""

import re
from pathlib import Path

from app.ingestion.converter import extract_text
from app.ingestion.chunker import chunk_text
from app.embedding.embedder import embed_passage  # ← FIXED: passage prefix
from app.vector.qdrant_client import store_chunks
from app.ingestion.manifest import is_changed, mark_ingested
from app.core.config import COLLECTIONS
from app.utils.language import (
    document_language_metadata,
)

SUPPORTED = {
    ".pdf",
    ".docx",
    ".doc",
    ".xlsx",
    ".xls",
    ".csv",
    ".txt",
    ".md",
    ".html",
}


# ── Metadata extraction from filename ────────────────────────────────────────

_GO_RE = re.compile(r"\bGO[_\s-]?(?:Ms|Rt|P)?[_\s-]?(\d+)\b", re.IGNORECASE)
_YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")


def extract_file_metadata(file_path: Path, collection_cfg: dict) -> dict:
    """
    Extract as much metadata as possible from filename and path.

    Example filename: "GO_Ms_42_Finance_2023.pdf"
    Extracted: go_number=42, department=Finance, year=2023
    """
    name = file_path.stem  # filename without extension

    # GO number
    go_match = _GO_RE.search(name)
    go_number = go_match.group(1) if go_match else ""

    # Year
    year_match = _YEAR_RE.search(name)
    year = year_match.group(0) if year_match else ""

    # Department — segment between underscores/hyphens that isn't a number or GO
    parts = re.split(r"[_\-\s]+", name)
    dept_parts = [
        p
        for p in parts
        if p
        and not p.isdigit()
        and not re.match(r"^GO|Ms|Rt|^20\d{2}$|^19\d{2}$", p, re.I)
    ]
    department = " ".join(dept_parts[:2]) if dept_parts else ""

    return {
        "source": file_path.name,
        "document_type": collection_cfg.get("doc_type", ""),
        "department": department,
        "go_number": go_number,
        "year": year,
        "collection": collection_cfg.get("collection", ""),
    }


# ── Per-collection ingestion ──────────────────────────────────────────────────


def ingest_collection(name: str, cfg: dict):
    """
    Ingest all documents in a collection directory.
    """
    source_dir = Path(cfg["data"])

    if not source_dir.exists():
        print(f"[ingest] Directory not found: {source_dir}")
        return

    all_chunks = []

    for file in sorted(source_dir.rglob("*")):

        if not file.is_file():
            continue

        if file.suffix.lower() not in SUPPORTED:
            continue

        # Incremental — skip unchanged files
        if not is_changed(file):
            print(f"[ingest] Skipping (unchanged): {file.name}")
            continue

        print(f"\n[ingest] Processing: {file.name}")

        # Extract raw text
        text = extract_text(file)

        if not text:
            print(f"[ingest] No text extracted from {file.name}")
            continue

        # Build metadata for this document
        metadata = extract_file_metadata(file, cfg)
        language_metadata = document_language_metadata(text)
        metadata.update(
            {
                "language": language_metadata["language"],
                "document_language": language_metadata["language"],
                "document_telugu_ratio": language_metadata["telugu_ratio"],
                "document_english_ratio": language_metadata["english_ratio"],
                "document_telugu_chars": language_metadata["telugu_chars"],
                "document_english_chars": language_metadata["english_chars"],
            }
        )

        print(
            "[ingest] language="
            f"{metadata['document_language']} "
            f"telugu={metadata['document_telugu_ratio']:.2f} "
            f"english={metadata['document_english_ratio']:.2f}"
        )

        # Chunk with metadata attached
        chunks = chunk_text(text, metadata=metadata)
        print(f"[ingest] {len(chunks)} chunks from {file.name}")

        # Embed each chunk with passage prefix
        for chunk in chunks:
            try:
                embedding = embed_passage(chunk["text"])  # ← FIXED

                all_chunks.append(
                    {
                        "text": chunk["text"],
                        "embedding": embedding,
                        "metadata": chunk["metadata"],  # full metadata
                    }
                )

            except Exception as e:
                print(f"[ingest] Embedding error: {e}")

        mark_ingested(file)

    # Store everything at once
    if all_chunks:
        store_chunks(cfg["collection"], all_chunks)
        print(f"\n[ingest] Stored {len(all_chunks)} chunks → {cfg['collection']}")
    else:
        print(f"\n[ingest] Nothing new to store for {name}")
