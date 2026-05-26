from app.agents.sql_agent.agent import SQLAgent
from app.agents.validation_agent.agent import ValidationAgent
from app.agents.retry_agent.agent import RetryAgent
from app.services.query_executor import QueryExecutor


class SQLWorkflow:

    def __init__(self):
        self.sql_agent = SQLAgent()
        self.validation_agent = ValidationAgent()
        self.retry_agent = RetryAgent()

    def process_query(self, user_query: str):
        try:
            generated_sql = self.sql_agent.generate_sql(user_query)
            validation = self.validation_agent.validate(generated_sql)

            retry_strategy = None
            if not validation["valid"]:
                retry_result = self.retry_agent.retry(
                    user_query=user_query,
                    previous_sql=generated_sql,
                    error_message=validation["error"]
                )
                generated_sql = retry_result["sql"]
                retry_strategy = retry_result.get("strategy")

            execution_result = QueryExecutor.execute(generated_sql)

            if not execution_result["success"]:
                retry_result = self.retry_agent.retry(
                    user_query=user_query,
                    previous_sql=generated_sql,
                    error_message=execution_result["error"]
                )
                if retry_result["success"] and retry_result["sql"]:
                    generated_sql = retry_result["sql"]
                    execution_result = QueryExecutor.execute(generated_sql)
                    retry_strategy = retry_result.get("strategy")

            return {
                "success": execution_result["success"],
                "sql": generated_sql,
                "results": execution_result["data"],
                "error": execution_result["error"],
                "retry_strategy": retry_strategy
            }

        except Exception as e:
            return {
                "success": False,
                "sql": None,
                "results": None,
                "error": str(e),
                "retry_strategy": None
            }
