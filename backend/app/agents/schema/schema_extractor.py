from sqlalchemy import inspect
from sqlalchemy.engine import Engine
from .schema_models import TableSchema, DatabaseSchema


class SchemaExtractor:
    def __init__(self, engine: Engine):
        self.engine = engine

    def extract_schema(self) -> DatabaseSchema:
        inspector = inspect(self.engine)

        tables = []

        # Get all available schemas (e.g. dbo, SalesLT)
        schema_names = inspector.get_schema_names()

        for schema_name in schema_names:
            # Skip system schemas
            if schema_name in (
                "INFORMATION_SCHEMA",
                "sys",
                "guest",
                "db_owner",
                "db_accessadmin",
                "db_securityadmin",
                "db_ddladmin",
                "db_backupoperator",
                "db_datareader",
                "db_datawriter",
                "db_denydatareader",
                "db_denydatawriter",
            ):
                continue

            for table_name in inspector.get_table_names(schema=schema_name):
                columns = inspector.get_columns(
                    table_name, schema=schema_name
                )

                column_names = [
                    col["name"]
                    for col in columns
                ]

                # Use schema-qualified name (e.g. SalesLT.Customer)
                qualified_name = f"{schema_name}.{table_name}"

                tables.append(
                    TableSchema(
                        table_name=qualified_name,
                        columns=column_names
                    )
                )

        return DatabaseSchema(tables=tables)