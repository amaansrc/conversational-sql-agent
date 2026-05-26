import re
from app.agents.memory.conversation_memory import (
    ConversationMemory
)


class MemoryService:
    def __init__(self):
        self.memory = ConversationMemory()

    def update(
        self,
        query: str,
        tables: list[str] = None
    ):
        q = query.lower()

        self.memory.last_query = query

        # metric
        if "sales" in q:
            self.memory.last_metric = "sales"
        elif "revenue" in q:
            self.memory.last_metric = "revenue"
        elif "profit" in q:
            self.memory.last_metric = "profit"

        # grouping
        groups = [
            "customer",
            "product",
            "region",
            "country",
            "date"
        ]
        for g in groups:
            if g in q:
                self.memory.last_group_by = g

        # time windows
        if "last month" in q:
            self.memory.last_time_window = "last month"
        elif "last year" in q:
            self.memory.last_time_window = "last year"
        elif "monthly" in q:
            self.memory.last_time_window = "monthly"

        # simple country filter
        countries = [
            "germany",
            "france",
            "usa",
            "uk"
        ]
        for c in countries:
            if c in q:
                self.memory.last_filters["country"] = c

        if tables:
            self.memory.last_tables = tables

    def get_context(self):
        return self.memory