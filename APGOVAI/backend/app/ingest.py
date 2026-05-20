from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

from app.config import PDF_FOLDER, CHROMA_DB_PATH
from app.utils import split_documents


def ingest_documents():
    print("Loading PDF files...")

    loader = PyPDFDirectoryLoader(PDF_FOLDER)
    documents = loader.load()

    print(f"Loaded {len(documents)} documents")

    chunks = split_documents(documents)

    print(f"Created {len(chunks)} chunks")

    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DB_PATH,
    )

    vector_store.persist()

    print("Documents ingested successfully")


if __name__ == "__main__":
    ingest_documents()