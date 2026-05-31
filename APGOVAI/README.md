# APGovAI — Multilingual Government RAG Assistant

## Overview

APGovAI is a multilingual Retrieval-Augmented Generation (RAG) platform designed for Andhra Pradesh Government documents.

The system supports:

* Telugu + English queries
* Government Orders (GO)
* Budget documents
* Circulars
* Policies
* Reports
* Scanned PDFs
* Citation-based responses

The architecture is fully custom-built without LangChain to provide:

* Better performance
* Full pipeline control
* Easier debugging
* Deep learning opportunity
* Production-style architecture

---

# Features

## Multilingual Support

Supports:

* Telugu
* English
* Mixed Telugu + English

Example:

```text
ఆరోగ్య శాఖ బడ్జెట్ వివరాలు చెప్పు
```

```text
Show health department budget
```

---

# Supported File Types

| Format       | Supported |
| ------------ | --------- |
| PDF          | Yes       |
| Scanned PDF  | Yes       |
| DOCX         | Yes       |
| DOC          | Yes       |
| XLSX         | Yes       |
| XLS          | Yes       |
| CSV          | Yes       |
| PPTX         | Yes       |
| TXT          | Yes       |
| Markdown     | Yes       |
| HTML         | Yes       |
| Images (OCR) | Yes       |

---

# Architecture

```text
User Query
    ↓
Language Detection
    ↓
Embedding Generation
    ↓
Qdrant Retrieval
    ↓
Prompt Builder
    ↓
Qwen2.5 Response Generation
    ↓
Streaming Response
```

---

# Tech Stack

## Backend

| Component   | Technology            |
| ----------- | --------------------- |
| API         | FastAPI               |
| LLM         | Qwen2.5               |
| Embeddings  | multilingual-e5-small |
| Vector DB   | Qdrant                |
| OCR         | Tesseract             |
| PDF Parsing | MarkItDown            |
| Streaming   | SSE                   |

---

## Frontend

| Component          | Technology     |
| ------------------ | -------------- |
| UI                 | React          |
| Styling            | Tailwind       |
| Streaming          | Fetch Stream   |
| Markdown Rendering | react-markdown |

---

# Final Model Stack

| Purpose    | Model                          |
| ---------- | ------------------------------ |
| LLM        | qwen2.5:7b-instruct-q4_K_M     |
| Embeddings | intfloat/multilingual-e5-small |

---

# Folder Structure

```text
APGOVAI/

backend/
│
├── app/
│   │
│   ├── api/
│   │   └── chat.py
│   │
│   ├── core/
│   │   └── config.py
│   │
│   ├── embedding/
│   │   └── embedder.py
│   │
│   ├── ingestion/
│   │   ├── chunker.py
│   │   ├── converter.py
│   │   ├── ingest.py
│   │   └── registry.py
│   │
│   ├── llm/
│   │   └── ollama_client.py
│   │
│   ├── retrieval/
│   │   └── retriever.py
│   │
│   ├── utils/
│   │   ├── language.py
│   │   └── prompt_builder.py
│   │
│   ├── vector/
│   │   └── qdrant_client.py
│   │
│   └── main.py
│
├── datasets/
│
├── processed/
│
├── requirements.txt
│
└── .env

frontend/
```

---

# Hardware Recommendation

## Minimum

| Resource | Requirement |
| -------- | ----------- |
| RAM      | 16 GB       |
| GPU VRAM | 4 GB        |
| Storage  | 30 GB       |

---

# Why Lightweight Models Were Chosen

Initial models:

```text
Qwen3-14B
bge-m3
reranker
```

caused:

* CUDA OOM
* Slow generation
* Heavy memory usage

Final optimized stack:

```text
Qwen2.5 7B Q4
+
multilingual-e5-small
```

provides:

* Faster inference
* Stable GPU usage
* Better streaming
* Good Telugu support

---

# Ubuntu Dependencies

Install system packages first.

```bash
sudo apt update

sudo apt install -y \
tesseract-ocr \
tesseract-ocr-tel \
poppler-utils \
libmagic1 \
antiword \
unrtf \
pandoc \
docker.io
```

---

# Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Start Ollama:

```bash
ollama serve
```

---

# Pull LLM

```bash
ollama pull qwen2.5:7b-instruct-q4_K_M
```

---

# Clone Project

```bash
git clone <your-repo>

cd APGOVAI
```

---

# Backend Setup

```bash
cd backend

python3 -m venv venv

source venv/bin/activate
```

---

# Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

# requirements.txt

```txt
fastapi
uvicorn
python-dotenv
python-multipart

torch
transformers
sentence-transformers
accelerate
numpy

qdrant-client

markitdown[all]

pymupdf
pdfplumber
pypdf

python-docx
docx2txt

openpyxl
xlrd
pandas

python-pptx

beautifulsoup4
lxml

markdown

pytesseract
pdf2image
pillow

langdetect

requests
httpx

tqdm
orjson

black
ruff
```

---

# Environment Variables

Create:

```text
backend/.env
```

Add:

```env
OLLAMA_MODEL=qwen2.5:7b-instruct-q4_K_M

EMBED_MODEL=intfloat/multilingual-e5-small

DATA_ROOT=./datasets

PROCESSED_ROOT=./processed

QDRANT_HOST=localhost

QDRANT_PORT=6333

TOP_K=8

CHUNK_SIZE=800

CHUNK_OVERLAP=150
```

---

# Start Qdrant

```bash
docker run \
-d \
--name apgovai-qdrant \
-p 6333:6333 \
qdrant/qdrant
```

---

# Dataset Structure

```text
datasets/

├── gos/
├── budgets/
├── reports/
└── datasets/
```

Place government documents inside these folders.

---

# Start Application

From project root:

```bash
chmod +x run.sh

./run.sh
```

---

# Ingestion Pipeline

```text
Document
    ↓
MarkItDown
    ↓
OCR Fallback
    ↓
Markdown
    ↓
Chunking
    ↓
Embeddings
    ↓
Qdrant Storage
```

---

# OCR Support

Scanned PDFs are automatically processed using:

```text
Tesseract OCR
```

Telugu OCR:

```text
eng+tel
```

---

# API Endpoints

## Chat

```http
POST /chat
```

Request:

```json
{
  "question": "ఆరోగ్య శాఖ బడ్జెట్"
}
```

---

# Retrieval Flow

```text
User Query
    ↓
Language Detection
    ↓
Embedding
    ↓
Qdrant Similarity Search
    ↓
Top Documents
    ↓
Prompt Building
    ↓
Qwen Generation
```

---

# Important Engineering Decisions

## Why Removed LangChain

LangChain caused:

* Hidden abstractions
* Slow debugging
* Less control
* Hard optimization

Custom implementation gives:

* Better performance
* Full visibility
* Easier learning
* Production-level understanding

---

# Why Qdrant

Advantages:

* Faster retrieval
* Better filtering
* Native vector database
* Scalable
* Production-ready

---

# Why MarkItDown

Government documents contain:

* Tables
* Mixed formatting
* Broken PDFs
* OCR content

MarkItDown preserves:

* Structure
* Headings
* Tables
* Markdown formatting

better than basic PDF parsers.

---

# Common Problems

---

## Vector Dimension Error

Error:

```text
expected dim: 1024 got 384
```

Cause:

Embedding model changed.

Fix:

Delete Qdrant collection and re-ingest.

---

## 0 Chunks Generated

Cause:

Scanned PDF with no text.

Fix:

OCR fallback automatically handles this.

---

## CUDA Out Of Memory

Cause:

Large models on small GPU.

Fix:

Use:

```text
qwen2.5:7b-instruct-q4_K_M
```

instead of larger models.

---

# Future Improvements

## Planned

* Hybrid Search
* BM25 + Vector Search
* Metadata Filtering
* Department Filtering
* Citation Highlighting
* Telugu OCR Improvements
* Streaming Tokens
* Conversation Memory
* User Authentication
* Multi-document summarization

---

# Production Roadmap

## Current

```text
Single-node local RAG
```

## Future

```text
vLLM
OpenSearch
Distributed Qdrant
GPU batching
Async ingestion
```

---

# Final Notes

This project is now:

* Fully custom
* Multilingual
* OCR-enabled
* Citation-based
* GPU-optimized
* Government-document focused

and designed specifically for Andhra Pradesh Government document intelligence.
