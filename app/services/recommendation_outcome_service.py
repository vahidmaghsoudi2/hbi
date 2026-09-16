"""Business outcome / feedback / follow-up for recommendations (Mission B)."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.audit import audit_event
from app.models.case import Case
from app.models.recommendation import Recommendation
from app.models.recommendation_outcome import RecommendationOutcome


_ALLOWED_OUTCOMES = {"SHOWN", "ACCEPTED", "REJECTED", "DEFERRED"}
_ALLOWED_FOLLOW_UP = {"NONE", "SCHEDULED", "DONE", "CANCELLED"}


class RecommendationOutcomeService:
    def __init__(self, db: Session):
        self.db = db

    def record_outcome(
        self,
        *,
        case_id: str,
        product_id: str,
        outcome_type: str,
        actor_id: str,
        recommendation_id: Optional[str] = None,
        notes: Optional[str] = None,
        follow_up_notes: Optional[str] = None,
        follow_up_status: Optional[str] = None,
    ) -> RecommendationOutcome:
        ot = (outcome_type or "").strip().upper()
        if ot not in _ALLOWED_OUTCOMES:
            raise ValueError(f"Invalid outcome_type: {outcome_type}")
        fus = None
        if follow_up_status is not None:
            fus = follow_up_status.strip().upper()
            if fus not in _ALLOWED_FOLLOW_UP:
                raise ValueError(f"Invalid follow_up_status: {follow_up_status}")

        row = RecommendationOutcome(
            outcome_id=str(uuid.uuid4()),
            case_id=case_id,
            product_id=product_id,
            recommendation_id=recommendation_id,
            outcome_type=ot,
            actor_id=actor_id,
            notes=notes,
            follow_up_notes=follow_up_notes,
            follow_up_status=fus,
        )
        self.db.add(row)
        self.db.flush()
        audit_event(
            "recommendation_outcome_recorded",
            customer_id=actor_id,
            outcome="ok",
            extra={
                "case_id": case_id,
                "product_id": product_id,
                "outcome_type": ot,
                "recommendation_id": recommendation_id,
            },
        )
        return row

    def list_by_case(self, case_id: str) -> List[RecommendationOutcome]:
        return (
            self.db.query(RecommendationOutcome)
            .filter(RecommendationOutcome.case_id == case_id)
            .order_by(RecommendationOutcome.created_at.desc())
            .all()
        )

    def apply_specialist_override(
        self,
        *,
        case_id: str,
        actor_id: str,
        reason: str,
        override_action: str,
        product_id: Optional[str] = None,
    ) -> Case:
        """Record an auditable specialist override on the Case.

        Preserves prior override text in the audit payload. Does not change
        scoring, Need mappings, or ProductKnowledge.
        """
        case = self.db.query(Case).filter(Case.case_id == case_id).first()
        if case is None:
            raise LookupError(f"Case not found: {case_id}")
        prior = case.operator_override
        payload = {
            "at": datetime.now(timezone.utc).isoformat(),
            "actor_id": actor_id,
            "action": (override_action or "").strip(),
            "reason": (reason or "").strip(),
            "product_id": product_id,
            "prior_override": prior,
        }
        case.operator_override = json.dumps(payload, ensure_ascii=False)
        self.db.flush()
        audit_event(
            "specialist_override_applied",
            customer_id=actor_id,
            outcome="ok",
            extra={"case_id": case_id, "action": payload["action"], "product_id": product_id},
        )
        return case

    def gallery_for_case(self, case_id: str) -> List[Dict[str, Any]]:
        """Front-door recommendation view: current recommendations for a case."""
        rows = (
            self.db.query(Recommendation)
            .filter(Recommendation.case_id == case_id)
            .order_by(Recommendation.ranking_score.desc().nullslast())
            .all()
        )
        out: List[Dict[str, Any]] = []
        for r in rows:
            out.append(
                {
                    "recommendation_id": r.recommendation_id,
                    "case_id": r.case_id,
                    "product_id": r.product_id,
                    "need_match_score": r.need_match_score,
                    "evidence_score": r.evidence_score,
                    "eligibility_status": r.eligibility_status,
                    "ranking_score": r.ranking_score,
                    "ranking_reasons": r.ranking_reasons,
                    "warnings": r.warnings,
                    "evidence_refs": r.evidence_refs,
                }
            )
        return out
