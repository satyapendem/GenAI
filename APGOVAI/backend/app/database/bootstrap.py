from app.database.models import (
    User,
)

from app.database.session import (
    SessionLocal,
)

from app.services.auth_service import (
    hash_password,
)


def create_default_admin():

    db = SessionLocal()

    admin = db.query(User).filter(User.username == "admin").first()

    if admin:

        db.close()

        return

    admin = User(
        username="admin",
        password_hash=hash_password("admin123"),
        role="admin",
    )

    db.add(admin)

    db.commit()

    db.close()

    print("Default admin created")
