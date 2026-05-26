from app.services.llm_service import LLMService
import json


class ExplanationAgent:

    def __init__(self):
        self.llm = LLMService.get_llm()


    def explain(
        self,
        user_query: str,
        sql: str,
        results: list
    ):

        sample_results = results[:5]

        prompt = f"""
You are a Business Intelligence analyst.

Use ONLY the information given.

User Query:
{user_query}

Generated SQL:
{sql}

Results:
{json.dumps(sample_results, indent=2)}

Return STRICT JSON only:

{{
    "query_explanation":"...",
    "summary":"...",
    "insights":[
        "...",
        "...",
        "..."
    ]
}}

Rules:
- No markdown
- No assumptions
- No extra text
- Insights must be directly supported by data
"""

        response = self.llm.invoke(prompt)

        cleaned = (
            response.content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        return json.loads(cleaned)