"""Phase 12 — V1 Accounting Reports (read-only).

Does not invent COGS/discount when schema cannot support them.
Does not mutate any accounting tables.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.sale import Sale
from app.models.sale_return import SaleReturn

LOCKED_CATEGORIES = ("BOOST", "HAIR", "BEAUTY", "TOOLS", "PERFUME", "OTHER")
DEFAULT_LOW_STOCK = 5


def _as_utc_aware(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _period_bounds(kind: str, now: Optional[datetime] = None) -> tuple[datetime, datetime]:
    now = _as_utc_aware(now) or datetime.now(timezone.utc)
    if kind == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
    elif kind == "week":
        # ISO week: Monday 00:00 → next Monday
        start = (now - timedelta(days=now.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end = start + timedelta(days=7)
    elif kind == "month":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if start.month == 12:
            end = start.replace(year=start.year + 1, month=1)
        else:
            end = start.replace(month=start.month + 1)
    else:
        raise ValueError(f"unknown period kind: {kind}")
    return start, end


class ReportService:
    def __init__(self, db: Session):
        self.db = db

    def sales_report(
        self,
        *,
        start: datetime,
        end: datetime,
    ) -> Dict[str, Any]:
        start = _as_utc_aware(start)
        end = _as_utc_aware(end)
        if start is None or end is None:
            raise ValueError("start and end are required")
        if end <= start:
            raise ValueError("end must be after start")

        sales: List[Sale] = (
            self.db.query(Sale)
            .filter(Sale.created_at >= start, Sale.created_at < end)
            .order_by(Sale.created_at.asc())
            .all()
        )
        total_usd = sum(float(s.total_amount_usd or 0) for s in sales)
        total_irr = sum(float(s.total_amount_irr or 0) for s in sales)
        total_toman = sum(int(s.total_amount_toman or 0) for s in sales)
        return {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "sale_count": len(sales),
            "revenue_usd": total_usd,
            "revenue_irr": total_irr,
            "revenue_toman": total_toman,
            "sales": [
                {
                    "sale_id": s.sale_id,
                    "customer_id": s.customer_id,
                    "total_amount_usd": s.total_amount_usd,
                    "total_amount_irr": s.total_amount_irr,
                    "total_amount_toman": s.total_amount_toman,
                    "fx_rate_usd_to_irr": s.fx_rate_usd_to_irr,
                    "created_at": s.created_at.isoformat() if s.created_at else None,
                }
                for s in sales
            ],
        }

    def sales_period(self, kind: str) -> Dict[str, Any]:
        start, end = _period_bounds(kind)
        return self.sales_report(start=start, end=end)

    def inventory_all(self) -> List[Dict[str, Any]]:
        rows = self.db.query(Inventory).order_by(Inventory.product_id.asc()).all()
        return [self._inv_row(i) for i in rows]

    def inventory_by_category(self, category_id: str) -> List[Dict[str, Any]]:
        cat = (category_id or "").strip().upper()
        if cat not in LOCKED_CATEGORIES:
            raise ValueError(
                f"invalid category_id: {category_id}; allowed={list(LOCKED_CATEGORIES)}"
            )
        rows = (
            self.db.query(Inventory)
            .join(Product, Product.product_id == Inventory.product_id)
            .filter(Product.category_id == cat)
            .order_by(Inventory.product_id.asc())
            .all()
        )
        return [self._inv_row(i) for i in rows]

    def inventory_low_stock(self, threshold: int = DEFAULT_LOW_STOCK) -> List[Dict[str, Any]]:
        if threshold < 0:
            raise ValueError("threshold must be >= 0")
        rows = (
            self.db.query(Inventory)
            .filter(Inventory.quantity_available <= threshold)
            .order_by(Inventory.quantity_available.asc(), Inventory.product_id.asc())
            .all()
        )
        return [self._inv_row(i) for i in rows]

    def financial_summary(
        self,
        *,
        start: datetime,
        end: datetime,
    ) -> Dict[str, Any]:
        sales = self.sales_report(start=start, end=end)
        rets: List[SaleReturn] = (
            self.db.query(SaleReturn)
            .filter(SaleReturn.created_at >= start, SaleReturn.created_at < end)
            .all()
        )
        returns_usd = sum(float(r.amount_usd or 0) for r in rets)
        returns_irr = sum(float(r.amount_irr or 0) for r in rets)
        returns_toman = sum(int(r.amount_toman or 0) for r in rets)

        # COGS / discounts not reliably available from schema at sale time
        return {
            "start": sales["start"],
            "end": sales["end"],
            "revenue_usd": sales["revenue_usd"],
            "revenue_irr": sales["revenue_irr"],
            "revenue_toman": sales["revenue_toman"],
            "returns_usd": returns_usd,
            "returns_irr": returns_irr,
            "returns_toman": returns_toman,
            "net_revenue_usd": sales["revenue_usd"] - returns_usd,
            "net_revenue_irr": sales["revenue_irr"] - returns_irr,
            "net_revenue_toman": sales["revenue_toman"] - returns_toman,
            "discounts": {"status": "UNSUPPORTED", "reason": "no discount fields in schema"},
            "cogs": {
                "status": "UNSUPPORTED",
                "reason": "SaleItem has no unit cost snapshot; cannot compute reliable COGS",
            },
            "gross_profit": {
                "status": "UNSUPPORTED",
                "reason": "depends on COGS which is unsupported",
            },
            "return_count": len(rets),
            "sale_count": sales["sale_count"],
        }

    def categories_locked(self) -> List[Dict[str, Any]]:
        rows = self.db.query(Category).order_by(Category.sort_order.asc()).all()
        return [
            {
                "category_id": c.category_id,
                "name_fa": c.name_fa,
                "name_en": c.name_en,
            }
            for c in rows
        ]

    def _inv_row(self, inv: Inventory) -> Dict[str, Any]:
        product = self.db.query(Product).filter(Product.product_id == inv.product_id).first()
        return {
            "inventory_id": inv.inventory_id,
            "product_id": inv.product_id,
            "category_id": product.category_id if product else None,
            "quantity_available": inv.quantity_available,
            "quantity_reserved": inv.quantity_reserved,
            "stock_status": inv.stock_status,
            "purchase_price_usd": inv.purchase_price_usd,
            "sale_price_usd": inv.sale_price_usd,
            "purchase_price_toman": inv.purchase_price_toman,
            "sale_price_toman": inv.sale_price_toman,
            "price_fx_rate_usd_to_irr": inv.price_fx_rate_usd_to_irr,
        }
