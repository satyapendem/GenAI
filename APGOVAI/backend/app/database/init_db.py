from app.database.session import (
    engine,
)

from app.database.models import (
    User,
    Conversation,
    Message,
    Document,
    AuditLog,
)

from app.database.session import (
    Base,
)


def create_tables():

    Base.metadata.create_all(
        bind=engine,
    )

    print()

    print("PostgreSQL tables ready")

    print()
