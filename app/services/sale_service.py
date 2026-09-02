"""Phase 08 — Sales workflow.

Uses existing Sale, SaleItem, Customer, Product, Inventory, StockMovement.
C-01: amount_irr = amount_usd * R; amount_toman = amount_irr / 10.
FX rate is caller-supplied only (never invented).
"""
from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.stock_movement import StockMovement
from app.repositories.sale_item_repository import SaleItemRepository
from app.repositories.sale_repository import SaleRepository
from app.services.base import BaseService
from app.services.stock_in_service import irr_to_toman, usd_to_irr


class SaleService(BaseService[Sale, SaleRepository]):
    def __init__(self, db: Session):
        super().__init__(SaleRepository(db), db)
        self.sale_item_repo = SaleItemRepository(db)

    def find_by_customer(self, customer_id: str) -> List[Sale]:
        return self.repository.find_by_customer(customer_id)

    def find_with_items(self, sale_id: str) -> Optional[Sale]:
        return self.repository.find_with_items(sale_id)

    def get_total_sales(self) -> int:
        return self.repository.get_total_sales()

    def get_sale_items(self, sale_id: str) -> List[SaleItem]:
        return self.sale_item_repo.find_by_sale(sale_id)

    def create_sale(
        self,
        customer_id: str,
        items: list,
        *,
        fx_rate_usd_to_irr: float,
    ) -> Sale:
        if not items:
            raise ValueError("Sale must have at least one item")
        if fx_rate_usd_to_irr is None or float(fx_rate_usd_to_irr) <= 0:
            raise ValueError("fx_rate_usd_to_irr must be > 0 (caller-supplied; never invented)")
        fx_rate = float(fx_rate_usd_to_irr)

        customer = self.db.query(Customer).filter(Customer.customer_id == customer_id).first()
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")

        validated = []
        for item_data in items:
            product_id = item_data.get("product_id")
            if not product_id:
                raise ValueError("product_id is required on each item")
            try:
                quantity = int(item_data.get("quantity"))
            except (TypeError, ValueError):
                raise ValueError("quantity must be a positive integer")
            if quantity <= 0:
                raise ValueError("quantity must be positive")

            product = self.db.query(Product).filter(Product.product_id == product_id).first()
            if not product:
                raise ValueError(f"Product {product_id} not found")
            if getattr(product, "status", None) != "ACTIVE":
                raise ValueError(f"Product {product_id} is not ACTIVE")

            inv = self.db.query(Inventory).filter(Inventory.product_id == product_id).first()
            if not inv:
                raise ValueError(f"Inventory for product {product_id} not found")
            sellable = inv.quantity_available - (inv.quantity_reserved or 0)
            if sellable < quantity:
                raise ValueError(
                    f"insufficient stock for product {product_id}: "
                    f"sellable={sellable}, requested={quantity}"
                )

            if "unit_price_usd" in item_data and item_data["unit_price_usd"] is not None:
                unit_usd = float(item_data["unit_price_usd"])
            elif inv.sale_price_usd is not None:
                unit_usd = float(inv.sale_price_usd)
            else:
                raise ValueError(
                    f"unit_price_usd required for product {product_id} "
                    "(not provided and inventory.sale_price_usd is empty)"
                )
            if unit_usd < 0:
                raise ValueError("unit_price_usd must be >= 0")

            unit_irr = usd_to_irr(unit_usd, fx_rate)
            unit_toman = irr_to_toman(unit_irr)
            validated.append(
                {
                    "product_id": product_id,
                    "quantity": quantity,
                    "unit_usd": unit_usd,
                    "unit_irr": unit_irr,
                    "unit_toman": unit_toman,
                    "inventory": inv,
                }
            )

        sale_id = str(uuid.uuid4())
        total_usd = 0.0

        try:
            sale = Sale(
                sale_id=sale_id,
                customer_id=customer_id,
                total_amount_toman=0,
                total_amount_usd=0.0,
                fx_rate_usd_to_irr=fx_rate,
                total_amount_irr=0.0,
            )
            self.db.add(sale)
            self.db.flush()

            for line in validated:
                inv = line["inventory"]
                before = inv.quantity_available
                qty = line["quantity"]
                after = before - qty
                if after < 0:
                    raise ValueError("negative inventory forbidden")

                inv.quantity_available = after
                if after == 0:
                    inv.stock_status = "OUT_OF_STOCK"

                line_usd = line["unit_usd"] * qty
                line_irr = usd_to_irr(line_usd, fx_rate)
                line_toman = irr_to_toman(line_irr)
                total_usd += line_usd

                item = SaleItem(
                    sale_item_id=str(uuid.uuid4()),
                    sale_id=sale_id,
                    product_id=line["product_id"],
                    quantity=qty,
                    unit_price_toman=int(round(line["unit_toman"])),
                    unit_price_usd=line["unit_usd"],
                    fx_rate_usd_to_irr=fx_rate,
                    unit_price_irr=line["unit_irr"],
                )
                self.db.add(item)

                movement = StockMovement(
                    movement_id=str(uuid.uuid4()),
                    product_id=line["product_id"],
                    inventory_id=inv.inventory_id,
                    movement_type="SALE",
                    quantity_delta=-qty,
                    quantity_after=after,
                    amount_usd=line_usd,
                    fx_rate_usd_to_irr=fx_rate,
                    amount_irr=line_irr,
                    amount_toman=line_toman,
                    reference_type="SALE",
                    reference_id=sale_id,
                    note="phase08_sale",
                )
                self.db.add(movement)

            total_irr = usd_to_irr(total_usd, fx_rate)
            total_toman = irr_to_toman(total_irr)
            sale.total_amount_usd = total_usd
            sale.total_amount_irr = total_irr
            sale.total_amount_toman = int(round(total_toman))
            sale.fx_rate_usd_to_irr = fx_rate
            self.db.flush()
            return sale
        except Exception:
            self.db.rollback()
            raise
