from pathlib import Path
import hashlib

from app.database.models import (
    Document,
)

from app.ingestion.ingest import (
    ingest_collection,
)

from app.core.config import (
    COLLECTIONS,
)

UPLOAD_ROOT = Path("./training_data")


def calculate_hash(
    path,
):

    md5 = hashlib.md5()

    with open(path, "rb") as f:

        while chunk := f.read(8192):

            md5.update(chunk)

    return md5.hexdigest()


async def upload_document(
    db,
    file,
    collection,
    user_id,
):

    folder = UPLOAD_ROOT / collection

    folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    filepath = folder / file.filename

    content = await file.read()

    filepath.write_bytes(content)

    file_hash = calculate_hash(filepath)

    existing = db.query(Document).filter(Document.file_hash == file_hash).first()

    if existing:

        filepath.unlink(missing_ok=True)

        return {"message": "Document already exists"}

    document = Document(
        filename=file.filename,
        file_hash=file_hash,
        collection=collection,
        file_path=str(filepath),
        uploaded_by=user_id,
        status="processing",
    )

    db.add(document)

    db.commit()

    db.refresh(document)

    try:

        ingest_collection(
            collection,
            COLLECTIONS[collection],
        )

        document.status = "completed"

        db.commit()

    except Exception:

        document.status = "failed"

        db.commit()

    return {"message": "Uploaded successfully"}


def get_documents(
    db,
):

    docs = db.query(Document).order_by(Document.created_at.desc()).all()

    return docs


def delete_document(
    db,
    document_id,
):

    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:

        return {"message": "Not found"}

    Path(document.file_path).unlink(missing_ok=True)

    db.delete(document)

    db.commit()

    return {"message": "Deleted"}
