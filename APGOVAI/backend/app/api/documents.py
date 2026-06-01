from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends,
)

from sqlalchemy.orm import (
    Session,
)

from app.database.session import (
    get_db,
)

from app.services.security import (
    require_admin,
)

from app.services.document_service import (
    upload_document,
    get_documents,
    delete_document,
)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post("/upload")
async def upload(
    collection: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):

    return await upload_document(
        db,
        file,
        collection,
        admin.id,
    )


@router.get("")
def documents(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):

    docs = get_documents(db)

    return [
        {
            "id": str(d.id),
            "filename": d.filename,
            "collection": d.collection,
            "status": d.status,
            "created_at": d.created_at,
        }
        for d in docs
    ]


@router.delete("/{id}")
def remove(
    id: str,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):

    return delete_document(
        db,
        id,
    )
