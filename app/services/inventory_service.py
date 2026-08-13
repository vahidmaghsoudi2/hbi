from typing import Optional, List
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
