import uuid

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean

from sqlalchemy.dialects.postgresql import (
    UUID,
)

from sqlalchemy.sql import func

from app.database.session import (
    Base,
)


class User(Base):

    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    username = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash = Column(
        Text,
        nullable=False,
    )

    role = Column(
        String,
        nullable=False,
        default="user",
    )

    is_active = Column(
        Boolean,
        default=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


class Conversation(Base):

    __tablename__ = "conversations"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    title = Column(
        String,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


class Message(Base):

    __tablename__ = "messages"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id"),
        nullable=False,
    )

    role = Column(
        String,
        nullable=False,
    )

    content = Column(
        Text,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


class Document(Base):

    __tablename__ = "documents"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    filename = Column(
        String,
        nullable=False,
    )

    file_hash = Column(
        String,
        unique=True,
        nullable=False,
    )

    collection = Column(
        String,
        nullable=False,
    )

    uploaded_by = Column(
        UUID(as_uuid=True),
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


class AuditLog(Base):

    __tablename__ = "audit_logs"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id = Column(
        UUID(as_uuid=True),
    )

    action = Column(
        Text,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
