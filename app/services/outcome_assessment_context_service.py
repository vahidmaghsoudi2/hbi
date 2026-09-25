"""Read-only longitudinal OutcomeAssessment context for consultation decision support."""

from __future__ import annotations

from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.models.case import Case
from app.services.outcome_assessment_service import OutcomeAssessmentService


class OutcomeAssessmentContextService:
    """Project Case-owned OutcomeAssessments into additive consultation context."""

    def __init__(self, db: Session):
        self.db = db
        self.outcomes = OutcomeAssessmentService(db)

    def build_for_customer(self, customer_id: str) -> List[Dict[str, Any]]:
        rows = self.outcomes.list_by_customer(customer_id)
        context: List[Dict[str, Any]] = []
        for row in rows:
            context.append({
                "outcome_assessment_id": row.outcome_assessment_id,
                "case_id": row.case_id,
                "result_state": row.result_state,
                "observed_at": row.observed_at.isoformat() if row.observed_at else None,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "provenance": row.provenance,
                "actor_id": row.actor_id,
                "product_id": row.product_id,
                "recommendation_id": row.recommendation_id,
                "feedback_id": row.feedback_id,
                "follow_up_id": row.follow_up_id,
            })
        return context

    def build_for_case(self, case: Case) -> Dict[str, Any]:
        """Return additive history plus explicit trace metadata for a customer-owned Case."""
        rows = self.build_for_customer(case.customer_id)
        return {
            "source": "OUTCOME_ASSESSMENT_HISTORY",
            "mode": "ADDITIVE_LONGITUDINAL_CONTEXT",
            "ordering": ["observed_at DESC", "created_at DESC"],
            "case_id": case.case_id,
            "customer_id": case.customer_id,
            "records": rows,
        }
