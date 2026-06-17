from rank_bm25 import BM25Okapi

from app.core.config import COLLECTIONS

from app.vector.qdrant_client import (
    get_all_chunks,
)


def bm25_search(
    query,
    limit=10,
):

    docs = []

    for cfg in COLLECTIONS.values():

        try:

            docs.extend(get_all_chunks(cfg["collection"]))

        except Exception as e:

            print(f"Skipping {cfg['collection']}: {e}")

    corpus = [doc["text"] for doc in docs]

    tokenized = [text.lower().split() for text in corpus]

    bm25 = BM25Okapi(tokenized)

    scores = bm25.get_scores(query.lower().split())

    ranked = sorted(
        zip(
            docs,
            scores,
        ),
        key=lambda x: x[1],
        reverse=True,
    )

    return [item[0] for item in ranked[:limit]]
