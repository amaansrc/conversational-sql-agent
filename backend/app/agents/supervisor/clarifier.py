import re
from app.agents.supervisor.models import ClarificationResult


class ClarifierAgent:
    def __init__(self):
        self.metric_keywords = {
            "best",
            "top",
            "highest",
            "lowest"
        }

        self.trend_keywords = {
            "trend",
            "growth",
            "decline"
        }

        self.compare_keywords = {
            "compare",
            "difference"
        }

        self.pronouns = {
            "those",
            "them",
            "that",
            "these"
        }

        self.partial_filters = {
            "only",
            "except",
            "exclude"
        }

    def analyze(self, query: str) -> ClarificationResult:
        q = query.lower()

        # 1. Missing metric
        if any(word in q for word in self.metric_keywords):
            if not self._contains_metric(q):
                return ClarificationResult(
                    needs_clarification=True,
                    ambiguity_type="missing_metric",
                    question="What metric should I use for this breakdown (sales, revenue, quantity, profit)?"
                )

        if "by category" in q and not self._contains_metric(q):
            return ClarificationResult(
                needs_clarification=True,
                ambiguity_type="missing_metric",
                question="What metric should I use for this breakdown (sales, revenue, quantity, profit)?"
            )

        # 2. Missing timeframe
        if any(word in q for word in self.trend_keywords):
            if not self._contains_time(q):
                return ClarificationResult(
                    needs_clarification=True,
                    ambiguity_type="missing_timeframe",
                    question="What time period should I analyze (daily, monthly, yearly)?"
                )

        # 3. Missing grouping
        if any(word in q for word in self.compare_keywords):
            if not self._contains_grouping(q):
                return ClarificationResult(
                    needs_clarification=True,
                    ambiguity_type="missing_grouping",
                    question="What should I compare by (customer, region, product, date)?"
                )
            
        # 4. Pronoun follow-up ambiguity
        if any(word in q.split() for word in self.pronouns):
            return ClarificationResult(
                needs_clarification=True,
                ambiguity_type="pronoun_reference",
                question="Can you clarify what 'those' refers to?"
            )

        # 5. Partial filter ambiguity
        if any(word in q.split() for word in self.partial_filters):
            words = q.split()

            # only "only germany" / "exclude bikes"
            if len(words) <= 3:
                return ClarificationResult(
                    needs_clarification=True,
                    ambiguity_type="partial_filter",
                    question="What should I apply this filter to?"
                )

        return ClarificationResult(
            needs_clarification=False
        )

    def _contains_metric(self, query: str) -> bool:
        metrics = {
            "sales",
            "revenue",
            "profit",
            "quantity",
            "orders",
            "total"
        }
        return any(word in query for word in metrics)

    def _contains_time(self, query: str) -> bool:
        times = {
            "day",
            "week",
            "month",
            "year",
            "daily",
            "monthly",
            "yearly"
        }
        return any(word in query for word in times)

    def _contains_grouping(self, query: str) -> bool:
        groups = {
            "customer",
            "region",
            "product",
            "date",
            "country",
            "category"
        }
        return any(word in query for word in groups)