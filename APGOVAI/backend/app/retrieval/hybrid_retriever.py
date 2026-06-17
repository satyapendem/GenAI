from app.retrieval.retriever import (
    retrieve_documents,
)

from app.retrieval.bm25_retriever import (
    bm25_search,
)


def hybrid_search(
    query,
):

    vector_docs = retrieve_documents(query)

    bm25_docs = bm25_search(query)

    merged = {}

    for doc in vector_docs + bm25_docs:

        text = doc["text"]

        merged[text] = doc

    return list(merged.values())
