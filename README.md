# Anki-KI

Foliensätze (PDF) aus Google Drive → per LLM generierte Lernkarten → Web-App zum Reviewen,
Durchsuchen und Lernen (Spaced Repetition), inkl. Qualitätsmessung gegen ein Gold-Set.

> In Arbeit. Architektur und Entscheidungen: siehe [CLAUDE.md](CLAUDE.md).

## Stack

| Teil     | Technik                                        |
|----------|------------------------------------------------|
| Frontend | React, Vite, TypeScript                        |
| Backend  | FastAPI (Python), SQLAlchemy 2, Alembic        |
| DB       | PostgreSQL + pgvector                          |
| Queue    | Procrastinate (Postgres-basiert)               |

## Lokal starten

Voraussetzungen: Docker, [uv](https://docs.astral.sh/uv/), Node.js

```bash
# Datenbank
docker compose up -d

# Backend (http://localhost:8000, API-Doku unter /docs)
cd backend
cp .env.example .env
uv run alembic upgrade head
uv run uvicorn backend.main:app --reload

# Frontend (http://localhost:5173)
cd frontend
npm install
npm run dev
```

## Tests

```bash
cd backend && uv run pytest && uv run ruff check
cd frontend && npm run lint && npm run build
```
