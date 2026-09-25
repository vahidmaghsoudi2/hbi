from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.case import Case
from app.models.feedback import Feedback
from app.models.follow_up import FollowUp
from app.models.outcome_assessment import OutcomeAssessment
from app.models.product import Product
from app.models.recommendation import Recommendation


RESULT_STATES = {
    "POSITIVE",
    "PARTIAL",
    "NO_BENEFIT",
    "ADVERSE_REACTION",
    "NOT_USED",
    "UNKNOWN",
}
PROVENANCE_VALUES = {"CUSTOMER", "SELLER", "SPECIALIST", "SYSTEM"}


class OutcomeAssessmentService:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        *,
        case_id: str,
        result_state: str,
        recommendation_id: str | None = None,
        feedback_id: str | None = None,
        follow_up_id: str | None = None,
        product_id: str | None = None,
        provenance: str = "CUSTOMER",
        actor_id: str | None = None,
        observed_at: datetime | None = None,
    ) -> OutcomeAssessment:
        case = self.db.get(Case, case_id)
        if case is None:
            raise ValueError(f"Case not found: {case_id}")

        result_state = (result_state or "").strip().upper()
        if result_state not in RESULT_STATES:
            raise ValueError(f"Invalid outcome assessment result state: {result_state}")

        provenance = (provenance or "").strip().upper()
        if provenance not in PROVENANCE_VALUES:
            raise ValueError(f"Invalid outcome assessment provenance: {provenance}")

        recommendations = []
        if recommendation_id:
            recommendation = self.db.get(Recommendation, recommendation_id)
            if recommendation is None:
                raise ValueError(f"Recommendation not found: {recommendation_id}")
            if recommendation.case_id != case_id:
                raise ValueError("Recommendation does not belong to the given case")
            recommendations.append(recommendation)

        feedback = None
        if feedback_id:
            feedback = self.db.get(Feedback, feedback_id)
            if feedback is None:
                raise ValueError(f"Feedback not found: {feedback_id}")
            if feedback.case_id != case_id:
                raise ValueError("Feedback does not belong to the given case")
            if feedback.recommendation_id:
                feedback_rec = self.db.get(Recommendation, feedback.recommendation_id)
                if feedback_rec is not None:
                    recommendations.append(feedback_rec)

        follow_up = None
        if follow_up_id:
            follow_up = self.db.get(FollowUp, follow_up_id)
            if follow_up is None:
                raise ValueError(f"Follow-up not found: {follow_up_id}")
            if follow_up.case_id != case_id:
                raise ValueError("Follow-up does not belong to the given case")
            if follow_up.status != "COMPLETED":
                raise ValueError("Outcome assessment FollowUp link requires COMPLETED status")
            if follow_up.recommendation_id:
                followup_rec = self.db.get(Recommendation, follow_up.recommendation_id)
                if followup_rec is not None:
                    recommendations.append(followup_rec)

        product = None
        if product_id:
            product = self.db.get(Product, product_id)
            if product is None:
                raise ValueError(f"Product not found: {product_id}")
            if not recommendations:
                raise ValueError("Product linkage requires a traceable Recommendation, Feedback, or FollowUp")
            if any(rec.product_id != product_id for rec in recommendations):
                raise ValueError("Product does not match the Case-linked recommendation trace")

        assessment = OutcomeAssessment(
            outcome_assessment_id=f"oa_{uuid4().hex[:16]}",
            case_id=case_id,
            recommendation_id=recommendation_id,
            feedback_id=feedback_id,
            follow_up_id=follow_up_id,
            product_id=product_id,
            result_state=result_state,
            provenance=provenance,
            actor_id=actor_id,
            observed_at=observed_at or datetime.now(timezone.utc),
        )
        self.db.add(assessment)
        self.db.flush()
        return assessment

    def list_by_case(self, case_id: str, recommendation_id: str | None = None):
        query = self.db.query(OutcomeAssessment).filter(OutcomeAssessment.case_id == case_id)
        if recommendation_id:
            query = query.filter(OutcomeAssessment.recommendation_id == recommendation_id)
        return query.order_by(OutcomeAssessment.observed_at.desc(), OutcomeAssessment.created_at.desc()).all()

    def list_by_customer(self, customer_id: str):
        """Profile projection: longitudinal assessments for all Cases owned by customer.
        Case remains source of truth; this is a read-only aggregation."""
        return (
            self.db.query(OutcomeAssessment)
            .join(Case, Case.case_id == OutcomeAssessment.case_id)
            .filter(Case.customer_id == customer_id)
            .order_by(OutcomeAssessment.observed_at.desc(), OutcomeAssessment.created_at.desc())
            .all()
        )
