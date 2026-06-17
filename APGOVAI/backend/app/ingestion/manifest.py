"""
Track ingested documents.

Only re-ingest changed files.
"""

import json

import hashlib

from pathlib import Path

MANIFEST_PATH = Path("./processed/manifest.json")

INGESTION_PIPELINE_VERSION = "2026-06-13-language-v2"


def load_manifest():
    """
    Load manifest file.
    """

    if not MANIFEST_PATH.exists():

        return {}

    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def save_manifest(
    manifest,
):
    """
    Save manifest.
    """

    MANIFEST_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    MANIFEST_PATH.write_text(
        json.dumps(
            manifest,
            indent=2,
        ),
        encoding="utf-8",
    )


def file_hash(
    path,
):
    """
    Generate file hash.
    """

    md5 = hashlib.md5()

    with open(path, "rb") as f:

        while chunk := f.read(8192):

            md5.update(chunk)

    return md5.hexdigest()


def is_changed(
    path,
):
    """
    Check if file changed.
    """

    manifest = load_manifest()

    current_hash = file_hash(path)

    saved = manifest.get(str(path))

    if isinstance(saved, dict):
        saved_hash = saved.get("hash")
        saved_version = saved.get("pipeline_version")
    else:
        saved_hash = saved
        saved_version = None

    return current_hash != saved_hash or saved_version != INGESTION_PIPELINE_VERSION


def mark_ingested(
    path,
):
    """
    Save ingested hash.
    """

    manifest = load_manifest()

    manifest[str(path)] = {
        "hash": file_hash(path),
        "pipeline_version": INGESTION_PIPELINE_VERSION,
    }

    save_manifest(manifest)
