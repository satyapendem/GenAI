from fastapi import (
    APIRouter,
)

from fastapi.responses import (
    StreamingResponse,
)

from app.retrieval.retriever import (
    retrieve_documents,
)


from app.utils.prompt_builder import (
    build_prompt,
)

from app.llm.ollama_client import (
    stream_generate,
)

router = APIRouter()


@router.post("/chat")
def chat(
    body: dict,
):

    question = body.get("question", "").strip()

    if not question:

        return {"error": "Question required"}

    #
    # Retrieve documents
    #

    docs = retrieve_documents(question)

    print()
    print("========== DOCUMENTS ==========")

    for d in docs:

        print()

        print(
            d["metadata"].get(
                "source",
                "Unknown",
            )
        )

        print()

        print(d["text"][:1500])

        print()

        print("----------------------")

    print("==============================")

    #
    # Build prompt
    #

    prompt = build_prompt(query=question, docs=docs)

    #
    # Direct text streaming
    #

    return StreamingResponse(
        stream_generate(prompt),
        media_type="text/plain",
    )
