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
        """
        منطق قطعی ساده برای Phase 1:
        اگر محصول VERIFIED باشد و موجودی داشته باشد، امتیاز پایه 0.75 می‌گیرد.
        (در آینده می‌توان بر اساس skin_type و claims گسترش داد)
        """
        # منطق قطعی و قابل توضیح
        base_score = 0.75
        return base_score
