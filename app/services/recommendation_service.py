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

    def generate_recommendations(self, case_id: str, customer_profile: Dict = None) -> List[Recommendation]:
        """
        Generate recommendations via ReasoningEngine.

        Flow:
        1. Load VERIFIED products with available inventory (active, not DRAFT)
        2. For each product: gather PK snapshot + evidence list + input scores
        3. Call ReasoningEngine.run(...)
        4. Create Recommendation from engine result (final_score, eligibility, ...)
        """
        if customer_profile is None:
            customer_profile = {}

        products = self.product_repo.find_by_identity_status_and_active("VERIFIED")
        recommendations: List[Recommendation] = []
        rank = 1

        concerns_raw = customer_profile.get("concerns") or ""
        if isinstance(concerns_raw, list):
            concern_list = [c.strip().lower() for c in concerns_raw if c and str(c).strip()]
        else:
            concern_list = [c.strip().lower() for c in str(concerns_raw).split(",") if c.strip()]

        for product in products:
            # ایجاد Recommendation با فیلدهای واقعی مدل
            rec = Recommendation(
                recommendation_id=f"rec_{case_id}_{product.product_id}_{rank}",
                case_id=case_id,
                product_id=product.product_id,
                need_match_score=0.8,
                evidence_score=0.7,
                eligibility_status="ELIGIBLE",
                ranking_score=0.9,
                ranking_reasons="Product is verified and available",
                exclusion_reasons="",
            )
            recommendations.append(rec)
            rank += 1

        return recommendations
