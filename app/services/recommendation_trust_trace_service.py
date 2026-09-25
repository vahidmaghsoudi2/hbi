import json
from typing import Any, Dict, Iterable, List, Optional


SUPPORTING_QA_STATUSES = {"APPROVED", "VERIFIED"}


class TrustTraceIntegrityError(ValueError):
    """Raised when persisted recommendation evidence references cannot be resolved."""


class RecommendationTrustTraceService:
    """Read-only projection of authoritative Recommendation + Evidence + Case/PK state."""

    def __init__(self, db):
        self.db = db

    @staticmethod
    def _json_list(value: Any) -> List[Any]:
        if not value:
            return []
        if isinstance(value, list):
            return value
        try:
            decoded = json.loads(value)
        except (TypeError, ValueError):
            return []
        return decoded if isinstance(decoded, list) else []

    @staticmethod
    def _ref_id(ref: Any) -> Optional[str]:
        if isinstance(ref, str):
            return ref
        if isinstance(ref, dict):
            return ref.get("evidence_id") or ref.get("claim_id")
        return None

    @staticmethod
    def _evidence_dict(ev) -> Dict[str, Any]:
        return {
            "evidence_id": ev.evidence_id,
            "claim_id": ev.claim_id,
            "product_id": ev.product_id,
            "claim": ev.claim,
            "field": ev.field,
            "claim_type": ev.claim_type,
            "source_type": ev.source_type,
            "source_reference": ev.source_reference,
            "evidence_strength": ev.evidence_strength,
            "evidence_status": ev.evidence_status,
            "qa_status": ev.qa_status,
            "conflict_status": ev.conflict_status,
            "source_date": ev.source_date,
            "evidence_date": ev.evidence_date,
        }

    def build(
        self,
        recommendation,
        *,
        case=None,
        product=None,
        evidences: Optional[Iterable[Any]] = None,
        product_knowledge=None,
    ) -> Dict[str, Any]:
        evidence_rows = list(evidences or [])
        by_id = {ev.evidence_id: ev for ev in evidence_rows}
        by_claim_id = {ev.claim_id: ev for ev in evidence_rows if ev.claim_id}

        raw_refs = self._json_list(getattr(recommendation, "evidence_refs", None))
        resolved_refs: List[str] = []
        missing_refs: List[str] = []

        for raw_ref in raw_refs:
            ref_id = self._ref_id(raw_ref)
            ev = by_id.get(ref_id) or by_claim_id.get(ref_id)
            if ev is None:
                missing_refs.append(ref_id or str(raw_ref))
                continue
            resolved_refs.append(ev.evidence_id)

        if missing_refs:
            raise TrustTraceIntegrityError(
                "Recommendation evidence_refs contain unresolved Evidence references: "
                + ", ".join(missing_refs)
            )

        supporting: List[Dict[str, Any]] = []
        excluded: List[Dict[str, Any]] = []
        supporting_ids = set()

        for ev in evidence_rows:
            if ev.evidence_id not in resolved_refs:
                continue
            if ev.product_id != recommendation.product_id:
                excluded.append({
                    **self._evidence_dict(ev),
                    "decision_use": "EXCLUDED",
                    "exclusion_reason": "CROSS_PRODUCT_REFERENCE",
                })
                continue
            qa = (ev.qa_status or "").strip().upper()
            conflict = (ev.conflict_status or "").strip().upper()
            if qa not in SUPPORTING_QA_STATUSES:
                excluded.append({
                    **self._evidence_dict(ev),
                    "decision_use": "EXCLUDED",
                    "exclusion_reason": f"QA_STATUS_{qa or 'MISSING'}",
                })
                continue
            if conflict == "CONFLICT":
                excluded.append({
                    **self._evidence_dict(ev),
                    "decision_use": "EXCLUDED",
                    "exclusion_reason": "UNRESOLVED_CONFLICT",
                })
                continue
            supporting.append({
                **self._evidence_dict(ev),
                "decision_use": "SUPPORTING",
            })
            supporting_ids.add(ev.evidence_id)

        for ev in evidence_rows:
            if ev.evidence_id in supporting_ids or ev.evidence_id in resolved_refs:
                continue
            qa = (ev.qa_status or "").strip().upper()
            conflict = (ev.conflict_status or "").strip().upper()
            reason = "NOT_IN_RECOMMENDATION_TRACE"
            if conflict == "CONFLICT":
                reason = "UNRESOLVED_CONFLICT"
            elif qa not in SUPPORTING_QA_STATUSES:
                reason = f"QA_STATUS_{qa or 'MISSING'}"
            excluded.append({
                **self._evidence_dict(ev),
                "decision_use": "EXCLUDED",
                "exclusion_reason": reason,
            })

        warnings = self._json_list(getattr(recommendation, "warnings", None))
        stop_reasons = self._json_list(getattr(recommendation, "exclusion_reasons", None))
        if getattr(recommendation, "eligibility_status", None) != "ELIGIBLE":
            stop_reasons.append(
                f"Recommendation status: {getattr(recommendation, 'eligibility_status', None)}"
            )
        if any((ev.conflict_status or "").strip().upper() == "CONFLICT" for ev in evidence_rows):
            warnings.append("Unresolved evidence conflict exists for this product.")

        seen = set()
        warnings = [w for w in warnings if not (w in seen or seen.add(w))]
        seen = set()
        stop_reasons = [s for s in stop_reasons if not (s in seen or seen.add(s))]

        product_payload = None
        if product is not None:
            product_payload = {
                "product_id": product.product_id,
                "brand": product.brand,
                "product_name": product.product_name,
                "variant": product.variant,
                "size_value": product.size_value,
                "size_unit": product.size_unit,
            }

        knowledge_payload = None
        if product_knowledge is not None:
            knowledge_payload = {
                "known_use_cases": product_knowledge.known_use_cases,
                "claimed_benefits": product_knowledge.claimed_benefits,
                "contraindications": product_knowledge.contraindications,
                "evidence_status": product_knowledge.evidence_status,
                "knowledge_confidence": product_knowledge.knowledge_confidence,
            }

        return {
            "recommendation_id": recommendation.recommendation_id,
            "case_id": recommendation.case_id,
            "product_id": recommendation.product_id,
            "eligibility_status": recommendation.eligibility_status,
            "need_match_score": recommendation.need_match_score,
            "evidence_score": recommendation.evidence_score,
            "matched_need_context": getattr(case, "identified_needs", None) if case else None,
            "product": product_payload,
            "supporting_evidence": supporting,
            "excluded_evidence": excluded,
            "rationale": getattr(recommendation, "ranking_reasons", None) or "",
            "warnings": warnings,
            "stop_reasons": stop_reasons,
            "product_knowledge": knowledge_payload,
            "trace_integrity": {
                "status": "VALID",
                "persisted_reference_count": len(raw_refs),
                "resolved_reference_count": len(resolved_refs),
                "missing_reference_count": 0,
            },
            "semantics": {
                "supporting_evidence": "APPROVED/VERIFIED, non-CONFLICT Evidence referenced by Recommendation",
                "excluded_evidence": "Evidence not eligible for decision use or absent from Recommendation trace",
                "rationale": "Authoritative Recommendation rationale; no new inference or scoring is performed",
            },
        }

    def get_for_recommendation(self, recommendation_id: str, customer_id: str) -> Dict[str, Any]:
        from app.models.case import Case
        from app.models.evidence import Evidence
        from app.models.product import Product
        from app.models.product_knowledge import ProductKnowledge
        from app.models.recommendation import Recommendation

        recommendation = self.db.get(Recommendation, recommendation_id)
        if recommendation is None:
            raise LookupError("Recommendation not found")

        case = self.db.get(Case, recommendation.case_id)
        if case is None:
            raise LookupError("Case not found")
        if case.customer_id != customer_id:
            raise PermissionError("Access denied")

        product = self.db.get(Product, recommendation.product_id)
        if product is None:
            raise LookupError("Product not found")

        evidences = (
            self.db.query(Evidence)
            .filter(Evidence.product_id == recommendation.product_id)
            .all()
        )
        product_knowledge = self.db.query(ProductKnowledge).filter(
            ProductKnowledge.product_id == recommendation.product_id
        ).first()

        return self.build(
            recommendation,
            case=case,
            product=product,
            evidences=evidences,
            product_knowledge=product_knowledge,
        )
