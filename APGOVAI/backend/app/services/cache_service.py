import hashlib

from app.database.models import (
    ResponseCache,
)


def generate_hash(
    text: str,
) -> str:

    return hashlib.sha256(text.strip().lower().encode("utf-8")).hexdigest()


def get_cached_response(
    db,
    question,
):

    qhash = generate_hash(question)

    return db.query(ResponseCache).filter(ResponseCache.question_hash == qhash).first()


def save_cached_response(
    db,
    question,
    answer,
):

    qhash = generate_hash(question)

    existing = (
        db.query(ResponseCache).filter(ResponseCache.question_hash == qhash).first()
    )

    if existing:

        return

    cache = ResponseCache(
        question_hash=qhash,
        question=question,
        answer=answer,
    )

    db.add(cache)

    db.commit()
