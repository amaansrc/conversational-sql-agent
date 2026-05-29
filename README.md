# 🤖 Conversational SQL Agent

This project is a full-stack application that implements a supervisor/schema/memory system alongside a SQL workflow, validation, retry, and execution pipeline. It provides a conversational interface to query SQL databases using natural language.

## 🏛️ Architecture

The project follows a decoupled client-server architecture:
- **Backend (Azure App Services):** ⚙️ A FastAPI-based service handling routing, memory management, LLM integrations (OpenAI/Groq), SQL generation, validation, and execution. It connects to PostgreSQL and Azure SQL databases.
- **Frontend (Azure Static Web Apps):** 💻 A React frontend built with Vite, providing a conversational chat UI, interactive data tables, and an integrated Monaco SQL editor.

## ✨ Major Functions and Features

- **🗣️ Natural Language to SQL:** Conversational interface that translates user questions into valid SQL queries based on database schemas.
- **🧭 Supervisor Routing & Clarification:** Determines if a query can be executed directly or needs clarification due to ambiguity.
- **🧠 Conversation Memory:** Context-aware memory system to handle follow-up questions effectively.
- **✅ SQL Validation & Retry Mechanism:** Automatic validation of generated SQL, with self-correction retry pipelines to handle errors dynamically.
- **⚡ Query Execution & Explanations:** Executes SQL queries safely using SQLAlchemy and generates natural language explanations for the results.
- **🎨 Interactive UI:** Features a Monaco editor for SQL visualization, responsive data tables, collaborative data exploration, and dynamic 3D backgrounds.

## 📂 Project Structure

### ⚙️ Backend
- `app/main.py` — 🚀 FastAPI application entrypoint and API routes
- `app/services/sql_workflow.py` — 🔄 End-to-end query processing pipeline
- `app/agents/sql_agent/agent.py` — 📝 SQL generation logic
- `app/agents/validation_agent/agent.py` — 🔍 Syntax validation
- `app/agents/retry_agent/agent.py` — 🔁 Retry strategies and error handling
- `app/agents/memory/memory_service.py` — 🗄️ Conversation memory management
- `app/config/settings.py` — 🔧 Environment configuration

### 💻 Frontend
- `src/` — ⚛️ React source code containing components, hooks, and API integration logic
- `vite.config.js` — 🛠️ Vite configuration for the frontend development server

## 📋 Prerequisites

- Node.js 🟢 (for frontend)
- Python 3.8+ 🐍 (for backend)
- Git 🐙

## 🚀 Setup & Running Locally

### 1️⃣ Backend Setup

Navigate to the backend directory, create a virtual environment, and install dependencies:

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

Update `.env` with your API keys and database connection settings. Set `LLM_PROVIDER=openai` (default) or `LLM_PROVIDER=groq`.

Start the backend server using Uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at `http://127.0.0.1:8000`. Health check: `http://127.0.0.1:8000/health`.

### 2️⃣ Frontend Setup

In a new terminal window, navigate to the frontend directory and install dependencies:

```bash
cd frontend
npm install
```

Start the frontend development server:

```bash
npm start
```

Open the local URL provided by Vite in your browser to interact with the application.

## ☁️ Deployment

- **Backend:** 🛠️ Deployed on **Azure App Services** using Gunicorn and Uvicorn workers for production stability.
- **Frontend:** 🌐 Hosted on **Azure Static Web Apps** for fast content delivery.

## 🔌 Query API (Backend Example)

Send requests to `POST /query` with a JSON payload:

```json
{
  "query": "Show top 5 products by list price"
}
```

## 👥 Individual Contributions

### 👨‍💻 Amaan Shahid – Backend Architecture, Conversation Flow, and Deployment
Amaan Shahid contributed extensively to the core backend architecture and conversational intelligence of the project. His responsibilities included project setup, workflow architecture design, schema-aware prompt engineering, clarification dialogue systems, ambiguity handling, conversation memory management, PostgreSQL and Azure SQL database integration, deployment planning, and production deployment setup. He also led major frontend improvements such as the premium UI redesign and animated gradient background integration. Additionally, he implemented Azure cloud deployment planning and production startup configuration using Gunicorn and Uvicorn. His contributions played a significant role in designing the overall system structure, deployment workflow, and user interaction experience.

### 👨‍💻 Tanish Kesarwani – SQL Generation, Validation, and Intelligent Features
Tanish Kesarwani primarily focused on the SQL intelligence and analytical capabilities of the conversational BI assistant. His work included natural language to SQL conversion, SQL validation, retry mechanisms, error handling workflows, query explanation generation, related analysis suggestions, Spider benchmark evaluation, accuracy reporting, query optimization, and explanation pipeline implementation. He also contributed to adding multi-LLM provider support using OpenAI and Groq integration. His contributions strengthened the reliability, accuracy, and intelligence of the system’s query generation and analytical workflows.

### 👨‍💻 Tamil Ks – Frontend Development, APIs, and Collaboration Features
Tamil Ks was mainly responsible for frontend development and user interaction components of the project. His contributions included setting up the React frontend, integrating the Monaco SQL editor, building interactive result table interfaces, developing the conversational chat UI, implementing collaborative data exploration features, creating backend API integrations, and performing end-to-end testing. He also developed separate agent API endpoints for modular testing and debugging. His work ensured smooth frontend usability, API connectivity, and an interactive user experience across the application.
