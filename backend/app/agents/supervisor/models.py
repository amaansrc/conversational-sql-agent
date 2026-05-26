from pydantic import BaseModel
from typing import Optional


class ClarificationResult(BaseModel):
    needs_clarification: bool
    ambiguity_type: Optional[str] = None
    question: Optional[str] = None