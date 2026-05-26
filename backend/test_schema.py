from app.db.database import engine
from app.agents.schema.schema_extractor import SchemaExtractor
from app.agents.schema.schema_service import SchemaService

extractor = SchemaExtractor(engine)
service = SchemaService(extractor)

result = service.get_relevant_schema(
    "top customers by total sales"
)

print(result)