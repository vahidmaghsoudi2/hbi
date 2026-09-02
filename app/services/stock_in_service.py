"""Phase 07 — Stock-In workflow.

Uses existing Product + Inventory + StockMovement only.
C-01 locked formula (via app.services.currency_fx):
  R = IRR per 1 USD
  amount_irr = amount_usd * R
  amount_toman = amount_irr / 10
FX rate is never invented; caller must supply it.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.product import Product
from app.models.stock_movement import StockMovement
from app.services.currency_fx import irr_to_toman, usd_to_irr, usd_to_toman, validate_fx_rate

# Re-export for legacy imports (sale/payment/return services)
__all__ = [
    "StockInService",
    "usd_to_irr",
    "irr_to_toman",
    "usd_to_toman",
    "validate_fx_rate",
]


class StockInService:
    def __init__(self, db: Session):
        self.db = db

    def stock_in(
        self,
        *,
        product_id: str,
        quantity: int,
        purchase_price_usd: float,
        fx_rate_usd_to_irr: float,
        note: Optional[str] = None,
        reference_type: Optional[str] = None,
        reference_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not product_id or not str(product_id).strip():
            raise ValueError("product_id is required")
        if quantity is None or int(quantity) <= 0:
            raise ValueError("quantity must be positive")
        quantity = int(quantity)
        if purchase_price_usd is None or float(purchase_price_usd) < 0:
            raise ValueError("purchase_price_usd must be >= 0")
        purchase_price_usd = float(purchase_price_usd)
        fx_rate_usd_to_irr = validate_fx_rate(fx_rate_usd_to_irr)

        product = (
            self.db.query(Product).filter(Product.product_id == product_id).first()
        )
        if not product:
            raise ValueError(f"Product {product_id} not found")

        inv = (
            self.db.query(Inventory).filter(Inventory.product_id == product_id).first()
        )
        if not inv:
            raise ValueError(
                f"Inventory for product {product_id} not found; "
                "Stock-In requires an existing Inventory row"
            )

        unit_irr = usd_to_irr(purchase_price_usd, fx_rate_usd_to_irr)
        unit_toman = irr_to_toman(unit_irr)
        line_usd = purchase_price_usd * quantity
        line_irr = usd_to_irr(line_usd, fx_rate_usd_to_irr)
        line_toman = irr_to_toman(line_irr)

        before_qty = inv.quantity_available
        prior_inv_fx = inv.price_fx_rate_usd_to_irr

        try:
            inv.quantity_available = before_qty + quantity
            if inv.quantity_available > 0 and inv.stock_status == "OUT_OF_STOCK":
                inv.stock_status = "active"

            inv.purchase_price_usd = purchase_price_usd
            inv.price_fx_rate_usd_to_irr = fx_rate_usd_to_irr
            inv.purchase_price_irr = unit_irr
            inv.purchase_price_toman = int(round(unit_toman))
            inv.price_updated_at = datetime.now(timezone.utc)

            movement = StockMovement(
                movement_id=str(uuid.uuid4()),
                product_id=product_id,
                inventory_id=inv.inventory_id,
                movement_type="STOCK_IN",
                quantity_delta=quantity,
                quantity_after=inv.quantity_available,
                amount_usd=line_usd,
                fx_rate_usd_to_irr=fx_rate_usd_to_irr,
                amount_irr=line_irr,
                amount_toman=line_toman,
                reference_type=reference_type,
                reference_id=reference_id,
                note=note,
            )
            self.db.add(movement)
            self.db.flush()

            return {
                "inventory": inv,
                "movement": movement,
                "before_quantity": before_qty,
                "prior_inventory_fx": prior_inv_fx,
            }
        except Exception:
            self.db.rollback()
            raise
