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
from app.reasoning.reasoning_engine import ReasoningEngine
from app.reasoning.conflict_analyzer import ConflictSeverity

logger = logging.getLogger(__name__)

# Source-type weights used only to *collect* evidence_score input for the engine.
# Scoring formula itself lives in MatchScoringEngine / ReasoningEngine (FROZEN).
_EVIDENCE_WEIGHTS = {
    "PEER_REVIEWED": 1.0,
    "CLINICAL_TRIAL": 1.0,
    "REGULATORY": 1.0,
    "OFFICIAL_MANUFACTURER": 0.6,
    "MANUFACTURER": 0.6,
    "REPUTABLE_RETAILER": 0.4,
    "SECONDARY": 0.2,
}

# F2 Design thresholds
NEED_MATCH_SUFFICIENT = 0.40

# Medical Context trigger tokens (MVP-safe, non-diagnostic)
_MEDICAL_TOKENS = {
    "پزشک", "دکتر", "نسخه", "دارو", "بیماری", "حساسیت شدید",
    "بارداری", "شیردهی", "تحت درمان", "doctor", "prescription",
    "pregnancy", "breastfeeding", "medication", "disease"
}


class RecommendationService(BaseService[Recommendation, RecommendationRepository]):
    """
    RecommendationService — F2 Implementation

    Responsibilities:
    - Build Decision State Computed Snapshot
    - Generate Need only from Decision State
    - Map UnknownPriority from ConflictSeverity
    - Detect minimal Medical Context
    - Produce Inference as computed output
    - Call ReasoningEngine.run for real scoring
    - Produce Recommendation with proper eligibility
    """

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

    # ------------------------------------------------------------------
    # F2 Helpers
    # ------------------------------------------------------------------

    def _map_unknown_priority(self, severity: str) -> str:
        """Derived mapping only. ConflictSeverity stays independent."""
        if severity == ConflictSeverity.CRITICAL.value:
            return "CRITICAL_UNKNOWN"
        if severity == ConflictSeverity.HIGH.value:
            return "IMPORTANT_UNKNOWN"
        return "OPTIONAL_UNKNOWN"

    def _detect_medical_context(self, customer_profile: Dict, factors: List[Dict]) -> tuple:
        """Minimal MVP trigger. Never diagnoses."""
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

    def _build_decision_state(
        self,
        case_id: str,
        customer_profile: Dict,
    ) -> Dict[str, Any]:
        """Build the Decision State Computed Snapshot (F2)."""
        raw_concerns = []
        concerns_raw = customer_profile.get("concerns") or ""
        if isinstance(concerns_raw, list):
            raw_concerns = [str(c).strip() for c in concerns_raw if c and str(c).strip()]
        else:
            raw_concerns = [c.strip() for c in str(concerns_raw).split(",") if c.strip()]

        factors = []
        for c in raw_concerns:
            factors.append({
                "name": "concern",
                "value": c,
                "source": "customer_input",
                "validity": "DECLARED",
            })

        medical_active, medical_notes = self._detect_medical_context(customer_profile, factors)

        decision_state = {
            "case_id": case_id,
            "customer_id": customer_profile.get("customer_id"),
            "raw_concerns": raw_concerns,
            "evidence_refs": [],
            "evidence_gaps": [],
            "unknowns": [],
            "conflicts": [],
            "factors": factors,
            "inferences": [],
            "medical_context_active": medical_active,
            "medical_context_notes": medical_notes,
            "needs": [],
            "need_match": 0.0,
            "confidence": 0.0,
            "decision_status": "READY",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        return decision_state

    def _generate_needs_from_decision_state(self, decision_state: Dict[str, Any]) -> List[str]:
        """Need is produced ONLY from Decision State (F2 hard rule)."""
        needs = []
        for f in decision_state.get("factors", []):
            val = (f.get("value") or "").strip()
            if val and val not in needs:
                needs.append(val)
        return needs

    def _calculate_need_match(self, generated_needs: List[str], known_use_cases: Optional[str]) -> float:
        if not generated_needs:
            return 0.0
        need_tokens = set()
        for n in generated_needs:
            need_tokens |= self._normalize_tokens(n)
        use_tokens = self._normalize_tokens(known_use_cases or "")
        if not need_tokens:
            return 0.0
        intersection = need_tokens & use_tokens
        return round(len(intersection) / max(len(need_tokens), 1), 4)

    def _compute_evidence_score(self, evidences: List[Evidence]) -> float:
        if not evidences:
            return 0.0
        total = 0.0
        for ev in evidences:
            st = (ev.source_type or "SECONDARY").upper()
            total += _EVIDENCE_WEIGHTS.get(st, 0.2)
        return round(min(1.0, total / len(evidences)), 4)

    def _build_inferences(
        self,
        engine_result: Dict[str, Any],
        decision_state: Dict[str, Any],
        product_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Produce Inference as computed reasoning output (F2).
        Never stored as Fact. Never diagnoses.
        """
        inferences: List[Dict[str, Any]] = []

        for u in engine_result.get("unknowns", []):
            inferences.append({
                "statement": f"Unknown on field '{u.get('field')}' requires attention",
                "confidence": 0.5,
                "based_on_evidence_refs": [],
                "based_on_factors": [],
                "source": "engine_unknown",
                "product_id": product_id,
            })

        for v in engine_result.get("claim_boundary_violations", []):
            inferences.append({
                "statement": f"Claim boundary violation detected: {v.get('reason', 'unspecified')}",
                "confidence": 0.6,
                "based_on_evidence_refs": [],
                "based_on_factors": [],
                "source": "claim_validator",
                "product_id": product_id,
            })

        if decision_state.get("medical_context_active"):
            inferences.append({
                "statement": "Medical context present — professional review may be required",
                "confidence": 0.7,
                "based_on_evidence_refs": [],
                "based_on_factors": [f.get("value") for f in decision_state.get("factors", [])],
                "source": "medical_context_trigger",
                "product_id": product_id,
            })

        return inferences

    def _map_eligibility(
        self,
        engine_result: Dict[str, Any],
        decision_state: Dict[str, Any],
        need_match: float,
    ) -> str:
        """Map to statuses compatible with existing DB CheckConstraint."""
        for u in decision_state.get("unknowns", []):
            if u.get("unknown_priority") == "CRITICAL_UNKNOWN":
                return "INELIGIBLE_PENDING_REVIEW"

        if decision_state.get("medical_context_active") and decision_state.get("decision_status") == "REFERRAL":
            return "INELIGIBLE_PENDING_REVIEW"

        if need_match < NEED_MATCH_SUFFICIENT or not decision_state.get("needs"):
            return "INELIGIBLE_PENDING_REVIEW"

        eng_elig = engine_result.get("eligibility") or "INELIGIBLE"
        if eng_elig == "NEEDS_REVIEW":
            return "INELIGIBLE_PENDING_REVIEW"
        if eng_elig == "ELIGIBLE":
            return "ELIGIBLE"
        return "INELIGIBLE_PENDING_REVIEW"

    # ------------------------------------------------------------------
    # Main entry
    # ------------------------------------------------------------------

    def generate_recommendations(self, case_id: str, customer_profile: Dict = None) -> List[Recommendation]:
        """
        F2 Implementation of Recommendation Decision Pipeline.

        Flow:
        Customer Data → Decision State → Needs → Product Intelligence
        → ReasoningEngine → Recommendation
        """
        if customer_profile is None:
            customer_profile = {}

        decision_state = self._build_decision_state(case_id, customer_profile)

        needs = self._generate_needs_from_decision_state(decision_state)
        decision_state["needs"] = needs

        if not needs:
            decision_state["decision_status"] = "INSUFFICIENT"
        if decision_state["medical_context_active"]:
            decision_state["decision_status"] = "REFERRAL" if not needs else decision_state["decision_status"]

        products = self.product_repo.find_by_identity_status_and_active("VERIFIED")
        recommendations: List[Recommendation] = []
        rank = 1

        for product in products:
            pk = self.pk_repo.find_by_product(product.product_id)
            known_use_cases = pk.known_use_cases if pk else None
            evidences = self.evidence_repo.find_by_product(product.product_id)

            inv = self.inventory_repo.find_by_product(product.product_id)
            inventory_score = 1.0 if (inv and inv.quantity_available and inv.quantity_available > 0) else 0.0

            need_match = self._calculate_need_match(needs, known_use_cases)
            evidence_score = self._compute_evidence_score(evidences)

            evidence_list = []
            for ev in evidences:
                evidence_list.append({
                    "evidence_id": ev.evidence_id,
                    "claim_id": ev.claim_id,
                    "field": ev.field,
                    "claim_type": ev.claim_type,
                    "source_reference": ev.source_reference,
                    "source_type": ev.source_type,
                    "evidence_strength": ev.evidence_strength,
                    "qa_status": ev.qa_status,
                    "claim": ev.claim,
                })

            pk_snapshot = {}
            if pk:
                pk_snapshot = {
                    "known_use_cases": pk.known_use_cases,
                    "claimed_benefits": pk.claimed_benefits,
                    "contraindications": pk.contraindications,
                    "ingredients": pk.ingredients,
                }

            engine_result = self.reasoning_engine.run(
                product_id=product.product_id,
                product_knowledge_snapshot=pk_snapshot,
                evidence_list=evidence_list,
                need_match=need_match,
                evidence_score=evidence_score,
                inventory_score=inventory_score,
            )

            for u in engine_result.get("unknowns", []):
                sev = u.get("severity", "LOW")
                decision_state["unknowns"].append({
                    "field": u.get("field"),
                    "unknown_priority": self._map_unknown_priority(sev),
                    "action": u.get("action"),
                    "notes": u.get("notes"),
                })
            decision_state["conflicts"].extend(engine_result.get("conflicts", []))

            # F2: Inference as computed output
            inferences = self._build_inferences(engine_result, decision_state, product.product_id)
            decision_state["inferences"] = inferences

            eligibility = self._map_eligibility(engine_result, decision_state, need_match)

            final_score = engine_result.get("final_score", 0.0)
            rationale = engine_result.get("rationale", "")
            ranking_reasons = (
                f"{rationale} | needs={needs} | need_match={need_match:.2f} | "
                f"medical_context={decision_state['medical_context_active']} | "
                f"decision_status={decision_state['decision_status']} | "
                f"inferences={len(inferences)}"
            )

            rec = Recommendation(
                recommendation_id=f"rec_{case_id}_{product.product_id}_{rank}",
                case_id=case_id,
                product_id=product.product_id,
                need_match_score=need_match,
                evidence_score=evidence_score,
                eligibility_status=eligibility,
                ranking_score=final_score,
                ranking_reasons=ranking_reasons[:2000] if ranking_reasons else "",
                exclusion_reasons="",
            )
            recommendations.append(rec)
            rank += 1

        recommendations.sort(key=lambda r: (r.ranking_score or 0.0), reverse=True)
        return recommendations
