"""
Cross-encoder reranking.
"""

from sentence_transformers import (
    CrossEncoder,
)

from app.core.config import (
    RERANK_MODEL,
    RERANK_TOP,
)

model = CrossEncoder(
    RERANK_MODEL,
    device="cpu",
)


def rerank(
    query,
    docs,
):

    pairs = [[query, d["text"]] for d in docs]

    scores = model.predict(pairs)

    ranked = sorted(
        zip(docs, scores),
        key=lambda x: x[1],
        reverse=True,
    )

    return [d for d, _ in ranked[:RERANK_TOP]]
