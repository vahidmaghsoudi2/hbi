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
        self.db.flush()
        return mov

    def _sync_stock_status(self, inv: Inventory) -> None:
        if inv.quantity_available <= 0:
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
            raise ValueError("quantity must be positive")
        self._require_product(product_id)
        inv = self._require_inventory(product_id)
        inv.quantity_available = inv.quantity_available + quantity
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

    def decrease_stock(
        self,
        product_id: str,
        quantity: int,
        *,
        note: Optional[str] = None,
        movement_type: str = "ADJUSTMENT",
        reference_type: Optional[str] = None,
        reference_id: Optional[str] = None,
    ) -> Inventory:
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        self._require_product(product_id)
        inv = self._require_inventory(product_id)
        before = inv.quantity_available
        if before < quantity:
            raise ValueError(
                f"insufficient stock for product {product_id}: available={before}, requested={quantity}"
            )
        inv.quantity_available = before - quantity
        self._sync_stock_status(inv)
        self._record_movement(
            product_id=product_id,
            inventory_id=inv.inventory_id,
            movement_type=movement_type,
            quantity_delta=-quantity,
            quantity_after=inv.quantity_available,
            note=note,
            reference_type=reference_type,
            reference_id=reference_id,
        )
        self.db.flush()
        return inv

    # Non-customer outflow reasons (INVENTORY-OUTFLOW-001). Not SALE.
    OUTFLOW_REASONS = frozenset({
        "DAMAGE_WASTE",
        "INTERNAL_USE",
        "SHORTAGE_LOSS",
        "OTHER",
    })

    def record_non_customer_outflow(
        self,
        product_id: str,
        quantity: int,
        *,
        reason: str,
        note: Optional[str] = None,
        actor_id: Optional[str] = None,
    ) -> dict:
        """Decrease stock as ADJUSTMENT with structured OUTFLOW reference — never SALE.

        No amount_usd / FX is set (no invented price). Sales reports use Sale table only.
        """
        reason_key = (reason or "").strip().upper()
        if reason_key not in self.OUTFLOW_REASONS:
            raise ValueError(
                f"invalid outflow reason: {reason}; allowed={sorted(self.OUTFLOW_REASONS)}"
            )
        ref_id = f"OUTFLOW-{uuid.uuid4().hex[:12]}"
        ref_type = f"OUTFLOW_{reason_key}"
        note_parts = [f"reason={reason_key}"]
        if actor_id:
            note_parts.append(f"actor={actor_id}")
        if note:
            note_parts.append(note.strip())
        combined_note = " | ".join(note_parts)

        inv = self.decrease_stock(
            product_id,
            quantity,
            note=combined_note,
            movement_type="ADJUSTMENT",
            reference_type=ref_type,
            reference_id=ref_id,
        )
        mov = (
            self.db.query(StockMovement)
            .filter(StockMovement.reference_id == ref_id)
            .first()
        )
        return {
            "inventory": inv,
            "movement": mov,
            "outflow_id": ref_id,
            "reason": reason_key,
        }

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

    def set_sale_price_usd(
        self,
        product_id: str,
        sale_price_usd: float,
        *,
        fx_rate_usd_to_irr: float | None = None,
    ) -> Inventory:
        """Official sale price source (PO #181): Inventory.sale_price_usd.

        Optionally refresh derived/legacy sale_price_toman when FX is supplied
        (C-01: toman = usd * R / 10). FX is never invented here.
        """
        from datetime import datetime, timezone
        from app.services.currency_fx import irr_to_toman, usd_to_irr, validate_fx_rate

        if sale_price_usd is None or float(sale_price_usd) < 0:
            raise ValueError("sale_price_usd must be >= 0")
        sale_price_usd = float(sale_price_usd)
        self._require_product(product_id)
        inv = self._require_inventory(product_id)

        inv.sale_price_usd = sale_price_usd
        inv.price_updated_at = datetime.now(timezone.utc)

        if fx_rate_usd_to_irr is not None:
            rate = validate_fx_rate(fx_rate_usd_to_irr)
            unit_irr = usd_to_irr(sale_price_usd, rate)
            inv.price_fx_rate_usd_to_irr = rate
            inv.sale_price_irr = unit_irr
            inv.sale_price_toman = int(round(irr_to_toman(unit_irr)))
        self.db.flush()
        return inv
