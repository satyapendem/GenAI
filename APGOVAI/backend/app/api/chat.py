from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
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

from app.utils.language import (
    SUPPORTED_LANGUAGES,
    resolve_language,
)

from app.database.schemas import (
    ChatRequest,
)

from app.llm.ollama_client import (
    stream_generate,
)

from app.services.conversation_service import (
    save_message,
    get_conversation_context,
    get_conversation,
)

router = APIRouter()


@router.get("/chat/languages")
def chat_languages():

    return {
        "default": "auto",
        "languages": [
            {
                "id": language,
                "code": details["code"],
                "label": details["label"],
            }
            for language, details in SUPPORTED_LANGUAGES.items()
        ],
    }


@router.post("/chat")
def chat(
    body: ChatRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    question = body.question.strip()

    conversation_id = body.conversation_id

    if not question:

        raise HTTPException(
            status_code=400,
            detail="Question required",
        )

    if not conversation_id:

        raise HTTPException(
            status_code=400,
            detail="Conversation required",
        )

    conversation = get_conversation(
        db,
        conversation_id,
    )

    if not conversation:

        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    if str(conversation.user_id) != str(current_user.id):

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )

    language = resolve_language(
        body.language,
        question,
    )

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
        language=language,
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
        media_type="text/plain; charset=utf-8",
        headers={
            "X-APGovAI-Language": language,
        },
    )
