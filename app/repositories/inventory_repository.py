from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.inventory import Inventory
from app.repositories.base import BaseRepository


class InventoryRepository(BaseRepository[Inventory]):
    def __init__(self, db: Session):
        super().__init__(Inventory, db)

    def find_by_product(self, product_id: str) -> Optional[Inventory]:
        return self.db.query(Inventory).filter(Inventory.product_id == product_id).first()

    def find_all_records(self) -> List[Inventory]:
        return self.db.query(Inventory).order_by(Inventory.product_id).all()

    def find_available(self) -> List[Inventory]:
        """Sellable rows: quantity_available > 0 and not OUT_OF_STOCK.

        Legacy stock_status values include 'active' and 'AVAILABLE'.
        """
        return (
            self.db.query(Inventory)
            .filter(
                Inventory.quantity_available > 0,
                Inventory.stock_status != "OUT_OF_STOCK",
            )
            .all()
        )

    def update_quantity(self, product_id: str, quantity: int) -> Optional[Inventory]:
        inventory = self.find_by_product(product_id)
        if inventory:
            inventory.quantity_available = quantity
            self.db.flush()
        return inventory
