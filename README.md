# AskDocs (RAG Knowledge Base API)

AskDocs is a production-ready RAG (Retrieval-Augmented Generation) backend API built with FastAPI, PostgreSQL (pgvector), Redis, and Celery.

## Features
- **Authentication**: JWT-based login/registration.
- **Document Management**: Upload PDF/TXT/MD files.
- **Async Ingestion**: Background tasks for text extraction, chunking, and embedding.
- **RAG Chat**: Semantic search + LLM generation with user isolation.
- **Streaming**: Server-Sent Events (SSE) for chat responses.
- **Ops**: Rate limiting, Structured Logging, Docker Compose.

## Architecture
```
[Client] -> [Load Balancer/API] -> [Postgres (Pgvector)]
                                -> [Redis (Queue/Cache)] -> [Worker]
```

## Setup & Running

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (optional, if running locally without Docker)

### Quick Start (Docker)
1. Clone the repo.
2. `cp .env.example .env`
3. `make up` (Starts DB, Redis, API, Worker)
4. Visit `http://localhost:8000/docs`

### Local Development
1. `cp .env.example .env`
2. `docker-compose up -d db redis` (Start backing services)
3. `pip install -r requirements.txt`
4. `alembic upgrade head` (Run migrations)
5. `make dev` (Start API)
6. `make worker` (Start Worker in another terminal)

## API Usage Example

1. **Register**: `POST /auth/register`
2. **Login**: `POST /auth/login` -> Get Token
3. **Upload**: `POST /docs/upload` (Multipart)
4. **Chat**: `POST /chat/` or `GET /chat/stream`

## Testing
`make test`
