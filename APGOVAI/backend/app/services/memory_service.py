from sqlalchemy.orm import Session

from app.database.models import (
    Message,
)

MEMORY_LIMIT = 10


def build_memory(
    db: Session,
    conversation_id,
):

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(MEMORY_LIMIT)
        .all()
    )

    messages.reverse()

    if not messages:

        return ""

    memory = []

    for msg in messages:

        memory.append(f"{msg.role.upper()}:\n{msg.content}")

    return "\n\n".join(memory)
