from fastapi import FastAPI

from fastapi.middleware.cors import (
    CORSMiddleware,
)

from app.api.chat import (
    router as chat_router,
)

from app.database.init_db import (
    create_tables,
)

from app.api.auth import (
    router as auth_router,
)

from app.api.admin import (
    router as admin_router,
)

from app.database.bootstrap import (
    create_default_admin,
)

app = FastAPI()


@app.on_event("startup")
def startup():

    create_tables()

    create_default_admin()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

app.include_router(admin_router)

app.include_router(
    chat_router,
)


@app.get("/")
def root():

    return {
        "message": "APGovAI Running",
    }
