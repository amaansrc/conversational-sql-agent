from app.agents.memory.memory_service import (
    MemoryService
)

memory = MemoryService()

queries = [
    "show total sales by customer",
    "now only germany",
    "last month only"
]

for q in queries:
    memory.update(q)
    print(q)
    print(memory.get_context())
    print("-" * 50)