from typing import Dict, List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

from app.agents.memory.memory_service import MemoryService
from app.agents.supervisor.clarifier import ClarifierAgent
from app.agents.supervisor.supervisor_agent import SupervisorAgent
from app.agents.supervisor.supervisor_models import RouteType
from app.services.sql_workflow import SQLWorkflow

app = FastAPI(
    title="Conversational SQL Agent",
    description="Merged Amaan and Tanish backend workflow for conversational SQL generation and execution.",
)

memory_service = MemoryService()
supervisor_agent = SupervisorAgent()
clarifier_agent = ClarifierAgent()
workflow = SQLWorkflow()


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    success: bool
    route: str
    reason: Optional[str] = None
    clarification: Optional[str] = None
    sql: Optional[str] = None
    results: Optional[List[Dict[str, object]]] = None
    error: Optional[str] = None
    retry_strategy: Optional[str] = None


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def process_query(request: QueryRequest):
    clarification = clarifier_agent.analyze(request.query)
    if clarification.needs_clarification:
        return QueryResponse(
            success=False,
            route=RouteType.CLARIFY.value,
            reason="Ambiguous intent detected",
            clarification=clarification.question,
            sql=None,
            results=None,
            error=None,
            retry_strategy=None,
        )

    decision = supervisor_agent.route(request.query)
    query_input = request.query
    if decision.route == RouteType.MEMORY:
        context = memory_service.get_context()
        if context.last_query:
            query_input = (
                f"Previous query: {context.last_query}. "
                f"Use it as context for: {request.query}"
            )

    result = workflow.process_query(query_input)

    if result["success"]:
        memory_service.update(request.query)

    return QueryResponse(
        success=result["success"],
        route=decision.route.value,
        reason=decision.reason,
        clarification=None,
        sql=result.get("sql"),
        results=result.get("results"),
        error=result.get("error"),
        retry_strategy=result.get("retry_strategy"),
    )
