# APGovAI

APGovAI is a multilingual retrieval-augmented generation system for Andhra Pradesh government documents. It provides authenticated chat, document ingestion, vector search, admin controls, and language-aware responses in English and Telugu.

## What It Does

- Answers questions from retrieved government documents
- Streams responses from the backend to the UI
- Preserves conversation history per chat thread
- Supports English and Telugu user interfaces
- Switches model output language based on the selected UI language
- Lets admins manage users and documents

## Architecture

```text
Browser / React UI
  -> FastAPI API
    -> Authentication, conversations, users, documents
    -> Chat orchestration
      -> Retrieval from Qdrant
      -> Prompt assembly
      -> Ollama LLM streaming
    -> PostgreSQL for system of record
    -> Qdrant for vector search
    -> Local document ingestion pipeline
```

## Request Flow

1. User selects a language in the UI.
2. The frontend loads the available languages from `GET /chat/languages`.
3. The selected language is persisted in `localStorage`.
4. Chat requests send the language code to `POST /chat`.
5. The backend resolves the requested language and builds a language-specific prompt.
6. Retrieved context is inserted into the prompt.
7. Ollama streams the answer back to the frontend.
8. The assistant message is stored in the conversation history.

## Telugu Support

Telugu support is implemented in both layers:

- Frontend translations live in `frontend/src/i18n.js`
- The language selector uses backend-provided options from `GET /chat/languages`
- Backend language helpers are in `backend/app/utils/language.py`
- Telugu-specific prompt instructions are in `backend/app/utils/prompt_builder.py`

When the user selects Telugu, the chat request uses `te`, and the backend instructs the model to answer in Telugu while preserving official values, numbers, file names, and GO references exactly.

## Repository Layout

### Frontend

- `frontend/src/App.jsx` - main application state and page routing
- `frontend/src/api.js` - chat API helpers
- `frontend/src/components/` - reusable UI components
- `frontend/src/pages/` - login, users, and documents pages
- `frontend/src/i18n.js` - UI translation strings
- `frontend/src/styles.css` - application styling

### Backend

- `backend/app/api/` - HTTP routes
- `backend/app/services/` - auth, conversations, security, and document services
- `backend/app/utils/` - language and prompt utilities
- `backend/app/retrieval/` - retrieval and reranking logic
- `backend/app/embedding/` - embedding model setup
- `backend/app/ingestion/` - file conversion, chunking, and ingest pipeline
- `backend/app/llm/` - Ollama streaming client
- `backend/app/database/` - models, schemas, session, and bootstrap code

## Key Backend Endpoints

### Authentication

- `POST /auth/login`

### Chat

- `GET /chat/languages`
- `POST /chat`

### Conversations

- `POST /conversations`
- `GET /conversations`
- `GET /conversations/{id}/messages`
- `DELETE /conversations/{id}`

### Users

- `GET /users/me`
- `GET /users`
- `POST /admin/users`

### Documents

- `GET /documents`
- `POST /documents/upload`
- `DELETE /documents/{id}`

## Data Stores

- PostgreSQL stores users, conversations, messages, documents, audit data, and cached responses
- Qdrant stores chunk embeddings and metadata for retrieval

## Language Rules

- English and Telugu are supported response languages
- The backend detects language only when the client sends `auto`
- Telugu queries and Telugu-selected chats should produce Telugu answers
- Official values should remain unchanged unless the source text explicitly differs

## Development Notes

- The frontend is a Vite React app
- The backend is a FastAPI app
- Responses are streamed from the backend as plain text
- `react-markdown` renders assistant responses in the chat window
- The app is designed to work with local services for the API, PostgreSQL, Qdrant, and Ollama

## Local Setup

### Frontend

```bash
cd frontend
npm install
npm run build
```

### Backend

Create a virtual environment, install `backend/requirements.txt`, then run FastAPI with your preferred ASGI server.

## Environment Variables

Typical backend variables include:

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

## Notes On Quality

- Telugu strings are stored as real Unicode text, not transliterated placeholders
- The frontend language selector now falls back to bundled options if the backend language endpoint is unavailable
- Backend compile and frontend production build should both pass before release

