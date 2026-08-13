from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.inventory import Inventory
from app.repositories.base import BaseRepository

class InventoryRepository(BaseRepository[Inventory]):
    def __init__(self, db: Session):
        super().__init__(Inventory, db)

    def find_by_product(self, product_id: str) -> Optional[Inventory]:
        return self.db.query(Inventory).filter(Inventory.product_id == product_id).first()

    def find_available(self) -> List[Inventory]:
        return self.db.query(Inventory).filter(Inventory.stock_status == "AVAILABLE").all()

    def update_quantity(self, product_id: str, quantity: int) -> Optional[Inventory]:
        inventory = self.find_by_product(product_id)
        if inventory:
            inventory.quantity_available = quantity
            self.db.flush()
        return inventory
