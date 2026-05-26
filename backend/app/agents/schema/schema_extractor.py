from sqlalchemy import inspect
from sqlalchemy.engine import Engine
from .schema_models import TableSchema, DatabaseSchema


class SchemaExtractor:
    def __init__(self, engine: Engine):
        self.engine = engine

    def extract_schema(self) -> DatabaseSchema:
        inspector = inspect(self.engine)

        tables = []

        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)

            column_names = [
                col["name"]
                for col in columns
            ]

            tables.append(
                TableSchema(
                    table_name=table_name,
                    columns=column_names
                )
            )

        return DatabaseSchema(tables=tables)