from langchain_community.vectorstores import Chroma
from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate


from app.config import CHROMA_DB_PATH, OLLAMA_MODEL
from app.prompts import SYSTEM_PROMPT


embeddings = OllamaEmbeddings(model="nomic-embed-text")

vector_store = Chroma(
    persist_directory=CHROMA_DB_PATH,
    embedding_function=embeddings,
)

retriever = vector_store.as_retriever(search_kwargs={"k": 3})

llm = ChatOllama(
    model=OLLAMA_MODEL,
    temperature=0,
)


prompt_template = ChatPromptTemplate.from_template(
    """
{system_prompt}

Context:
{context}

Question:
{question}

Answer:
"""
)


def get_context(question: str):
    docs = retriever.invoke(question)

    return "\n\n".join([doc.page_content for doc in docs])


async def stream_answer(question: str):
    context = get_context(question)

    prompt = prompt_template.format(
        system_prompt=SYSTEM_PROMPT,
        context=context,
        question=question,
    )

    async for chunk in llm.astream(prompt):
        if chunk.content:
            yield chunk.content