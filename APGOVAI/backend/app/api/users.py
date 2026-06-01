from fastapi import (
    APIRouter,
    Depends,
)

from app.services.security import (
    get_current_user,
)

router = APIRouter(
    prefix="/users",
)


@router.get("/me")
def me(current_user=Depends(get_current_user)):

    return {
        "id": str(current_user.id),
        "username": current_user.username,
        "role": current_user.role,
    }
