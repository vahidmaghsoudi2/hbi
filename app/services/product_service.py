from typing import Optional, List
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
