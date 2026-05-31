from datetime import (
    datetime,
    timedelta,
)

from jose import jwt

from passlib.context import (
    CryptContext,
)

from sqlalchemy.orm import Session

from app.database.models import (
    User,
)

from app.core.config import (
    JWT_SECRET,
    JWT_ALGORITHM,
    JWT_EXPIRE_MINUTES,
)

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
)


def hash_password(password: str):

    print("PASSWORD:", password)

    print("LENGTH:", len(password.encode("utf-8")))

    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
):
    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(
    user: User,
):
    expire = datetime.utcnow() + timedelta(
        minutes=JWT_EXPIRE_MINUTES,
    )

    payload = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )


def authenticate_user(
    db: Session,
    username: str,
    password: str,
):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        return None

    if not verify_password(
        password,
        user.password_hash,
    ):
        return None

    return user
