from typing import Dict, List
from .schema_extractor import SchemaExtractor
from .schema_ranker import SchemaRanker


class SchemaService:
    def __init__(self, extractor: SchemaExtractor):
        self.extractor = extractor
        self.ranker = SchemaRanker()

    def get_relevant_schema(
        self,
        user_query: str
    ) -> Dict[str, List[str]]:

        schema = self.extractor.extract_schema()

        return self.ranker.rank(
            user_query,
            schema
        )