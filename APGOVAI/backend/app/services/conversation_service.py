from sqlalchemy.orm import Session

from app.database.models import (
    Conversation,
    Message,
)


def create_conversation(
    db: Session,
    user_id,
    title="New Chat",
):

    conversation = Conversation(
        user_id=user_id,
        title=title,
    )

    db.add(conversation)

    db.commit()

    db.refresh(conversation)

    return conversation


def get_conversation(
    db: Session,
    conversation_id,
):

    return db.query(Conversation).filter(Conversation.id == conversation_id).first()


def get_user_conversations(
    db: Session,
    user_id,
):

    return (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id)
        .order_by(Conversation.created_at.desc())
        .all()
    )


def save_message(
    db,
    conversation_id,
    role,
    content,
):

    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
    )

    db.add(message)

    #
    # First user message becomes title
    #

    if role == "user":

        conversation = (
            db.query(Conversation).filter(Conversation.id == conversation_id).first()
        )

        if conversation:

            existing_messages = (
                db.query(Message)
                .filter(Message.conversation_id == conversation_id)
                .count()
            )

            #
            # First message only
            #

            if existing_messages == 0:

                title = content.strip().replace("\n", " ")

                #
                # Keep sidebar clean
                #

                if len(title) > 60:

                    title = title[:60] + "..."

                conversation.title = title

    db.commit()

    db.refresh(message)

    return message


def get_messages(
    db: Session,
    conversation_id,
):

    return (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )


def delete_conversation(
    db: Session,
    conversation_id,
):

    (db.query(Message).filter(Message.conversation_id == conversation_id).delete())

    (db.query(Conversation).filter(Conversation.id == conversation_id).delete())

    db.commit()


def get_conversation_context(
    db,
    conversation_id,
    limit=10,
):
    """
    Get latest messages for memory.
    """

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
        .all()
    )

    messages.reverse()

    return messages
