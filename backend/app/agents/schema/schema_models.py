from pydantic import BaseModel
from typing import List


class TableSchema(BaseModel):
    table_name: str
    columns: List[str]


class DatabaseSchema(BaseModel):
    tables: List[TableSchema]