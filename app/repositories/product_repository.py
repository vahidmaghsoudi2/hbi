from typing import List
from sqlalchemy.orm import Session
from app.models.product import Product
from app.repositories.base import BaseRepository

class ProductRepository(BaseRepository[Product]):
    def __init__(self, db: Session):
        super().__init__(Product, db)

    def find_by_brand(self, brand: str) -> List[Product]:
        return self.db.query(Product).filter(Product.brand.ilike(f"%{brand}%")).all()

    def find_by_identity_status(self, status: str) -> List[Product]:
        return self.db.query(Product).filter(Product.identity_status == status).all()

    def find_by_qa_verdict(self, verdict: str) -> List[Product]:
        return self.db.query(Product).filter(Product.qa_verdict == verdict).all()

    def get_with_inventory(self, product_id: str):
        return self.db.query(Product).filter(Product.product_id == product_id).first()
