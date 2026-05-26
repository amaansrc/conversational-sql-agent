from typing import Dict, List
from .schema_models import DatabaseSchema


class SchemaRanker:
    IGNORE_COLUMNS = {
        "rowguid",
        "modifieddate",
        "passwordhash",
        "passwordsalt"
    }

    KEYWORD_MAP = {
        "customer": ["Customer"],
        "sales": ["SalesOrderHeader", "SalesOrderDetail"],
        "order": ["SalesOrderHeader", "SalesOrderDetail"],
        "product": ["Product"],
        "address": ["Address", "CustomerAddress"]
    }

    IMPORTANT_COLUMNS = {
        "id",
        "name",
        "firstname",
        "lastname",
        "companyname",
        "totaldue",
        "subtotal",
        "linetotal",
        "orderdate",
        "productid",
        "customerid"
    }

    def rank(
        self,
        query: str,
        schema: DatabaseSchema
    ) -> Dict[str, List[str]]:

        query = query.lower()
        ranked_schema = {}

        for table in schema.tables:
            table_score = 0
            selected_columns = []

            # ---- Table scoring ----
            for keyword, mapped_tables in self.KEYWORD_MAP.items():
                if keyword in query and table.table_name in mapped_tables:
                    table_score += 3

            if table.table_name.lower() in query:
                table_score += 2

            # ---- Column scoring ----
            for col in table.columns:
                col_lower = col.lower()

                if col_lower in self.IGNORE_COLUMNS:
                    continue

                col_score = 0

                if col_lower in query:
                    col_score += 3

                if col_lower in self.IMPORTANT_COLUMNS:
                    col_score += 2

                if "id" in col_lower:
                    col_score += 1

                if col_score > 0:
                    selected_columns.append(col)

            if table_score > 0 and selected_columns:
                ranked_schema[table.table_name] = selected_columns

        return ranked_schema