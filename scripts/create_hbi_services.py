import os
from pathlib import Path

BASE_DIR = Path(r"E:\HBI")
SERVICES_DIR = BASE_DIR / "app" / "services"
TESTS_DIR = BASE_DIR / "tests"

SERVICES_DIR.mkdir(parents=True, exist_ok=True)
TESTS_DIR.mkdir(parents=True, exist_ok=True)

files = {}

files["__init__.py"] = '''from .base import BaseService
from .product_service import ProductService
from .customer_service import CustomerService
from .case_service import CaseService
from .recommendation_service import RecommendationService
from .inventory_service import InventoryService
from .sale_service import SaleService

__all__ = [
    "BaseService",
    "ProductService",
    "CustomerService",
    "CaseService",
    "RecommendationService",
    "InventoryService",
    "SaleService",
]
'''

files["base.py"] = '''from typing import Generic, TypeVar, Optional, List
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)
RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)

class BaseService(Generic[ModelType, RepositoryType]):
    def __init__(self, repository: RepositoryType, db: Session):
        self.repository = repository
        self.db = db

    def get_by_id(self, id: str) -> Optional[ModelType]:
        return self.repository.get_by_id(id)

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return self.repository.get_all(skip, limit)

    def create(self, **kwargs) -> ModelType:
        return self.repository.create(**kwargs)

    def update(self, id: str, **kwargs) -> Optional[ModelType]:
        return self.repository.update(id, **kwargs)

    def delete(self, id: str) -> bool:
        return self.repository.delete(id)

    def count(self) -> int:
        return self.repository.count()
'''

files["product_service.py"] = '''from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.services.base import BaseService

class ProductService(BaseService[Product, ProductRepository]):
    def __init__(self, db: Session):
        super().__init__(ProductRepository(db), db)

    def find_by_brand(self, brand: str) -> List[Product]:
        return self.repository.find_by_brand(brand)

    def find_by_identity_status(self, status: str) -> List[Product]:
        return self.repository.find_by_identity_status(status)

    def find_by_qa_verdict(self, verdict: str) -> List[Product]:
        return self.repository.find_by_qa_verdict(verdict)

    def get_with_inventory(self, product_id: str) -> Optional[Product]:
        return self.repository.get_with_inventory(product_id)

    def get_verified_products(self) -> List[Product]:
        return self.repository.find_by_identity_status("VERIFIED")

    def get_products_with_valid_qa(self) -> List[Product]:
        return self.repository.find_by_qa_verdict("VALID")
'''

files["customer_service.py"] = '''from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.repositories.customer_repository import CustomerRepository
from app.services.base import BaseService
from datetime import datetime

class CustomerService(BaseService[Customer, CustomerRepository]):
    def __init__(self, db: Session):
        super().__init__(CustomerRepository(db), db)

    def find_by_mobile(self, mobile: str) -> Optional[Customer]:
        return self.repository.find_by_mobile(mobile)

    def find_by_name(self, name: str) -> List[Customer]:
        return self.repository.find_by_name(name)

    def get_with_cases(self, customer_id: str) -> Optional[Customer]:
        return self.repository.get_with_cases(customer_id)

    def register_customer(self, name: str, mobile: Optional[str] = None, **kwargs) -> Customer:
        if mobile:
            existing = self.find_by_mobile(mobile)
            if existing:
                raise ValueError(f"Customer with mobile {mobile} already exists")

        consent = kwargs.get("consent_to_store_data", 0)
        if consent not in (0, 1):
            raise ValueError("consent_to_store_data must be 0 or 1")

        if consent == 1 and "consent_date" not in kwargs:
            kwargs["consent_date"] = datetime.now()

        customer = self.create(
            customer_id=f"CUST_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            name=name,
            mobile=mobile,
            **kwargs
        )
        return customer
'''

files["case_service.py"] = '''from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.case import Case
from app.repositories.case_repository import CaseRepository
from app.services.base import BaseService
from datetime import datetime

class CaseService(BaseService[Case, CaseRepository]):
    def __init__(self, db: Session):
        super().__init__(CaseRepository(db), db)

    def find_by_customer(self, customer_id: str) -> List[Case]:
        return self.repository.find_by_customer(customer_id)

    def find_by_case_type(self, case_type: str) -> List[Case]:
        return self.repository.find_by_case_type(case_type)

    def get_with_recommendations(self, case_id: str) -> Optional[Case]:
        return self.repository.get_with_recommendations(case_id)

    def create_case(self, customer_id: str, case_type: str = "OPEN") -> Case:
        case_id = f"CASE_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return self.create(
            case_id=case_id,
            customer_id=customer_id,
            case_type=case_type
        )

    def close_case(self, case_id: str) -> Optional[Case]:
        return self.update(case_id, case_type="CLOSED")
'''

files["recommendation_service.py"] = '''from typing import Optional, List, Dict
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
'''

files["inventory_service.py"] = '''from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.inventory import Inventory
from app.repositories.inventory_repository import InventoryRepository
from app.services.base import BaseService

class InventoryService(BaseService[Inventory, InventoryRepository]):
    def __init__(self, db: Session):
        super().__init__(InventoryRepository(db), db)

    def find_by_product(self, product_id: str) -> Optional[Inventory]:
        return self.repository.find_by_product(product_id)

    def find_available(self) -> List[Inventory]:
        return self.repository.find_available()

    def update_quantity(self, product_id: str, quantity: int) -> Optional[Inventory]:
        return self.repository.update_quantity(product_id, quantity)

    def reserve_stock(self, product_id: str, quantity: int) -> bool:
        inventory = self.find_by_product(product_id)
        if not inventory:
            return False
        available = inventory.quantity_available - inventory.quantity_reserved
        if available < quantity:
            return False
        inventory.quantity_reserved += quantity
        self.db.flush()
        return True

    def release_stock(self, product_id: str, quantity: int) -> bool:
        inventory = self.find_by_product(product_id)
        if not inventory:
            return False
        if inventory.quantity_reserved < quantity:
            return False
        inventory.quantity_reserved -= quantity
        self.db.flush()
        return True

    def confirm_sale(self, product_id: str, quantity: int) -> bool:
        """تأیید فروش: کاهش available و reserved"""
        inventory = self.find_by_product(product_id)
        if not inventory:
            return False
        if inventory.quantity_available < quantity:
            return False

        inventory.quantity_available -= quantity
        if inventory.quantity_reserved >= quantity:
            inventory.quantity_reserved -= quantity
        else:
            inventory.quantity_reserved = 0

        if inventory.quantity_available == 0:
            inventory.stock_status = "OUT_OF_STOCK"
        self.db.flush()
        return True
'''

files["sale_service.py"] = '''from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.repositories.sale_repository import SaleRepository
from app.repositories.sale_item_repository import SaleItemRepository
from app.services.base import BaseService
from app.services.inventory_service import InventoryService
from datetime import datetime

class SaleService(BaseService[Sale, SaleRepository]):
    def __init__(self, db: Session):
        super().__init__(SaleRepository(db), db)
        self.sale_item_repo = SaleItemRepository(db)
        self.inventory_service = InventoryService(db)

    def find_by_customer(self, customer_id: str) -> List[Sale]:
        return self.repository.find_by_customer(customer_id)

    def find_with_items(self, sale_id: str) -> Optional[Sale]:
        return self.repository.find_with_items(sale_id)

    def get_total_sales(self) -> int:
        return self.repository.get_total_sales()

    def create_sale(self, customer_id: str, items: list) -> Sale:
        if not items:
            raise ValueError("Sale must have at least one item")

        sale_id = f"SALE_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        total_amount = 0

        sale = self.create(
            sale_id=sale_id,
            customer_id=customer_id,
            total_amount_toman=0
        )

        for item_data in items:
            product_id = item_data["product_id"]
            quantity = item_data["quantity"]
            unit_price = item_data["unit_price_toman"]

            if not self.inventory_service.reserve_stock(product_id, quantity):
                raise ValueError(f"Insufficient stock for product {product_id}")

            item_id = f"SI_{datetime.now().strftime('%Y%m%d%H%M%S')}_{product_id}"
            self.sale_item_repo.create(
                sale_item_id=item_id,
                sale_id=sale.sale_id,
                product_id=product_id,
                quantity=quantity,
                unit_price_toman=unit_price
            )
            total_amount += quantity * unit_price
            self.inventory_service.confirm_sale(product_id, quantity)

        self.update(sale.sale_id, total_amount_toman=total_amount)
        return sale

    def get_sale_items(self, sale_id: str) -> List[SaleItem]:
        return self.sale_item_repo.find_by_sale(sale_id)
'''

# نوشتن فایل‌ها
for filename, content in files.items():
    path = SERVICES_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created/Updated: {path}")

print()
print("=" * 60)
print("GATE 6-3 Service Layer (corrected) created successfully.")
print("=" * 60)