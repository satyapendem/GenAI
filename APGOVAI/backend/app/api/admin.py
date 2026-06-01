from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.database.session import (
    get_db,
)

from app.database.models import (
    User,
)

from app.database.schemas import (
    UserCreate,
)

from app.services.security import (
    require_admin,
)

from app.services.auth_service import (
    hash_password,
)

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


@router.post("/users")
def create_user(
    request: UserCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):

    existing = db.query(User).filter(User.username == request.username).first()

    if existing:

        raise HTTPException(
            status_code=400,
            detail="User already exists",
        )

    user = User(
        username=request.username,
        password_hash=hash_password(request.password),
        role=request.role,
    )

    db.add(user)

    db.commit()

    db.refresh(user)

    return {
        "message": "User created",
        "id": str(user.id),
    }


@router.get("/users")
def list_users(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):

    users = db.query(User).order_by(User.created_at.desc()).all()

    return [
        {
            "id": str(u.id),
            "username": u.username,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at,
        }
        for u in users
    ]
