from .supervisor_models import (
    RouteType,
    SupervisorDecision
)


class SupervisorAgent:
    FOLLOWUP_WORDS = {
        "now",
        "only",
        "also",
        "compare",
        "same",
        "that",
        "those",
        "them"
    }

    AMBIGUOUS_WORDS = {
        "top",
        "best",
        "sales",
        "performance",
        "trend"
    }

    METRIC_WORDS = {
        "sales",
        "revenue",
        "profit",
        "quantity",
        "orders",
        "total"
    }

    def _contains_metric(self, query: str) -> bool:
        return any(word in query for word in self.METRIC_WORDS)

    def route(
        self,
        query: str
    ) -> SupervisorDecision:

        query_lower = query.lower()

        # ---- Memory route ----
        for word in self.FOLLOWUP_WORDS:
            if word in query_lower:
                return SupervisorDecision(
                    route=RouteType.MEMORY,
                    reason="Follow-up query detected"
                )

        # ---- Clarification route ----
        ambiguous_hits = 0

        for word in self.AMBIGUOUS_WORDS:
            if word in query_lower:
                ambiguous_hits += 1

        if ambiguous_hits >= 2 and not self._contains_metric(query_lower):
            return SupervisorDecision(
                route=RouteType.CLARIFY,
                reason="Ambiguous intent detected"
            )

        # ---- Schema route ----
        return SupervisorDecision(
            route=RouteType.SCHEMA,
            reason="Clear query, retrieve schema"
        )