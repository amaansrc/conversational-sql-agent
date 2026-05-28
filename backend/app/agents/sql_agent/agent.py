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


    def _build_schema_context(
        self,
        user_query: str
    ) -> str:

        relevant_schema = (
            self.schema_service.get_relevant_schema(
                user_query
            )
        )

        if not relevant_schema:

            schema = (
                self.schema_service.extractor.extract_schema()
            )

            relevant_schema = {

                table.table_name: table.columns

                for table in schema.tables
            }

        schema_text = ""

        for table, columns in relevant_schema.items():

            schema_text += (

                f"\nTable: {table}\n"
                f"Columns: {', '.join(columns)}\n"

            )

        return schema_text.strip()


    def _clean_sql_response(
        self,
        sql: str
    ) -> str:

        sql = sql.strip()

        sql = sql.replace(
            "```sql",
            ""
        )

        sql = sql.replace(
            "```",
            ""
        )

        sql = sql.replace(
            "`",
            ""
        )

        return sql.strip()


    def generate_sql(
        self,
        user_query: str
    ) -> str:

        schema_context = (
            self._build_schema_context(
                user_query
            )
        )

        prompt = f"""
You are an expert SQL generator for a Business Intelligence assistant.

Database Schema:

{schema_context}

STRICT RULES:

1. Return ONLY executable SQL
2. Return NO explanations
3. Return NO markdown
4. Use T-SQL (SQL Server) syntax only
5. Use ONLY tables and columns present in schema
6. Follow user intent exactly
7. Never ignore important words
8. Generate executable SQL only
9. Do NOT wrap column or table names in square brackets unless they contain spaces or are reserved words
10. Use TOP N instead of LIMIT N
11. ALWAYS use schema-qualified table names with the dot OUTSIDE brackets. Correct: [SalesLT].[Customer]. WRONG: [SalesLT.Customer]. Each identifier part must be bracketed separately.

Intent Rules:

- highest / top / maximum → use ORDER BY DESC
- lowest / minimum → use ORDER BY ASC
- price / pricing / cost / value → prioritize ListPrice
- top N → use SELECT TOP N

Examples:

Question:
Show top 5 products by list price

SQL:
SELECT TOP 5 ProductID, Name, ListPrice
FROM [SalesLT].[Product]
ORDER BY ListPrice DESC

Question:
Find customers

SQL:
SELECT CustomerID, FirstName, LastName
FROM [SalesLT].[Customer]

Question:
Top 5 customers by total sales

SQL:
SELECT TOP 5 C.CustomerID, C.FirstName, C.LastName, SUM(SOH.TotalDue) AS TotalSales
FROM [SalesLT].[Customer] C
INNER JOIN [SalesLT].[SalesOrderHeader] SOH ON C.CustomerID = SOH.CustomerID
GROUP BY C.CustomerID, C.FirstName, C.LastName
ORDER BY TotalSales DESC

Question:
{user_query}

SQL:
"""

        try:

            response = self.llm.invoke(
                prompt
            )

            generated_sql = (

                self._clean_sql_response(
                    response.content
                )

            )

            return generated_sql

        except Exception as e:

            raise Exception(
                f"SQL generation failed: {str(e)}"
            )