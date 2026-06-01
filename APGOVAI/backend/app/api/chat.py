from fastapi import (
    APIRouter,
    Depends,
)

from fastapi.responses import (
    StreamingResponse,
)

from sqlalchemy.orm import (
    Session,
)

from app.database.session import (
    get_db,
)

from app.services.security import (
    get_current_user,
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

from app.services.conversation_service import (
    save_message,
    get_conversation_context,
)

router = APIRouter()


@router.post("/chat")
def chat(
    body: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    question = body.get("question", "").strip()

    conversation_id = body.get("conversation_id")

    if not question:

        return {"error": "Question required"}

    #
    # Save user message
    #

    save_message(
        db,
        conversation_id,
        "user",
        question,
    )

    #
    # Memory
    #

    history = get_conversation_context(
        db,
        conversation_id,
        limit=20,
    )

    #
    # Retrieval
    #

    docs = retrieve_documents(question)

    #
    # Prompt
    #

    prompt = build_prompt(
        query=question,
        docs=docs,
        history=history,
    )

    def generate():

        answer = ""

        for chunk in stream_generate(prompt):

            answer += chunk

            yield chunk

        #
        # Save assistant response
        #

        save_message(
            db,
            conversation_id,
            "assistant",
            answer,
        )

    return StreamingResponse(
        generate(),
        media_type="text/plain",
    )
