from app.agents.sql_agent.agent import SQLAgent


class RetryAgent:

    def __init__(self):
        self.sql_agent = SQLAgent()

    def retry(self, user_query: str, previous_sql: str, error_message: str):
        try:
            cleaned_sql = previous_sql.strip()
            if cleaned_sql.endswith(";"):
                cleaned_sql = cleaned_sql[:-1]
            return {
                "success": True,
                "strategy": "Formatting Fix",
                "sql": cleaned_sql
            }
        except Exception:
            pass

        try:
            regenerated_sql = self.sql_agent.generate_sql(user_query)
            return {
                "success": True,
                "strategy": "Regenerated SQL",
                "sql": regenerated_sql
            }
        except Exception:
            pass

        try:
            simplified_prompt = f"Generate a simple SQL query for: {user_query}"
            simplified_sql = self.sql_agent.generate_sql(simplified_prompt)
            return {
                "success": True,
                "strategy": "Simplified Query",
                "sql": simplified_sql
            }
        except Exception as e:
            return {
                "success": False,
                "strategy": None,
                "sql": None,
                "error": str(e)
            }
