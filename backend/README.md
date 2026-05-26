# Conversational SQL Agent Backend

This backend merges Amaan's supervisor/schema/memory work with Tanish's SQL workflow, validation, retry, and execution pipeline.

## What is included

- FastAPI backend entrypoint at `backend/app/main.py`
- Supervisor routing and clarification logic
- Conversation memory service
- SQL generation via LLM with schema context
- SQL validation using `sqlparse`
- Retry strategies for failed SQL generation/execution
- Query execution with SQLAlchemy
- Centralized config using `.env`

## Setup

1. Create a virtual environment and install dependencies:

```bash
cd "Capstone Project 2/backend"
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Copy the sample environment file:

```bash
cp .env.example .env
```

3. Update `.env` with your API key and DB settings.

## Running the backend

Start the server with Uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then access the health check:

```bash
curl http://127.0.0.1:8000/health
```

## Query API

Send requests to `POST /query` with JSON payload:

```json
{
  "query": "Show top 5 products by list price"
}
```

## Notes

- The default database is `AdventureWorksLT.db`.
- LLM provider defaults to `openai`.
- Use `LLM_PROVIDER=groq` in `.env` if you want Groq instead.

## Files of interest

- `app/main.py` — FastAPI endpoints
- `app/services/sql_workflow.py` — end-to-end query pipeline
- `app/agents/sql_agent/agent.py` — SQL generation logic
- `app/agents/validation_agent/agent.py` — syntax validation
- `app/agents/retry_agent/agent.py` — retry strategies
- `app/agents/memory/memory_service.py` — conversation memory
- `app/config/settings.py` — environment configuration
