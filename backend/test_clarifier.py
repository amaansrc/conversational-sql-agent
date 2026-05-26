from app.agents.supervisor.clarifier import ClarifierAgent

clarifier = ClarifierAgent()

queries = [
    "top customers",
    "sales trend",
    "compare revenue",
    "show only those",
    "only germany",
    "top sales by customer",
    "monthly sales trend"
]

for q in queries:
    result = clarifier.analyze(q)
    print(q)
    print(result)
    print("-" * 40)