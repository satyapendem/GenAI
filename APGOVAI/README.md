# APGovAI — Technical Architecture & System Design

**Version:** 1.0
**Status:** Production Foundation Complete
**Stack:** FastAPI + PostgreSQL + Qdrant + Ollama + React

---

# Overview

APGovAI is a Retrieval-Augmented Generation (RAG) platform designed for Andhra Pradesh Government documents.

The system allows authenticated users to query:

* Government Orders (GOs)
* Budgets
* Reports
* Datasets
* Policy Documents
* Circulars
* Future Legislative Documents

using natural language.

The application supports:

* Multi-user authentication
* Conversation history
* Context-aware chat
* Vector search
* Response caching
* Admin user management
* Document management
* Incremental ingestion

---

# High Level Architecture

```text
┌───────────────────────┐
│ React Frontend        │
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│ FastAPI Backend       │
└──────────┬────────────┘
           │
           ├──────────────────────┐
           │                      │
           ▼                      ▼

┌─────────────────┐      ┌─────────────────┐
│ PostgreSQL      │      │ Qdrant          │
│ Metadata Store  │      │ Vector Store    │
└─────────────────┘      └─────────────────┘
           ▲                      ▲
           │                      │
           └──────────┬───────────┘
                      │
                      ▼

             ┌────────────────┐
             │ Ollama         │
             │ Qwen2.5 7B     │
             └────────────────┘
```

---

# Frontend Architecture

```text
src/

├── components
│   ├── ChatInput.jsx
│   ├── ChatWindow.jsx
│   ├── MessageBubble.jsx
│   └── Sidebar.jsx
│
├── pages
│   ├── Login.jsx
│   ├── Users.jsx
│   └── Documents.jsx
│
├── api
│   ├── auth.js
│   ├── conversations.js
│   ├── documents.js
│   └── users.js
│
├── assets
│
├── styles.css
│
└── App.jsx
```

---

# Backend Architecture

```text
app/

├── api
│   ├── auth.py
│   ├── admin.py
│   ├── users.py
│   ├── chat.py
│   ├── conversations.py
│   └── documents.py
│
├── database
│   ├── models.py
│   ├── schemas.py
│   ├── session.py
│   ├── bootstrap.py
│   └── init_db.py
│
├── services
│   ├── auth_service.py
│   ├── security.py
│   ├── conversation_service.py
│   ├── cache_service.py
│   └── document_service.py
│
├── retrieval
│   └── retriever.py
│
├── vector
│   └── qdrant_client.py
│
├── embedding
│   └── embedder.py
│
├── llm
│   └── ollama_client.py
│
├── ingestion
│   ├── ingest.py
│   ├── converter.py
│   ├── chunker.py
│   ├── manifest.py
│   └── run_ingest.py
│
└── main.py
```

---

# Authentication Flow

Implemented using JWT.

## Login

```text
User
 ↓
POST /auth/login
 ↓
Validate Username/Password
 ↓
Generate JWT
 ↓
Return Token
```

Frontend stores:

```javascript
localStorage.setItem(
  "token",
  token
)
```

Every API call sends:

```http
Authorization: Bearer <token>
```

---

# User Roles

## Admin

Can:

* Create Users
* View Users
* Upload Documents
* Delete Documents
* Re-ingest Documents
* View Chats

## User

Can:

* Login
* Create Chats
* Ask Questions
* View Own History

Cannot:

* Manage Users
* Manage Documents

---

# PostgreSQL Architecture

Database acts as system-of-record.

---

## Users

```text
users
```

Stores:

```text
id
username
password_hash
role
is_active
created_at
```

---

## Conversations

```text
conversations
```

Stores:

```text
id
user_id
title
created_at
```

---

## Messages

```text
messages
```

Stores:

```text
id
conversation_id
role
content
created_at
```

Roles:

```text
user
assistant
```

---

## Documents

```text
documents
```

Stores:

```text
id
filename
file_hash
collection
file_path
status
uploaded_by
created_at
```

---

## Response Cache

```text
response_cache
```

Stores:

```text
question_hash
question
answer
created_at
```

---

## Audit Logs

```text
audit_logs
```

Stores:

```text
user_id
action
created_at
```

---

# Conversation Memory

Implemented.

Each conversation has:

```text
Conversation
 ├── User Message
 ├── Assistant Response
 ├── User Message
 ├── Assistant Response
```

When user asks:

```text
"What was the budget increase?"
```

System loads:

```python
history = get_conversation_context(
    db,
    conversation_id
)
```

and injects history into prompt.

Result:

```text
Conversation-aware responses
```

similar to ChatGPT.

---

# Retrieval Pipeline

Current Retrieval:

```text
Question
 ↓
Embed Query
 ↓
Qdrant Search
 ↓
Top K Chunks
 ↓
Prompt Builder
 ↓
LLM
```

---

# Embeddings

Model:

```text
intfloat/multilingual-e5-small
```

Query:

```text
query: <question>
```

Document:

```text
passage: <chunk>
```

Normalization:

```python
normalize_embeddings=True
```

Supports:

* Telugu
* English
* Multilingual Retrieval

---

# Chunking Strategy

Custom semantic chunker.

Features:

### Sentence Aware

Avoids:

```text
mid sentence splits
```

### Telugu Safe

Avoids:

```text
Unicode grapheme corruption
```

### Overlapping Chunks

```text
chunk_size = 1500
overlap = 200
```

---

# Qdrant Architecture

Collections:

```text
gos
budgets
reports
datasets
```

Each collection:

```text
text
embedding
metadata
```

Metadata:

```json
{
  "source": "...",
  "department": "...",
  "year": "...",
  "document_type": "...",
  "chunk_index": 1
}
```

---

# Duplicate Prevention

Implemented at two layers.

---

## Ingestion Layer

Manifest

```text
processed/manifest.json
```

Stores:

```text
file hash
```

Unchanged files skipped.

---

## Database Layer

Documents table

```text
file_hash UNIQUE
```

Same file uploaded:

```text
Rejected
```

---

# Document Management

Admin can:

```text
Upload
Delete
List
Re-Ingest
```

Upload Flow:

```text
Upload File
 ↓
Calculate Hash
 ↓
Check PostgreSQL
 ↓
Store File
 ↓
Chunk
 ↓
Embed
 ↓
Qdrant
 ↓
Metadata Save
```

---

# Response Cache

Implemented.

Flow:

```text
Question
 ↓
Hash Question
 ↓
Cache Lookup
```

If hit:

```text
Return Cached Response
```

If miss:

```text
Generate Response
 ↓
Store Cache
```

Benefits:

```text
10x Faster Repeated Queries
Reduced LLM Load
```

---

# Ollama Layer

Current Model:

```text
qwen2.5:7b-instruct-q4_K_M
```

Generation:

```python
temperature = 0.1
repeat_penalty = 1.1
```

Streaming:

```text
Token Streaming
```

Frontend receives chunks live.

---

# Current API Endpoints

## Authentication

```http
POST /auth/login
```

---

## User Management

```http
POST /admin/users
GET /users/me
GET /users
```

---

## Conversations

```http
POST /conversations
GET /conversations
GET /conversations/{id}/messages
DELETE /conversations/{id}
```

---

## Chat

```http
POST /chat
```

Streaming response.

---

## Documents

```http
POST /documents/upload
GET /documents
DELETE /documents/{id}
```

---

# Docker Architecture

```yaml
services:

  postgres

  qdrant

  backend

  frontend
```

---

# Environment Variables

```env
OLLAMA_MODEL=qwen2.5:7b-instruct-q4_K_M

OLLAMA_HOST=http://localhost:11434

EMBED_MODEL=intfloat/multilingual-e5-small

QDRANT_HOST=qdrant
QDRANT_PORT=6333

POSTGRES_HOST=postgres
POSTGRES_PORT=5432

POSTGRES_DB=apgovai
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

JWT_SECRET=<secret>

TOP_K=8
RERANK_TOP=3

CHUNK_SIZE=1500
CHUNK_OVERLAP=200
```

---

# Current Production Readiness

### Completed

✅ Authentication

✅ Authorization

✅ User Management

✅ Conversation Memory

✅ PostgreSQL Persistence

✅ Document Management

✅ Duplicate Prevention

✅ Qdrant Vector Search

✅ Response Cache

✅ Docker Deployment

✅ Incremental Ingestion

✅ Streaming Responses

---

# Planned Next Phase

## Phase 2

### Hybrid Search

```text
BM25
+
Vector Search
+
Reranker
```

---

### Source Citations

```text
Answer
 ↓
Sources
   GO_42.pdf
   Budget_2024.xlsx
```

---

### Analytics Dashboard

```text
Total Users
Total Documents
Total Chats
Cache Hit Rate
```

---

### Feedback System

```text
👍 Helpful

👎 Not Helpful
```

---

### Audit Dashboard

```text
User Login
Document Upload
Document Delete
Admin Actions
```

---

# Vision

APGovAI is evolving into a Government Knowledge Platform capable of:

* Enterprise RAG
* Multilingual Retrieval
* Department Knowledge Management
* Policy Search
* Budget Intelligence
* Government Decision Support

with complete ownership of data and models running entirely on local infrastructure.
