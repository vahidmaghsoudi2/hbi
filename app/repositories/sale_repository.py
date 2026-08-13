from typing import List
from sqlalchemy.orm import Session
from app.models.sale import Sale
from app.repositories.base import BaseRepository

class SaleRepository(BaseRepository[Sale]):
    def __init__(self, db: Session):
        super().__init__(Sale, db)

    def find_by_customer(self, customer_id: str) -> List[Sale]:
        return self.db.query(Sale).filter(Sale.customer_id == customer_id).all()

    def find_with_items(self, sale_id: str):
        return self.db.query(Sale).filter(Sale.sale_id == sale_id).first()

    def get_total_sales(self) -> int:
        result = self.db.query(Sale.total_amount_toman).all()
        return sum([r[0] for r in result]) if result else 0
