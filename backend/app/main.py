from typing import Dict, List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

from app.agents.explanation_agent.agent import ExplanationAgent
from app.agents.memory.memory_service import MemoryService
from app.agents.retry_agent.agent import RetryAgent
from app.agents.sql_agent.agent import SQLAgent
from app.agents.supervisor.clarifier import ClarifierAgent
from app.agents.supervisor.supervisor_agent import SupervisorAgent
from app.agents.supervisor.supervisor_models import RouteType
from app.agents.validation_agent.agent import ValidationAgent
from app.services.sql_workflow import SQLWorkflow

app = FastAPI(
    title="Conversational SQL Agent",
    description="Backend workflow for conversational SQL generation and execution.",
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

memory_service = MemoryService()
supervisor_agent = SupervisorAgent()
clarifier_agent = ClarifierAgent()
sql_agent = SQLAgent()
validation_agent = ValidationAgent()
retry_agent = RetryAgent()
explanation_agent = ExplanationAgent()
workflow = SQLWorkflow()


# ---------------------------------------------------------------------------
# Shared request/response models
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Agent-specific request/response models
# ---------------------------------------------------------------------------

class ClarifyResponse(BaseModel):
    needs_clarification: bool
    ambiguity_type: Optional[str] = None
    question: Optional[str] = None


class RouteResponse(BaseModel):
    route: str
    reason: str


class GenerateSQLResponse(BaseModel):
    success: bool
    sql: Optional[str] = None
    error: Optional[str] = None


class ValidateSQLRequest(BaseModel):
    sql: str


class ValidateSQLResponse(BaseModel):
    valid: bool
    error: Optional[str] = None


class RetryRequest(BaseModel):
    query: str
    previous_sql: str
    error_message: str


class RetryResponse(BaseModel):
    success: bool
    strategy: Optional[str] = None
    sql: Optional[str] = None
    error: Optional[str] = None


class ExplainQueryResponse(BaseModel):
    success: bool
    route: str
    reason: Optional[str] = None
    clarification: Optional[str] = None
    sql: Optional[str] = None
    results: Optional[List[Dict[str, object]]] = None
    query_explanation: Optional[str] = None
    summary: Optional[str] = None
    insights: Optional[List[str]] = None
    error: Optional[str] = None
    retry_strategy: Optional[str] = None


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health")
def health_check():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Main query pipeline
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Agent endpoints
# ---------------------------------------------------------------------------

@app.post("/agent/clarify", response_model=ClarifyResponse)
def agent_clarify(request: QueryRequest):
    """
    Run only the ClarifierAgent on the given query.
    Returns whether the query is ambiguous, the ambiguity type, and
    the clarifying question to show the user (if any).
    """
    result = clarifier_agent.analyze(request.query)
    return ClarifyResponse(
        needs_clarification=result.needs_clarification,
        ambiguity_type=result.ambiguity_type,
        question=result.question,
    )


@app.post("/agent/route", response_model=RouteResponse)
def agent_route(request: QueryRequest):
    """
    Run only the SupervisorAgent on the given query.
    Returns the routing decision (schema / memory / clarify) and the reason.
    """
    decision = supervisor_agent.route(request.query)
    return RouteResponse(
        route=decision.route.value,
        reason=decision.reason,
    )


@app.post("/agent/generate-sql", response_model=GenerateSQLResponse)
def agent_generate_sql(request: QueryRequest):
    """
    Run only the SQLAgent — generates SQL from the natural language query
    using schema context + LLM. Does NOT execute the SQL.
    """
    try:
        sql = sql_agent.generate_sql(request.query)
        return GenerateSQLResponse(success=True, sql=sql)
    except Exception as e:
        return GenerateSQLResponse(success=False, error=str(e))


@app.post("/agent/validate-sql", response_model=ValidateSQLResponse)
def agent_validate_sql(request: ValidateSQLRequest):
    """
    Run only the ValidationAgent on a raw SQL string.
    Checks syntax and ensures only SELECT statements are allowed.
    """
    result = validation_agent.validate(request.sql)
    return ValidateSQLResponse(
        valid=result["valid"],
        error=result.get("error"),
    )


@app.post("/agent/retry", response_model=RetryResponse)
def agent_retry(request: RetryRequest):
    """
    Run only the RetryAgent. Pass in the original query, the failed SQL,
    and the error message. Returns the recovered SQL and the strategy used
    (Formatting Fix / Regenerated SQL / Simplified Query).
    """
    result = retry_agent.retry(
        user_query=request.query,
        previous_sql=request.previous_sql,
        error_message=request.error_message,
    )
    return RetryResponse(
        success=result["success"],
        strategy=result.get("strategy"),
        sql=result.get("sql"),
        error=result.get("error"),
    )


# ---------------------------------------------------------------------------
# Explained query pipeline
# ---------------------------------------------------------------------------

@app.post("/query/explain", response_model=ExplainQueryResponse)
def explain_query(request: QueryRequest):
    """
    Full pipeline: NL query → SQL generation → execution → plain English explanation.

    Steps:
      1. ClarifierAgent   — returns a question if the query is ambiguous
      2. SupervisorAgent  — decides route (schema / memory)
      3. SQLWorkflow      — generates, validates, retries, and executes the SQL
      4. ExplanationAgent — explains the results as query_explanation, summary, insights
    """
    # Step 1 — Clarify
    clarification = clarifier_agent.analyze(request.query)
    if clarification.needs_clarification:
        return ExplainQueryResponse(
            success=False,
            route=RouteType.CLARIFY.value,
            reason="Ambiguous intent detected",
            clarification=clarification.question,
        )

    # Step 2 — Route
    decision = supervisor_agent.route(request.query)
    query_input = request.query
    if decision.route == RouteType.MEMORY:
        context = memory_service.get_context()
        if context.last_query:
            query_input = (
                f"Previous query: {context.last_query}. "
                f"Use it as context for: {request.query}"
            )

    # Step 3 — Generate SQL → Execute
    result = workflow.process_query(query_input)

    if not result["success"]:
        return ExplainQueryResponse(
            success=False,
            route=decision.route.value,
            reason=decision.reason,
            sql=result.get("sql"),
            error=result.get("error"),
            retry_strategy=result.get("retry_strategy"),
        )

    memory_service.update(request.query)

    # Step 4 — Explain results in plain English
    try:
        explanation = explanation_agent.explain(
            user_query=request.query,
            sql=result["sql"],
            results=result["results"],
        )
    except Exception as e:
        # SQL + results are still returned even if explanation fails
        return ExplainQueryResponse(
            success=True,
            route=decision.route.value,
            reason=decision.reason,
            sql=result["sql"],
            results=result["results"],
            retry_strategy=result.get("retry_strategy"),
            error=f"Explanation failed: {str(e)}",
        )

    return ExplainQueryResponse(
        success=True,
        route=decision.route.value,
        reason=decision.reason,
        sql=result["sql"],
        results=result["results"],
        query_explanation=explanation.get("query_explanation"),
        summary=explanation.get("summary"),
        insights=explanation.get("insights"),
        retry_strategy=result.get("retry_strategy"),
    )