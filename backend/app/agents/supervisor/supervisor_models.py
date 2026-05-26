from enum import Enum
from pydantic import BaseModel
from typing import Optional, Dict, Any


class RouteType(str, Enum):
    CLARIFY = "clarify"
    SCHEMA = "schema"
    MEMORY = "memory"
    SQL = "sql"


class SupervisorDecision(BaseModel):
    route: RouteType
    reason: str
    payload: Optional[Dict[str, Any]] = None