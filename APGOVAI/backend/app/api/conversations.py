from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
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

from app.services.conversation_service import (
    create_conversation,
    get_user_conversations,
    get_messages,
    get_conversation,
    delete_conversation,
)

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


@router.post("")
def create_chat(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):

    conversation = create_conversation(
        db,
        user.id,
    )

    return {
        "id": str(conversation.id),
        "title": conversation.title,
    }


@router.get("")
def list_chats(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):

    conversations = get_user_conversations(
        db,
        user.id,
    )

    return [
        {
            "id": str(c.id),
            "title": c.title,
        }
        for c in conversations
    ]


@router.get("/{conversation_id}/messages")
def messages(
    conversation_id: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):

    conversation = get_conversation(
        db,
        conversation_id,
    )

    if not conversation:

        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    if str(conversation.user_id) != str(user.id):

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )

    msgs = get_messages(
        db,
        conversation_id,
    )

    return [
        {
            "id": str(m.id),
            "role": m.role,
            "content": m.content,
        }
        for m in msgs
    ]


@router.delete("/{conversation_id}")
def remove_chat(
    conversation_id: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):

    conversation = get_conversation(
        db,
        conversation_id,
    )

    if not conversation:

        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    if str(conversation.user_id) != str(user.id):

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )

    delete_conversation(
        db,
        conversation_id,
    )

    return {"message": "Conversation deleted"}
