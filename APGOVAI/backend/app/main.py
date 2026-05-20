from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.models import ChatRequest
from app.rag_chain import stream_answer


app = FastAPI(title="Simple RAG Chat API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "RAG API is running"}


@app.post("/chat")
async def chat(request: ChatRequest):

    async def generate():
        async for chunk in stream_answer(request.question):
            yield chunk

    return StreamingResponse(generate(), media_type="text/plain")