import sqlparse
from sqlparse.tokens import DML


class ValidationAgent:

    @staticmethod
    def validate(sql: str):
        try:
            sql = sql.strip()

            if not sql:
                return {
                    "valid": False,
                    "error": "Empty SQL query"
                }

            parsed = sqlparse.parse(sql)
            if not parsed:
                return {
                    "valid": False,
                    "error": "Unable to parse SQL"
                }

            statement = parsed[0]
            found_select = False

            for token in statement.tokens:
                if token.ttype is DML and token.value.upper() == "SELECT":
                    found_select = True

            if not found_select:
                return {
                    "valid": False,
                    "error": "Only SELECT queries allowed"
                }

            return {
                "valid": True,
                "error": None
            }

        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
