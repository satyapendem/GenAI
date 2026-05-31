from sqlalchemy import create_engine

from sqlalchemy.orm import (
    sessionmaker,
    declarative_base,
)

from app.core.config import (
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_DB,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
)

DATABASE_URL = (
    f"postgresql+psycopg://"
    f"{POSTGRES_USER}:"
    f"{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:"
    f"{POSTGRES_PORT}/"
    f"{POSTGRES_DB}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()
