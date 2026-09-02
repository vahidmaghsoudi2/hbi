"""Inventory management — Phase 05.

Rules:
- quantity_available must never go negative
- mutations are atomic with optional StockMovement ledger row
- does not invent prices or FX; does not touch Product A–D seeds
"""
from __future__ import annotations

import uuid
from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.product import Product
from app.models.stock_movement import StockMovement
from app.repositories.inventory_repository import InventoryRepository
from app.services.base import BaseService


class InventoryService(BaseService[Inventory, InventoryRepository]):
    def __init__(self, db: Session):
        super().__init__(InventoryRepository(db), db)

    def find_by_product(self, product_id: str) -> Optional[Inventory]:
        return self.repository.find_by_product(product_id)

    def list_all(self) -> List[Inventory]:
        return self.repository.find_all_records()

    def find_available(self) -> List[Inventory]:
        return self.repository.find_available()

    def is_available(self, product_id: str, quantity: int = 1) -> bool:
        if quantity < 1:
            return False
        inv = self.find_by_product(product_id)
        if not inv:
            return False
        if inv.stock_status == "OUT_OF_STOCK":
            return False
        sellable = inv.quantity_available - (inv.quantity_reserved or 0)
        return sellable >= quantity

    def sellable_quantity(self, product_id: str) -> int:
        inv = self.find_by_product(product_id)
        if not inv or inv.stock_status == "OUT_OF_STOCK":
            return 0
        return max(0, inv.quantity_available - (inv.quantity_reserved or 0))

    def update_quantity(self, product_id: str, quantity: int) -> Optional[Inventory]:
        if quantity < 0:
            raise ValueError("quantity_available cannot be negative")
        return self.repository.update_quantity(product_id, quantity)

    def _require_product(self, product_id: str) -> Product:
        product = self.db.query(Product).filter(Product.product_id == product_id).first()
        if not product:
            raise ValueError(f"Product {product_id} not found")
        return product

    def _require_inventory(self, product_id: str) -> Inventory:
        inv = self.find_by_product(product_id)
        if not inv:
            raise ValueError(f"Inventory for product {product_id} not found")
        return inv

    def _record_movement(
        self,
        *,
        product_id: str,
        inventory_id: str,
        movement_type: str,
        quantity_delta: int,
        quantity_after: int,
        note: Optional[str] = None,
        reference_type: Optional[str] = None,
        reference_id: Optional[str] = None,
    ) -> StockMovement:
        mov = StockMovement(
            movement_id=str(uuid.uuid4()),
            product_id=product_id,
            inventory_id=inventory_id,
            movement_type=movement_type,
            quantity_delta=quantity_delta,
            quantity_after=quantity_after,
            note=note,
            reference_type=reference_type,
            reference_id=reference_id,
        )
        self.db.add(mov)
        return mov

    def _sync_stock_status(self, inv: Inventory) -> None:
        if inv.quantity_available <= 0:
            inv.quantity_available = 0
            inv.stock_status = "OUT_OF_STOCK"
        elif inv.stock_status == "OUT_OF_STOCK":
            inv.stock_status = "active"

    def increase_stock(
        self,
        product_id: str,
        quantity: int,
        *,
        note: Optional[str] = None,
        movement_type: str = "STOCK_IN",
    ) -> Inventory:
        if quantity <= 0:
            raise ValueError("increase quantity must be positive")
        if movement_type not in ("STOCK_IN", "PURCHASE", "RETURN_IN", "ADJUSTMENT"):
            raise ValueError(f"invalid movement_type for increase: {movement_type}")

        self._require_product(product_id)
        inv = self._require_inventory(product_id)
        before = inv.quantity_available

        try:
            inv.quantity_available = before + quantity
            self._sync_stock_status(inv)
            self._record_movement(
                product_id=product_id,
                inventory_id=inv.inventory_id,
                movement_type=movement_type,
                quantity_delta=quantity,
                quantity_after=inv.quantity_available,
                note=note,
            )
            self.db.flush()
            return inv
        except Exception:
            self.db.rollback()
            raise

    def decrease_stock(
        self,
        product_id: str,
        quantity: int,
        *,
        note: Optional[str] = None,
        movement_type: str = "ADJUSTMENT",
    ) -> Inventory:
        if quantity <= 0:
            raise ValueError("decrease quantity must be positive")
        if movement_type not in ("SALE", "RETURN_OUT", "ADJUSTMENT"):
            raise ValueError(f"invalid movement_type for decrease: {movement_type}")

        self._require_product(product_id)
        inv = self._require_inventory(product_id)
        before = inv.quantity_available

        if before < quantity:
            raise ValueError(
                f"insufficient stock for {product_id}: available={before}, requested={quantity}"
            )

        try:
            inv.quantity_available = before - quantity
            self._sync_stock_status(inv)
            self._record_movement(
                product_id=product_id,
                inventory_id=inv.inventory_id,
                movement_type=movement_type,
                quantity_delta=-quantity,
                quantity_after=inv.quantity_available,
                note=note,
            )
            self.db.flush()
            return inv
        except Exception:
            self.db.rollback()
            raise

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
        """تأیید فروش: کاهش available و reserved + StockMovement SALE."""
        try:
            self.decrease_stock(
                product_id,
                quantity,
                movement_type="SALE",
                note="confirm_sale",
            )
            inventory = self.find_by_product(product_id)
            if inventory and inventory.quantity_reserved >= quantity:
                inventory.quantity_reserved -= quantity
            elif inventory:
                inventory.quantity_reserved = 0
            self.db.flush()
            return True
        except ValueError:
            return False
