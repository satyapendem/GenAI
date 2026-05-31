from fastapi import (
    Depends,
    HTTPException,
)

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
)

from jose import jwt

from sqlalchemy.orm import Session

from app.database.session import (
    get_db,
)

from app.database.models import (
    User,
)

from app.core.config import (
    JWT_SECRET,
    JWT_ALGORITHM,
)

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials

    try:

        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
        )

        user_id = payload.get("sub")

    except Exception:

        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user:

        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    return user


def require_admin(
    current_user=Depends(get_current_user),
):
    if current_user.role != "admin":

        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )

    return current_user
