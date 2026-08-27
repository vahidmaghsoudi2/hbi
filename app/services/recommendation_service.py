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
from app.services.base import BaseService
from app.reasoning.reasoning_engine import ReasoningEngine

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


class RecommendationService(BaseService[Recommendation, RecommendationRepository]):
    """
    RecommendationService — thin orchestration layer.

    Responsibilities:
    - Collect verified products + inventory + evidence + knowledge snapshots
    - Call ReasoningEngine.run() for scoring / conflict / claim checks
    - Persist Recommendation rows based on engine output

    Does NOT contain match-score or evidence-score calculation logic.
    """

    def __init__(self, db: Session):
        super().__init__(RecommendationRepository(db), db)
        self.product_repo = ProductRepository(db)
        self.inventory_repo = InventoryRepository(db)
        self.reasoning_engine = ReasoningEngine()

    def find_by_case(self, case_id: str) -> List[Recommendation]:
        return self.repository.find_by_case(case_id)

    def find_by_product(self, product_id: str) -> List[Recommendation]:
        return self.repository.find_by_product(product_id)

    def find_eligible(self) -> List[Recommendation]:
        return self.repository.find_eligible()

    def generate_recommendations(
        self, case_id: str, customer_profile: Dict
    ) -> List[Recommendation]:
        """
        Generate recommendations via ReasoningEngine.

        Flow:
        1. Load VERIFIED products with available inventory
        2. For each product: gather PK snapshot + evidence list + input scores
        3. Call ReasoningEngine.run(...)
        4. Create Recommendation from engine result (final_score, eligibility, ...)
        """
        products = [p for p in self.product_repo.find_by_identity_status("VERIFIED") if p.status == "ACTIVE"]
        recommendations: List[Recommendation] = []
        rank = 1

        concerns = customer_profile.get("concerns", "")
        if isinstance(concerns, str):
            concern_list = [c.strip().lower() for c in concerns.split(",") if c.strip()]
        else:
            concern_list = [str(c).strip().lower() for c in (concerns or []) if str(c).strip()]

        for product in products:
            inventory = self.inventory_repo.find_by_product(product.product_id)
            if not inventory or inventory.quantity_available <= 0:
                continue

            # --- Data collection only (no scoring formula here) ---
            pk_snapshot = self._collect_product_knowledge_snapshot(product.product_id)
            evidence_list = self._collect_evidence_list(product.product_id)

            need_match = self._compute_need_match(concern_list, pk_snapshot)
            evidence_score = self._max_evidence_weight(evidence_list)
            inventory_score = 1.0 if inventory.quantity_available > 0 else 0.0

            engine_result = self.reasoning_engine.run(
                product_id=product.product_id,
                product_knowledge_snapshot=pk_snapshot,
                evidence_list=evidence_list,
                need_match=need_match,
                evidence_score=evidence_score,
                inventory_score=inventory_score,
            )

            final_score = float(engine_result.get("final_score", 0.0))
            eligibility = engine_result.get("eligibility", "INELIGIBLE")
            rationale = engine_result.get("rationale", "")

            # Hard filter: only persist if score meets minimum threshold
            if final_score < 0.5:
                continue

            rec_id = f"REC_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{rank}"

            recommendation = self.create(
                recommendation_id=rec_id,
                case_id=case_id,
                product_id=product.product_id,
                need_match_score=need_match,
                evidence_score=evidence_score,
                eligibility_status=eligibility,
                ranking_score=final_score,
                ranking_reasons=rationale,
            )
            recommendations.append(recommendation)
            rank += 1

        return recommendations

    # ─── Data collectors (no scoring formula) ─────────────────

    def _collect_product_knowledge_snapshot(self, product_id: str) -> Dict[str, Any]:
        try:
            pk = (
                self.db.query(ProductKnowledge)
                .filter_by(product_id=product_id)
                .first()
            )
            if not pk:
                return {}
            return {
                "product_knowledge_id": pk.product_knowledge_id,
                "known_use_cases": pk.known_use_cases,
                "claimed_benefits": pk.claimed_benefits,
                "ingredients": pk.ingredients,
                "evidence_status": pk.evidence_status,
                "knowledge_confidence": pk.knowledge_confidence,
            }
        except Exception as exc:
            logger.error(
                "Failed to collect ProductKnowledge for %s: %s",
                product_id,
                exc,
                exc_info=True,
            )
            return {}

    def _collect_evidence_list(self, product_id: str) -> List[Dict[str, Any]]:
        try:
            rows = self.db.query(Evidence).filter_by(product_id=product_id).all()
            return [
                {
                    "evidence_id": e.evidence_id,
                    "claim_id": e.claim_id,
                    "field": e.field,
                    "claim": e.claim,
                    "claim_type": e.claim_type,
                    "source_type": e.source_type,
                    "source_reference": e.source_reference,
                    "evidence_strength": e.evidence_strength,
                    "qa_status": e.qa_status,
                }
                for e in rows
            ]
        except Exception as exc:
            logger.error(
                "Failed to collect Evidence for %s: %s",
                product_id,
                exc,
                exc_info=True,
            )
            return []

    def _compute_need_match(
        self, concern_list: List[str], pk_snapshot: Dict[str, Any]
    ) -> float:
        """Simple keyword overlap — input preparation only, not final scoring."""
        if not concern_list:
            return 0.0
        raw = pk_snapshot.get("known_use_cases") or ""
        use_cases = [u.strip().lower() for u in raw.split(",") if u.strip()]
        if not use_cases:
            return 0.0
        overlap = len(set(concern_list) & set(use_cases))
        return round(overlap / len(concern_list), 2)

    def _max_evidence_weight(self, evidence_list: List[Dict[str, Any]]) -> float:
        """Max source-type weight — input preparation for the engine."""
        mx = 0.0
        for e in evidence_list:
            w = _EVIDENCE_WEIGHTS.get((e.get("source_type") or "").upper(), 0.0)
            if w > mx:
                mx = w
        return mx

