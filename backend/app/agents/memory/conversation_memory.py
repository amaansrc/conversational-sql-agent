from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ConversationMemory:
    last_query: Optional[str] = None
    last_metric: Optional[str] = None
    last_group_by: Optional[str] = None
    last_tables: list[str] = field(default_factory=list)
    last_filters: dict = field(default_factory=dict)
    last_time_window: Optional[str] = None
    entities: list[str] = field(default_factory=list)

    def reset(self):
        self.last_query = None
        self.last_metric = None
        self.last_group_by = None
        self.last_tables = []
        self.last_filters = {}
        self.last_time_window = None
        self.entities = []