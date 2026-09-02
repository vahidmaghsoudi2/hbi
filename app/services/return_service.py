"""Phase 10 — Returns workflow on existing SaleReturn + Inventory + StockMovement.

Uses movement type RETURN_IN only.
Does not mutate historical Sale monetary totals.
Does not implement payment refunds.
"""
from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.inventory import Inventory
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.sale_return import SaleReturn
from app.models.stock_movement import StockMovement
from app.services.stock_in_service import irr_to_toman, usd_to_irr


class ReturnService:
    def __init__(self, db: Session):
        self.db = db

    def list_by_sale(self, sale_id: str) -> List[SaleReturn]:
        return (
            self.db.query(SaleReturn)
            .filter(SaleReturn.sale_id == sale_id)
            .order_by(SaleReturn.created_at.asc(), SaleReturn.return_id.asc())
            .all()
        )

    def _sold_qty(self, sale_id: str, product_id: str) -> int:
        rows = (
            self.db.query(SaleItem)
            .filter(SaleItem.sale_id == sale_id, SaleItem.product_id == product_id)
            .all()
        )
        return sum(int(r.quantity) for r in rows)

    def _already_returned_qty(self, sale_id: str, product_id: str) -> int:
        total = (
            self.db.query(func.coalesce(func.sum(SaleReturn.quantity), 0))
            .filter(SaleReturn.sale_id == sale_id, SaleReturn.product_id == product_id)
            .scalar()
        )
        return int(total or 0)

    def create_return(
        self,
        *,
        sale_id: str,
        product_id: str,
        quantity: int,
        fx_rate_usd_to_irr: Optional[float] = None,
        reason: Optional[str] = None,
    ) -> SaleReturn:
        if not sale_id:
            raise ValueError("sale_id is required")
        if not product_id:
            raise ValueError("product_id is required")
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            raise ValueError("quantity must be a positive integer")
        if quantity <= 0:
            raise ValueError("quantity must be positive")

        sale = self.db.query(Sale).filter(Sale.sale_id == sale_id).first()
        if not sale:
            raise ValueError(f"Sale {sale_id} not found")

        prior_usd = sale.total_amount_usd
        prior_irr = sale.total_amount_irr
        prior_toman = sale.total_amount_toman
        prior_fx = sale.fx_rate_usd_to_irr

        items = (
            self.db.query(SaleItem)
            .filter(SaleItem.sale_id == sale_id, SaleItem.product_id == product_id)
            .all()
        )
        if not items:
            raise ValueError(
                f"SaleItem for sale {sale_id} product {product_id} not found"
            )

        sold = self._sold_qty(sale_id, product_id)
        already = self._already_returned_qty(sale_id, product_id)
        remaining = sold - already
        if quantity > remaining:
            raise ValueError(
                f"return quantity exceeds remaining sold quantity: "
                f"sold={sold}, already_returned={already}, requested={quantity}"
            )

        inv = self.db.query(Inventory).filter(Inventory.product_id == product_id).first()
        if not inv:
            raise ValueError(f"Inventory for product {product_id} not found")

        # Unit price from first matching sale item (USD)
        unit_usd = items[0].unit_price_usd
        if unit_usd is None:
            unit_usd = 0.0
        else:
            unit_usd = float(unit_usd)

        # FX: prefer explicit caller rate; else sale snapshot; else item snapshot
        if fx_rate_usd_to_irr is not None:
            if float(fx_rate_usd_to_irr) <= 0:
                raise ValueError("fx_rate_usd_to_irr must be > 0 when provided")
            fx_rate = float(fx_rate_usd_to_irr)
        elif sale.fx_rate_usd_to_irr is not None and float(sale.fx_rate_usd_to_irr) > 0:
            fx_rate = float(sale.fx_rate_usd_to_irr)
        elif items[0].fx_rate_usd_to_irr is not None and float(items[0].fx_rate_usd_to_irr) > 0:
            fx_rate = float(items[0].fx_rate_usd_to_irr)
        else:
            raise ValueError(
                "fx_rate_usd_to_irr required (not on sale/item and not supplied)"
            )

        line_usd = unit_usd * quantity
        line_irr = usd_to_irr(line_usd, fx_rate)
        line_toman = irr_to_toman(line_irr)

        try:
            before = inv.quantity_available
            after = before + quantity
            inv.quantity_available = after
            if after > 0 and inv.stock_status == "OUT_OF_STOCK":
                inv.stock_status = "active"

            ret = SaleReturn(
                return_id=str(uuid.uuid4()),
                sale_id=sale_id,
                product_id=product_id,
                quantity=quantity,
                amount_usd=line_usd,
                fx_rate_usd_to_irr=fx_rate,
                amount_irr=line_irr,
                amount_toman=int(round(line_toman)),
                reason=reason,
            )
            self.db.add(ret)

            movement = StockMovement(
                movement_id=str(uuid.uuid4()),
                product_id=product_id,
                inventory_id=inv.inventory_id,
                movement_type="RETURN_IN",
                quantity_delta=quantity,
                quantity_after=after,
                amount_usd=line_usd,
                fx_rate_usd_to_irr=fx_rate,
                amount_irr=line_irr,
                amount_toman=line_toman,
                reference_type="SALE_RETURN",
                reference_id=ret.return_id,
                note=f"return of sale {sale_id}",
            )
            self.db.add(movement)
            self.db.flush()

            self.db.refresh(sale)
            if sale.total_amount_usd != prior_usd:
                raise RuntimeError("sale total_amount_usd corrupted by return")
            if sale.total_amount_irr != prior_irr:
                raise RuntimeError("sale total_amount_irr corrupted by return")
            if sale.total_amount_toman != prior_toman:
                raise RuntimeError("sale total_amount_toman corrupted by return")
            if sale.fx_rate_usd_to_irr != prior_fx:
                raise RuntimeError("sale fx_rate corrupted by return")

            return ret
        except Exception:
            self.db.rollback()
            raise
