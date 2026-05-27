# Conversational SQL Agent

This project is a full-stack application that merges Amaan's supervisor/schema/memory work with Tanish's SQL workflow, validation, retry, and execution pipeline. It provides a conversational interface to query SQL databases using natural language.

## Project Structure

- `backend/`: FastAPI backend containing the supervisor routing, memory service, SQL generation, validation, and execution pipeline.
- `frontend/`: React frontend built with Vite, providing the conversational UI.

## What is included (Backend)

- FastAPI backend entrypoint at `backend/app/main.py`
- Supervisor routing and clarification logic
- Conversation memory service
- SQL generation via LLM with schema context
- SQL validation using `sqlparse`
- Retry strategies for failed SQL generation/execution
- Query execution with SQLAlchemy
- Centralized config using `.env`

## What is included (Frontend)

- React built with Vite for fast development
- Interactive conversational interface
- Monaco editor integration for SQL query visualization
- Lucide React for iconography

## Prerequisites

- Node.js (for frontend)
- Python 3.8+ (for backend)
- Git

## Setup & Running Locally

### 1. Backend Setup

First, navigate to the backend directory, create a virtual environment, and install the dependencies:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy the sample environment file:

```bash
cp .env.example .env
```

Update `.env` with your API key and DB settings.

Start the backend server with Uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at `http://127.0.0.1:8000`. You can access the health check at `http://127.0.0.1:8000/health`.

### 2. Frontend Setup

In a new terminal window, navigate to the frontend directory and install dependencies:

```bash
cd frontend
npm install
```

Start the frontend development server:

```bash
npm start
```

The frontend will run on the port provided by Vite (usually `http://localhost:5173`). Open this URL in your browser to interact with the application.

## Query API (Backend)

Send requests to `POST /query` with JSON payload:

```json
{
  "query": "Show top 5 products by list price"
}
```

## Notes

- The default database is `AdventureWorksLT.db`.
- LLM provider defaults to `openai`.
- Use `LLM_PROVIDER=groq` in the backend `.env` if you want Groq instead.

## Files of interest

### Backend
- `app/main.py` — FastAPI endpoints
- `app/services/sql_workflow.py` — end-to-end query pipeline
- `app/agents/sql_agent/agent.py` — SQL generation logic
- `app/agents/validation_agent/agent.py` — syntax validation
- `app/agents/retry_agent/agent.py` — retry strategies
- `app/agents/memory/memory_service.py` — conversation memory
- `app/config/settings.py` — environment configuration

### Frontend
- `src/` — React source code components and application logic
- `vite.config.js` — Vite configuration for the development server
