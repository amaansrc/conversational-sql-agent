from app.agents.schema.schema_extractor import SchemaExtractor
from app.agents.schema.schema_service import SchemaService
from app.db.database import engine
from app.services.llm_service import LLMService


class SQLAgent:

    def __init__(self):
        self.llm = LLMService.get_llm()
        self.schema_service = SchemaService(
            extractor=SchemaExtractor(engine)
        )

    def _build_schema_context(self, user_query: str) -> str:
        relevant_schema = self.schema_service.get_relevant_schema(user_query)

        if not relevant_schema:
            schema = self.schema_service.extractor.extract_schema()
            relevant_schema = {
                table.table_name: table.columns
                for table in schema.tables
            }

        schema_text = ""
        for table, columns in relevant_schema.items():
            schema_text += f"\nTable: {table}\nColumns: {', '.join(columns)}\n"

        return schema_text.strip()

    def _clean_sql_response(self, sql: str) -> str:
        sql = sql.strip()
        sql = sql.replace("```sql", "")
        sql = sql.replace("```", "")
        return sql.strip()

    def generate_sql(self, user_query: str) -> str:
        schema_context = self._build_schema_context(user_query)

        prompt = f"""
You are an expert SQL generator.

Database Schema:

{schema_context}

Rules:
1. Return ONLY SQL
2. Do not explain anything
3. Do not use markdown
4. Use SQLite syntax only
5. Use only provided tables and columns
6. Generate executable SQL

Question:
{user_query}

SQL:
"""

        try:
            response = self.llm.invoke(prompt)
            generated_sql = self._clean_sql_response(response.content)
            return generated_sql
        except Exception as e:
            raise Exception(f"SQL generation failed: {str(e)}")
