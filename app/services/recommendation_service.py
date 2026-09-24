import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.recommendation import Recommendation
from app.models.product import Product
from app.models.product_knowledge import ProductKnowledge
from app.models.evidence import Evidence
from app.repositories.recommendation_repository import RecommendationRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.product_knowledge_repository import ProductKnowledgeRepository
from app.repositories.evidence_repository import EvidenceRepository
from app.services.base import BaseService
from app.services.need_normalization import normalize_needs_from_factors, CANONICAL_NEEDS
from app.services.product_compatibility import product_compatibility_ids
from app.reasoning.reasoning_engine import ReasoningEngine
from app.reasoning.conflict_analyzer import ConflictSeverity

logger = logging.getLogger(__name__)

_EVIDENCE_WEIGHTS = {
    "PEER_REVIEWED": 1.0,
    "CLINICAL_TRIAL": 1.0,
    "REGULATORY": 1.0,
    "OFFICIAL_MANUFACTURER": 0.6,
    "MANUFACTURER": 0.6,
    "REPUTABLE_RETAILER": 0.4,
    "SECONDARY": 0.2,
}

NEED_MATCH_SUFFICIENT = 0.40

_MEDICAL_TOKENS = {
    "پزشک", "دکتر", "نسخه", "دارو", "بیماری", "حساسیت شدید",
    "بارداری", "شیردهی", "تحت درمان", "doctor", "prescription",
    "pregnancy", "breastfeeding", "medication", "disease"
}


class RecommendationService(BaseService[Recommendation, RecommendationRepository]):
    """RecommendationService — F2 + GAP-01 + GAP-03 + GAP-04 + GAP-05 L1"""

    def __init__(self, db: Session):
        super().__init__(RecommendationRepository(db), db)
        self.product_repo = ProductRepository(db)
        self.inventory_repo = InventoryRepository(db)
        self.pk_repo = ProductKnowledgeRepository(db)
        self.evidence_repo = EvidenceRepository(db)
        self.reasoning_engine = ReasoningEngine()

    def find_by_case(self, case_id: str) -> List[Recommendation]:
        return self.repository.find_by_case(case_id)

    def find_by_product(self, product_id: str) -> List[Recommendation]:
        return self.repository.find_by_product(product_id)

    def find_eligible(self) -> List[Recommendation]:
        return self.repository.find_eligible()

    def _map_unknown_priority(self, severity: str) -> str:
        if severity == ConflictSeverity.CRITICAL.value:
            return "CRITICAL_UNKNOWN"
        if severity == ConflictSeverity.HIGH.value:
            return "IMPORTANT_UNKNOWN"
        return "OPTIONAL_UNKNOWN"

    def _detect_medical_context(self, customer_profile: Dict, factors: List[Dict]) -> tuple:
        texts = []
        concerns = customer_profile.get("concerns") or ""
        if isinstance(concerns, list):
            texts.extend([str(c) for c in concerns])
        else:
            texts.append(str(concerns))
        notes = customer_profile.get("medical_notes") or customer_profile.get("operator_notes") or ""
        texts.append(str(notes))
        for f in factors:
            texts.append(str(f.get("value", "")))
        combined = " ".join(texts).lower()
        hits = [t for t in _MEDICAL_TOKENS if t.lower() in combined]
        if hits:
            return True, f"Medical context tokens detected: {', '.join(hits[:5])}"
        return False, ""

    def _normalize_tokens(self, text: str) -> set:
        if not text:
            return set()
        return {t.strip().lower() for t in str(text).replace(",", " ").split() if t.strip()}

    def _build_decision_state(self, case_id: str, customer_profile: Dict) -> Dict[str, Any]:
        raw_concerns = []
        concerns_raw = customer_profile.get("concerns") or ""
        if isinstance(concerns_raw, list):
            raw_concerns = [str(c).strip() for c in concerns_raw if c and str(c).strip()]
        else:
            raw_concerns = [c.strip() for c in str(concerns_raw).split(",") if c.strip()]
        profile_fact_context = customer_profile.get("_profile_fact_context") or {}
        source_map = profile_fact_context.get("sources") or {}
        concern_source = (source_map.get("concerns") or {}).get("source", "CURRENT_CONSULTATION")
        concern_fact_id = (source_map.get("concerns") or {}).get("profile_fact_id")
        factor_source = "profile_fact" if concern_source == "PROFILE_FACT" else "customer_input"
        factors = [{
            "name": "concern",
            "value": c,
            "source": factor_source,
            "validity": "DECLARED",
            **({"profile_fact_id": concern_fact_id} if concern_fact_id else {}),
        } for c in raw_concerns]
        medical_active, medical_notes = self._detect_medical_context(customer_profile, factors)
        return {
            "case_id": case_id,
            "customer_id": customer_profile.get("customer_id"),
            "raw_concerns": raw_concerns,
            "evidence_refs": [],
            "evidence_gaps": [],
            "unknowns": [],
            "conflicts": list(profile_fact_context.get("conflicts") or []),
            "factors": factors,
            "profile_fact_context": profile_fact_context,
            "inferences": [],
            "medical_context_active": medical_active,
            "medical_context_notes": medical_notes,
            "needs": [],
            "need_match": 0.0,
            "confidence": 0.0,
            "decision_status": "READY",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _generate_needs_from_decision_state(self, decision_state: Dict[str, Any]) -> List[str]:
        """Need ONLY from Decision State (F2 + GAP-05 L1). No silent guessing."""
        needs, mappings, unmapped, ambiguous = normalize_needs_from_factors(
            decision_state.get("factors", [])
        )
        decision_state["need_mappings"] = mappings
        decision_state["unmapped_need_factors"] = unmapped
        decision_state["ambiguous_need_factors"] = ambiguous
        if not needs and (unmapped or ambiguous):
            decision_state["decision_status"] = "INSUFFICIENT"
        return needs

    def _calculate_need_match(self, generated_needs: List[str], known_use_cases: Optional[str]) -> float:
        """Match canonical customer Needs to canonical ProductKnowledge use cases.

        The frozen scoring formula is unchanged: intersection size divided by
        the number of canonical Need ids. Only the semantic input surface changes.
        """
        if not generated_needs:
            return 0.0
        surface_to_id = {surface: cid for cid, surface in CANONICAL_NEEDS.items()}
        generated_ids = {surface_to_id[n] for n in generated_needs if n in surface_to_id}
        if not generated_ids:
            return 0.0
        product_ids = set(product_compatibility_ids(known_use_cases))
        return round(len(generated_ids & product_ids) / max(len(generated_ids), 1), 4)

    def _compute_evidence_score(self, evidences: List[Evidence]) -> float:
        """Score only Evidence explicitly approved by QA for decision use."""
        approved_evidences = [
            ev for ev in evidences
            if (getattr(ev, "qa_status", None) or "").strip().upper() in {"APPROVED", "VERIFIED"}
        ]
        if not approved_evidences:
            return 0.0
        total = 0.0
        for ev in approved_evidences:
            st = (ev.source_type or "SECONDARY").upper()
            total += _EVIDENCE_WEIGHTS.get(st, 0.2)
        return round(min(1.0, total / len(approved_evidences)), 4)

    def _build_inferences(self, engine_result: Dict[str, Any], decision_state: Dict[str, Any], product_id: str) -> List[Dict[str, Any]]:
        inferences: List[Dict[str, Any]] = []
        for u in engine_result.get("unknowns", []):
            inferences.append({"statement": f"Unknown on field '{u.get('field')}' requires attention", "confidence": 0.5, "based_on_evidence_refs": [], "based_on_factors": [], "source": "engine_unknown", "product_id": product_id})
        for v in engine_result.get("claim_boundary_violations", []):
            inferences.append({"statement": f"Claim boundary violation detected: {v.get('reason', 'unspecified')}", "confidence": 0.6, "based_on_evidence_refs": [], "based_on_factors": [], "source": "claim_validator", "product_id": product_id})
        if decision_state.get("medical_context_active"):
            inferences.append({"statement": "Medical context present — professional review may be required", "confidence": 0.7, "based_on_evidence_refs": [], "based_on_factors": [f.get("value") for f in decision_state.get("factors", [])], "source": "medical_context_trigger", "product_id": product_id})
        return inferences

    def _map_eligibility(self, engine_result: Dict[str, Any], decision_state: Dict[str, Any], need_match: float, product_unknowns: Optional[List[Dict[str, Any]]] = None) -> str:
        product_unknowns = product_unknowns or []
        for u in product_unknowns:
            if u.get("unknown_priority") == "CRITICAL_UNKNOWN":
                return "INELIGIBLE_PENDING_REVIEW"
        for u in decision_state.get("unknowns", []):
            if u.get("unknown_priority") == "CRITICAL_UNKNOWN":
                return "INELIGIBLE_PENDING_REVIEW"
        # Hard gates: medical context, claim-boundary violations, and HIGH/CRITICAL conflicts
        # must never become an ordinary recommendation even if the numeric score is high.
        if decision_state.get("medical_context_active"):
            return "INELIGIBLE_PENDING_REVIEW"
        if engine_result.get("claim_boundary_violations"):
            return "INELIGIBLE_PENDING_REVIEW"
        high_or_critical = [
            c for c in (engine_result.get("conflicts") or [])
            if c.get("severity") in (ConflictSeverity.HIGH.value, ConflictSeverity.CRITICAL.value)
        ]
        if high_or_critical:
            return "INELIGIBLE_PENDING_REVIEW"
        if need_match < NEED_MATCH_SUFFICIENT or not decision_state.get("needs"):
            return "INELIGIBLE_PENDING_REVIEW"
        eng_elig = engine_result.get("eligibility") or "INELIGIBLE"
        if eng_elig == "NEEDS_REVIEW":
            return "INELIGIBLE_PENDING_REVIEW"
        if eng_elig == "ELIGIBLE":
            return "ELIGIBLE"
        return "INELIGIBLE_PENDING_REVIEW"

    def _stable_recommendation_id(self, case_id: str, product_id: str) -> str:
        return f"rec_{case_id}_{product_id}"

    def _upsert_current_recommendation(self, *, case_id: str, product_id: str, need_match: float, evidence_score: float, eligibility: str, ranking_score: float, ranking_reasons: str, exclusion_reasons: str = "", evidence_refs: Optional[List[Dict[str, Any]]] = None, warnings: Optional[List[str]] = None) -> Recommendation:
        existing = self.repository.find_by_case_and_product(case_id, product_id)
        evidence_refs_json = json.dumps(evidence_refs or [], ensure_ascii=False, sort_keys=True)
        warnings_json = json.dumps(warnings or [], ensure_ascii=False)
        if isinstance(existing, Recommendation):
            existing.need_match_score = need_match
            existing.evidence_score = evidence_score
            existing.eligibility_status = eligibility
            existing.ranking_score = ranking_score
            existing.ranking_reasons = ranking_reasons[:2000] if ranking_reasons else ""
            existing.exclusion_reasons = exclusion_reasons or ""
            existing.evidence_refs = evidence_refs_json
            existing.warnings = warnings_json
            self.db.flush()
            return existing
        return self.repository.create(
            recommendation_id=self._stable_recommendation_id(case_id, product_id),
            case_id=case_id,
            product_id=product_id,
            need_match_score=need_match,
            evidence_score=evidence_score,
            eligibility_status=eligibility,
            ranking_score=ranking_score,
            ranking_reasons=ranking_reasons[:2000] if ranking_reasons else "",
            exclusion_reasons=exclusion_reasons or "",
            evidence_refs=evidence_refs_json,
            warnings=warnings_json,
        )

    def _existing_conflicts_from_evidence(self, evidences: List[Evidence], product_id: str) -> List[Dict[str, Any]]:
        """Build existing_conflicts for ReasoningEngine from Evidence.conflict_status=CONFLICT."""
        conflicts: List[Dict[str, Any]] = []
        for ev in evidences or []:
            status = (getattr(ev, "conflict_status", None) or "").strip().upper()
            if status != "CONFLICT":
                continue
            conflicts.append({
                "field": (getattr(ev, "field", None) or "general"),
                "conflicting_values": [getattr(ev, "claim", None) or ""],
                "values": [getattr(ev, "claim", None) or ""],
                "evidence_refs": [getattr(ev, "evidence_id", None)],
                "sources": [getattr(ev, "source_reference", None)],
                "product_id": product_id,
            })
        return conflicts

    def generate_recommendations(self, case_id: str, customer_profile: Dict = None) -> List[Recommendation]:
        if customer_profile is None:
            customer_profile = {}
        decision_state = self._build_decision_state(case_id, customer_profile)
        needs = self._generate_needs_from_decision_state(decision_state)
        decision_state["needs"] = needs
        if not needs:
            decision_state["decision_status"] = "INSUFFICIENT"
        # Hard gate: Medical Context always forces REFERRAL (independent of presence of Need).
        if decision_state["medical_context_active"]:
            decision_state["decision_status"] = "REFERRAL"
        products = self.product_repo.find_by_identity_status_and_active("VERIFIED")
        recommendations: List[Recommendation] = []
        existing_case_recs = list(self.repository.find_by_case(case_id))
        kept_product_ids = set()
        case_unknowns_before_loop = len(decision_state.get("unknowns", []))
        for product in products:
            pk = self.pk_repo.find_by_product(product.product_id)
            known_use_cases = pk.known_use_cases if pk else None
            evidences = self.evidence_repo.find_by_product(product.product_id)
            inv = self.inventory_repo.find_by_product(product.product_id)
            inventory_score = 1.0 if (inv and inv.quantity_available and inv.quantity_available > 0) else 0.0
            if inventory_score <= 0.0:
                continue
            need_match = self._calculate_need_match(needs, known_use_cases)
            evidence_score = self._compute_evidence_score(evidences)
            evidence_list = [{
                "evidence_id": ev.evidence_id,
                "claim_id": ev.claim_id,
                "field": ev.field,
                "claim_type": ev.claim_type,
                "source_reference": ev.source_reference,
                "source_type": ev.source_type,
                "evidence_strength": ev.evidence_strength,
                "qa_status": ev.qa_status,
                "claim": ev.claim,
                "conflict_status": getattr(ev, "conflict_status", None),
            } for ev in evidences]
            existing_conflicts = self._existing_conflicts_from_evidence(evidences, product.product_id)
            pk_snapshot = {}
            if pk:
                pk_snapshot = {"known_use_cases": pk.known_use_cases, "claimed_benefits": pk.claimed_benefits, "contraindications": pk.contraindications, "ingredients": pk.ingredients}
            engine_result = self.reasoning_engine.run(
                product_id=product.product_id,
                product_knowledge_snapshot=pk_snapshot,
                evidence_list=evidence_list,
                existing_conflicts=existing_conflicts,
                need_match=need_match,
                evidence_score=evidence_score,
                inventory_score=inventory_score,
            )
            product_unknowns = []
            for u in engine_result.get("unknowns", []):
                product_unknowns.append({"field": u.get("field"), "unknown_priority": self._map_unknown_priority(u.get("severity", "LOW")), "action": u.get("action"), "notes": u.get("notes"), "product_id": product.product_id})
            product_conflicts = list(engine_result.get("conflicts", []))
            inferences = self._build_inferences(engine_result, decision_state, product.product_id)
            eligibility = self._map_eligibility(engine_result, decision_state, need_match, product_unknowns=product_unknowns)
            final_score = engine_result.get("final_score", 0.0)
            rationale = engine_result.get("rationale", "")
            trace_evidence_refs = list(engine_result.get("evidence_refs", []))
            trace_warnings = list(engine_result.get("warnings", []))
            if eligibility != "ELIGIBLE" and not trace_warnings:
                trace_warnings.append(f"Recommendation gated: {eligibility}")
            profile_fact_context = decision_state.get("profile_fact_context") or {}
            ranking_reasons = (
                f"{rationale} | needs={needs} | need_match={need_match:.2f} | "
                f"medical_context={decision_state['medical_context_active']} | "
                f"decision_status={decision_state['decision_status']} | "
                f"product_unknowns={len(product_unknowns)} | product_conflicts={len(product_conflicts)} | "
                f"inferences={len(inferences)} | need_mappings={len(decision_state.get('need_mappings') or [])} | "
                f"unmapped_need_factors={len(decision_state.get('unmapped_need_factors') or [])} | "
                f"ambiguous_need_factors={len(decision_state.get('ambiguous_need_factors') or [])} | "
                f"profile_fact_trace={json.dumps(profile_fact_context, ensure_ascii=False, sort_keys=True)}"
            )
            if eligibility != "ELIGIBLE":
                continue
            rec = self._upsert_current_recommendation(
                case_id=case_id, product_id=product.product_id, need_match=need_match,
                evidence_score=evidence_score, eligibility=eligibility, ranking_score=final_score,
                ranking_reasons=ranking_reasons, exclusion_reasons="",
                evidence_refs=trace_evidence_refs, warnings=trace_warnings,
            )
            kept_product_ids.add(product.product_id)
            recommendations.append(rec)
        for old in existing_case_recs:
            if old.product_id not in kept_product_ids:
                self.db.delete(old)
        self.db.flush()
        if len(decision_state.get("unknowns", [])) != case_unknowns_before_loop:
            logger.error("GAP-01 violation: Case Decision State unknowns mutated during product loop")
        recommendations.sort(key=lambda r: (r.ranking_score or 0.0), reverse=True)
        return recommendations
