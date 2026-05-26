from app.agents.supervisor.supervisor_agent import SupervisorAgent

agent = SupervisorAgent()

queries = [
    "top sales trend",
    "show products by category",
    "now only germany"
]

for q in queries:
    result = agent.route(q)
    print(q)
    print(result)
    print("-" * 30)