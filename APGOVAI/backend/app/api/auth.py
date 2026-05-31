from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.database.session import (
    get_db,
)

from app.database.schemas import (
    LoginRequest,
)

from app.services.auth_service import (
    authenticate_user,
    create_access_token,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/login")
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):

    user = authenticate_user(
        db,
        request.username,
        request.password,
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    token = create_access_token(
        user,
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
    }
