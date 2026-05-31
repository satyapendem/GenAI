"""
Central ingestion runner.

This file loops through all configured
collections and ingests documents.

Flow:

Documents
↓

Markdown Conversion

↓

Chunking

↓

Embeddings

↓

Qdrant Storage
"""

from app.core.config import (
    COLLECTIONS,
)

from app.ingestion.ingest import (
    ingest_collection,
)


def ingest_all():
    """
    Run ingestion for all collections.
    """

    for name, cfg in COLLECTIONS.items():

        print()
        print(f"=================================")

        print(f"Ingesting: {name}")

        print(f"=================================")

        ingest_collection(
            name,
            cfg,
        )

        print()
        print(f"Finished: {name}")


if __name__ == "__main__":

    ingest_all()
