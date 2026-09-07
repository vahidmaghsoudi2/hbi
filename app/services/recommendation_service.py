import logging
from typing import Optional, List, Dict, Any

from sqlalchemy.orm import Session

from app.models.recommendation import Recommendation
from app.models.product_knowledge import ProductKnowledge
from app.models.evidence import Evidence
from app.repositories.recommendation_repository import RecommendationRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.evidence_repository import EvidenceRepository
from app.repositories.product_knowledge_repository import ProductKnowledgeRepository
from app.services.base import BaseService
from app.reasoning.reasoning_engine import ReasoningEngine
from app.reasoning.scoring_constants import (
    ELIGIBILITY_ELIGIBLE,
    ELIGIBILITY_NEEDS_REVIEW,
    ELIGIBILITY_INELIGIBLE,
    INVENTORY_SCORE_AVAILABLE,
    INVENTORY_SCORE_UNAVAILABLE,
)

logger = logging.getLogger(__name__)

# Source-type weights used only to *collect* evidence_score input for the engine.
# Scoring formula itself lives in MatchScoringEngine / ReasoningEngine.
_EVIDENCE_WEIGHTS = {
    "PEER_REVIEWED": 1.0,
    "CLINICAL_TRIAL": 1.0,
    "REGULATORY": 1.0,
    "OFFICIAL_MANUFACTURER": 0.6,
    "MANUFACTURER": 0.6,
    "REPUTABLE_RETAILER": 0.4,
    "SECONDARY": 0.2,
}

# Recommendation.eligibility_status CHECK constraint values (schema-locked).
_STATUS_ELIGIBLE = "ELIGIBLE"
_STATUS_PENDING_REVIEW = "INELIGIBLE_PENDING_REVIEW"
_STATUS_OUT_OF_STOCK = "INELIGIBLE_OUT_OF_STOCK"
_STATUS_CONFLICT = "INELIGIBLE_CONFLICT"


class RecommendationService(BaseService[Recommendation, RecommendationRepository]):
    """
    RecommendationService — thin orchestration layer.

    Responsibilities:
    - Collect verified products + inventory + evidence + knowledge snapshots
    - Call ReasoningEngine.run() for scoring / conflict / claim checks
    - Build in-memory Recommendation rows from engine output

    Does NOT own the scoring formula (that lives in ReasoningEngine / MatchScoringEngine).
    """

    def __init__(self, db: Session):
        super().__init__(RecommendationRepository(db), db)
        self.product_repo = ProductRepository(db)
        self.inventory_repo = InventoryRepository(db)
        self.evidence_repo = EvidenceRepository(db)
        self.knowledge_repo = ProductKnowledgeRepository(db)
        self.reasoning_engine = ReasoningEngine()

    def find_by_case(self, case_id: str) -> List[Recommendation]:
        return self.repository.find_by_case(case_id)

    def find_by_product(self, product_id: str) -> List[Recommendation]:
        return self.repository.find_by_product(product_id)

    def find_eligible(self) -> List[Recommendation]:
        return self.repository.find_eligible()

    def generate_recommendations(
        self, case_id: str, customer_profile: Dict = None
    ) -> List[Recommendation]:
        """
        Generate recommendations via ReasoningEngine.

        Flow:
        1. Load VERIFIED products with available inventory (active, not DRAFT)
        2. For each product: gather PK snapshot + evidence list + input scores
        3. Call ReasoningEngine.run(...)
        4. Create Recommendation from engine result (scores, eligibility, rationale)
        """
        if customer_profile is None:
            customer_profile = {}

        products = self.product_repo.find_by_identity_status_and_active("VERIFIED")
        recommendations: List[Recommendation] = []
        rank = 1

        concern_list = self._parse_concerns(customer_profile)

        for product in products:
            evidence_rows = self.evidence_repo.find_by_product(product.product_id)
            evidence_list = [self._evidence_to_dict(ev) for ev in evidence_rows]
            knowledge = self.knowledge_repo.find_by_product(product.product_id)
            pk_snapshot = self._knowledge_snapshot(knowledge, product)
            inventory = self.inventory_repo.find_by_product(product.product_id)

            need_match = self._compute_need_match(concern_list, product, knowledge)
            evidence_score = self._compute_evidence_score(evidence_rows)
            inventory_score = self._compute_inventory_score(inventory)

            result = self.reasoning_engine.run(
                product_id=product.product_id,
                product_knowledge_snapshot=pk_snapshot,
                evidence_list=evidence_list,
                existing_conflicts=[],
                need_match=need_match,
                evidence_score=evidence_score,
                inventory_score=inventory_score,
            )

            eligibility_status = self._map_eligibility(result, inventory_score)
            ranking_score = float(result.get("final_score") or 0.0)
            ranking_reasons = (result.get("rationale") or "")[:2000]
            exclusion_reasons = self._exclusion_reasons(result)

            rec = Recommendation(
                recommendation_id=f"rec_{case_id}_{product.product_id}_{rank}",
                case_id=case_id,
                product_id=product.product_id,
                need_match_score=float(result.get("need_match") if result.get("need_match") is not None else need_match),
                evidence_score=float(result.get("evidence_score") if result.get("evidence_score") is not None else evidence_score),
                eligibility_status=eligibility_status,
                ranking_score=ranking_score,
                ranking_reasons=ranking_reasons,
                exclusion_reasons=exclusion_reasons,
            )
            recommendations.append(rec)
            rank += 1

        recommendations.sort(
            key=lambda r: (r.ranking_score is not None, r.ranking_score or 0.0),
            reverse=True,
        )
        return recommendations

    @staticmethod
    def _parse_concerns(customer_profile: Dict) -> List[str]:
        concerns_raw = customer_profile.get("concerns") or ""
        if isinstance(concerns_raw, list):
            return [c.strip().lower() for c in concerns_raw if c and str(c).strip()]
        return [c.strip().lower() for c in str(concerns_raw).split(",") if c.strip()]

    @staticmethod
    def _evidence_to_dict(ev: Evidence) -> Dict[str, Any]:
        return {
            "evidence_id": ev.evidence_id,
            "claim_id": ev.claim_id,
            "field": ev.field,
            "claim": ev.claim,
            "claim_type": ev.claim_type,
            "source_type": ev.source_type,
            "source_reference": ev.source_reference,
            "evidence_strength": getattr(ev, "evidence_strength", None),
            "qa_status": getattr(ev, "qa_status", None),
        }

    @staticmethod
    def _knowledge_snapshot(knowledge: Optional[ProductKnowledge], product) -> Dict[str, Any]:
        if not knowledge:
            return {
                "product_id": product.product_id,
                "brand": getattr(product, "brand", None),
                "product_name": getattr(product, "product_name", None),
            }
        return {
            "product_id": knowledge.product_id,
            "ingredients": knowledge.ingredients,
            "claimed_benefits": knowledge.claimed_benefits,
            "known_use_cases": knowledge.known_use_cases,
            "contraindications": knowledge.contraindications,
            "evidence_refs": knowledge.evidence_refs,
            "knowledge_confidence": knowledge.knowledge_confidence,
            "brand": getattr(product, "brand", None),
            "product_name": getattr(product, "product_name", None),
        }

    @staticmethod
    def _compute_need_match(
        concern_list: List[str], product, knowledge: Optional[ProductKnowledge]
    ) -> float:
        """Simple token-overlap input for the engine (not the final ranking formula)."""
        if not concern_list:
            return 0.5
        corpus_parts = [
            getattr(product, "product_name", None) or "",
            getattr(product, "brand", None) or "",
        ]
        if knowledge:
            corpus_parts.extend(
                [
                    knowledge.known_use_cases or "",
                    knowledge.claimed_benefits or "",
                    knowledge.ingredients or "",
                ]
            )
        corpus = " ".join(corpus_parts).lower()
        if not corpus.strip():
            return 0.3
        hits = sum(1 for c in concern_list if c and c in corpus)
        return round(min(1.0, hits / max(len(concern_list), 1)), 2)

    @staticmethod
    def _compute_evidence_score(evidence_rows: List[Evidence]) -> float:
        if not evidence_rows:
            return 0.0
        total = 0.0
        for ev in evidence_rows:
            st = (ev.source_type or "").upper()
            total += _EVIDENCE_WEIGHTS.get(st, 0.1)
        return round(min(1.0, total / len(evidence_rows)), 2)

    @staticmethod
    def _compute_inventory_score(inventory) -> float:
        if inventory is None:
            return INVENTORY_SCORE_UNAVAILABLE
        qty = getattr(inventory, "quantity_available", 0) or 0
        status = (getattr(inventory, "stock_status", None) or "").upper()
        if qty <= 0 or status == "OUT_OF_STOCK":
            return INVENTORY_SCORE_UNAVAILABLE
        return INVENTORY_SCORE_AVAILABLE

    @staticmethod
    def _map_eligibility(result: Dict[str, Any], inventory_score: float) -> str:
        """Map engine eligibility strings onto Recommendation CHECK constraint values."""
        if inventory_score <= 0.0:
            return _STATUS_OUT_OF_STOCK
        if result.get("conflicts"):
            high = [
                c
                for c in result["conflicts"]
                if (c.get("severity") or "").upper() in ("HIGH", "CRITICAL")
            ]
            if high:
                return _STATUS_CONFLICT
        engine_elig = (result.get("eligibility") or "").upper()
        if engine_elig == ELIGIBILITY_ELIGIBLE:
            return _STATUS_ELIGIBLE
        if engine_elig in (ELIGIBILITY_NEEDS_REVIEW, ELIGIBILITY_INELIGIBLE, ""):
            return _STATUS_PENDING_REVIEW
        return _STATUS_PENDING_REVIEW

    @staticmethod
    def _exclusion_reasons(result: Dict[str, Any]) -> str:
        parts: List[str] = []
        for w in result.get("warnings") or []:
            parts.append(str(w))
        for reason in result.get("hard_gate_reasons") or []:
            parts.append(str(reason))
        violations = result.get("claim_boundary_violations") or []
        if violations:
            parts.append(f"claim_boundary_violations={len(violations)}")
        return "; ".join(parts)[:2000]
