from sqlalchemy import text

from app.db.database import engine


class QueryExecutor:

    @staticmethod
    def execute(sql: str):
        try:
            with engine.connect() as connection:
                result = connection.execute(text(sql))
                rows = result.fetchall()
                columns = result.keys()

                data = [
                    dict(zip(columns, row))
                    for row in rows
                ]

                return {
                    "success": True,
                    "data": data,
                    "error": None
                }

        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }
