"""Read-only explainable suitability and customer consultation output projections.

A ProductProblemLink CANDIDATE is never promoted to suitability approval or a
recommendation. This module only explains current review blockers and projects
already-persisted, independently eligible recommendations.
"""
import json
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.case import Case
from app.models.product import Product
from app.repositories.recommendation_repository import RecommendationRepository
from app.services.product_problem_candidate_retrieval_service import (
    ProductProblemCandidateRetrievalService,
)


_BLOCKER_EXPLANATIONS = {
    "PRODUCT_IDENTITY_NOT_VERIFIED": "هویت محصول هنوز تأیید نشده است.",
    "PRODUCT_QA_NOT_VALID": "کنترل کیفیت محصول وضعیت معتبر ندارد.",
    "PRODUCT_NOT_ACTIVE": "چرخه عمر محصول اجازه عرضه فعال نمی‌دهد.",
    "EVIDENCE_NOT_VERIFIED": "شاهد متصل به این ادعا هنوز تأیید QA نشده است.",
    "EVIDENCE_CONFLICT": "برای شاهد یا ادعای متصل تعارض ثبت شده است.",
    "VARIANT_UNKNOWN": "نسخه یا نوع محصول برای این ارتباط مشخص نیست.",
}


class ExplainableSuitabilityService:
    """Computed-only projection. It does not write or mutate domain records."""

    def __init__(self, db: Session):
        self.db = db
        self.candidate_retrieval = ProductProblemCandidateRetrievalService(db)
        self.recommendation_repository = RecommendationRepository(db)

    def evaluate(
        self,
        problem_id: str,
        *,
        market_region: Optional[str] = None,
        variant: Optional[str] = None,
    ) -> Dict[str, Any]:
        retrieved = self.candidate_retrieval.retrieve(
            problem_id,
            market_region=market_region,
            variant=variant,
        )
        explained = []
        for candidate in retrieved["candidates"]:
            blockers = list(candidate["product_gate_blockers"])
            explanations = [
                _BLOCKER_EXPLANATIONS.get(code, code)
                for code in blockers
            ]
            if blockers:
                suitability_status = "BLOCKED"
            else:
                suitability_status = "HUMAN_REVIEW_REQUIRED"
                explanations.append(
                    "ارتباط فقط در وضعیت CANDIDATE است؛ ارزیابی انسانی لازم است و این مورد تأیید تناسب یا توصیه محصول نیست."
                )
            explained.append({
                **candidate,
                "suitability_status": suitability_status,
                "explanations": explanations,
                "recommendation_eligible": False,
            })

        return {
            "problem_id": retrieved["problem_id"],
            "problem_map_version": retrieved["problem_map_version"],
            "evaluation_mode": "EXPLAINABLE_HUMAN_REVIEW_ONLY",
            "computed_only": True,
            "recommendation_eligible": False,
            "candidate_count": retrieved["candidate_count"],
            "excluded_integrity_count": retrieved["excluded_integrity_count"],
            "candidates": explained,
            "empty_result_reason": (
                "NO_CURRENT_PRODUCT_PROBLEM_CANDIDATES"
                if not explained else None
            ),
        }

    @staticmethod
    def _read_json_list(value: Optional[str]) -> list:
        if not value:
            return []
        try:
            decoded = json.loads(value)
        except (TypeError, ValueError):
            return []
        return decoded if isinstance(decoded, list) else []

    def consultation_output(self, case_id: str) -> Dict[str, Any]:
        """Return the visit context and only already-eligible persisted recommendations."""
        case = self.db.get(Case, case_id)
        if case is None:
            raise LookupError(f"Case {case_id} not found.")

        envelope: Dict[str, Any] = {}
        try:
            decoded = json.loads(case.evidence_gaps or "{}")
            if isinstance(decoded, dict):
                envelope = decoded
        except (TypeError, ValueError):
            pass
        consultation_context = envelope.get("consultation_v1")
        if not isinstance(consultation_context, dict):
            consultation_context = None

        eligible_rows = [
            row for row in self.recommendation_repository.find_by_case(case_id)
            if (row.eligibility_status or "").strip().upper() == "ELIGIBLE"
        ]
        eligible_rows.sort(
            key=lambda row: (row.ranking_score or 0.0, row.recommendation_id),
            reverse=True,
        )
        recommendations = []
        for row in eligible_rows:
            product = self.db.get(Product, row.product_id)
            recommendations.append({
                "recommendation_id": row.recommendation_id,
                "product_id": row.product_id,
                "brand": product.brand if product else None,
                "product_name": product.product_name if product else None,
                "eligibility_status": "ELIGIBLE",
                "need_match_score": row.need_match_score,
                "evidence_score": row.evidence_score,
                "ranking_score": row.ranking_score,
                "warnings": self._read_json_list(row.warnings),
            })

        return {
            "case_id": case.case_id,
            "case_type": case.case_type,
            "consultation_context": consultation_context,
            "consultation_context_status": (
                "PRESENT" if consultation_context is not None else "NOT_RECORDED"
            ),
            "recommendation_status": (
                "RECOMMENDATIONS_AVAILABLE"
                if recommendations else "NO_ELIGIBLE_RECOMMENDATION"
            ),
            "recommendation_count": len(recommendations),
            "recommendations": recommendations,
            "generated_from": "PERSISTED_CASE_AND_RECOMMENDATION_RECORDS",
            "computed_only": True,
        }
