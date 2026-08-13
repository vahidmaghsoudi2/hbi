from typing import List
from sqlalchemy.orm import Session
from app.models.sale_item import SaleItem
from app.repositories.base import BaseRepository

class SaleItemRepository(BaseRepository[SaleItem]):
    def __init__(self, db: Session):
        super().__init__(SaleItem, db)

    def find_by_sale(self, sale_id: str) -> List[SaleItem]:
        return self.db.query(SaleItem).filter(SaleItem.sale_id == sale_id).all()

    def find_by_product(self, product_id: str) -> List[SaleItem]:
        return self.db.query(SaleItem).filter(SaleItem.product_id == product_id).all()
