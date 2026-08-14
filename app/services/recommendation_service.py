from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from app.models.recommendation import Recommendation
from app.models.product import Product
from app.repositories.recommendation_repository import RecommendationRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.inventory_repository import InventoryRepository
from app.services.base import BaseService
from datetime import datetime

class RecommendationService(BaseService[Recommendation, RecommendationRepository]):
    def __init__(self, db: Session):
        super().__init__(RecommendationRepository(db), db)
        self.product_repo = ProductRepository(db)
        self.inventory_repo = InventoryRepository(db)

    def find_by_case(self, case_id: str) -> List[Recommendation]:
        return self.repository.find_by_case(case_id)

    def find_by_product(self, product_id: str) -> List[Recommendation]:
        return self.repository.find_by_product(product_id)

    def find_eligible(self) -> List[Recommendation]:
        return self.repository.find_eligible()

    def generate_recommendations(self, case_id: str, customer_profile: Dict) -> List[Recommendation]:
        """
        تولید توصیه بر اساس منطق ساده و قطعی:
        - فقط محصولات VERIFIED
        - فقط محصولات با موجودی > 0
        - امتیاز بر اساس تطابق ساده با پروفایل (فعلاً امتیاز ثابت قابل توضیح)
        """
        products = self.product_repo.find_by_identity_status("VERIFIED")
        recommendations = []
        rank = 1

        for product in products:
            inventory = self.inventory_repo.find_by_product(product.product_id)
            if not inventory or inventory.quantity_available <= 0:
                continue

            match_score = self._calculate_match_score(product, customer_profile)

            if match_score >= 0.5:
                rec_id = f"REC_{datetime.now().strftime('%Y%m%d%H%M%S')}_{rank}"
                eligibility = "ELIGIBLE" if match_score >= 0.7 else "INELIGIBLE_PENDING_VERIFICATION"

                recommendation = self.create(
                    recommendation_id=rec_id,
                    case_id=case_id,
                    product_id=product.product_id,
                    need_match_score=match_score,
                    eligibility_status=eligibility,
                    ranking_score=match_score,
                    ranking_reasons=f"Deterministic match score based on available verified product: {match_score:.2f}"
                )
                recommendations.append(recommendation)
                rank += 1

        return recommendations

    def _calculate_match_score(self, product: Product, profile: Dict) -> float:
        """Uses MatchScoringEngine. Replaces placeholder base_score=0.75."""
        from app.reasoning.scoring import MatchScoringEngine
        eng = MatchScoringEngine()

        # need_match: keyword matching concerns vs known_use_cases
        concerns = profile.get("concerns", "")
        if isinstance(concerns, str):
            concerns = [c.strip().lower() for c in concerns.split(",") if c.strip()]
        need = 0.0
        if concerns:
            try:
                from app.models.product_knowledge import ProductKnowledge
                pk = self.db.query(ProductKnowledge).filter_by(
                    product_id=product.product_id).first()
                if pk and pk.known_use_cases:
                    uc = [u.strip().lower() for u in pk.known_use_cases.split(",")]
                    need = round(len(set(concerns) & set(uc)) / len(concerns), 2)
            except Exception:
                pass

        # evidence_score: from Evidence table (0.0 if none -> Hard Gate)
        ev_score = 0.0
        try:
            from app.models.evidence import Evidence
            evs = self.db.query(Evidence).filter_by(
                product_id=product.product_id).all()
            weights = {
                "PEER_REVIEWED": 1.0, "CLINICAL_TRIAL": 1.0, "REGULATORY": 1.0,
                "OFFICIAL_MANUFACTURER": 0.6, "MANUFACTURER": 0.6,
                "REPUTABLE_RETAILER": 0.4, "SECONDARY": 0.2,
            }
            for e in evs:
                s = weights.get((e.source_type or "").upper(), 0.0)
                if s > ev_score:
                    ev_score = s
        except Exception:
            pass

        # inventory_score
        inv = self.inventory_repo.find_by_product(product.product_id)
        inv_score = 1.0 if inv and inv.quantity_available > 0 else 0.0

        result = eng.calculate(need, ev_score, inv_score)
        return result["final_score"]
