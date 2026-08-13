from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.repositories.sale_repository import SaleRepository
from app.repositories.sale_item_repository import SaleItemRepository
from app.services.base import BaseService
from app.services.inventory_service import InventoryService
from datetime import datetime

class SaleService(BaseService[Sale, SaleRepository]):
    def __init__(self, db: Session):
        super().__init__(SaleRepository(db), db)
        self.sale_item_repo = SaleItemRepository(db)
        self.inventory_service = InventoryService(db)

    def find_by_customer(self, customer_id: str) -> List[Sale]:
        return self.repository.find_by_customer(customer_id)

    def find_with_items(self, sale_id: str) -> Optional[Sale]:
        return self.repository.find_with_items(sale_id)

    def get_total_sales(self) -> int:
        return self.repository.get_total_sales()

    def create_sale(self, customer_id: str, items: list) -> Sale:
        if not items:
            raise ValueError("Sale must have at least one item")

        sale_id = f"SALE_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        total_amount = 0

        sale = self.create(
            sale_id=sale_id,
            customer_id=customer_id,
            total_amount_toman=0
        )

        for item_data in items:
            product_id = item_data["product_id"]
            quantity = item_data["quantity"]
            unit_price = item_data["unit_price_toman"]

            if not self.inventory_service.reserve_stock(product_id, quantity):
                raise ValueError(f"Insufficient stock for product {product_id}")

            item_id = f"SI_{datetime.now().strftime('%Y%m%d%H%M%S')}_{product_id}"
            self.sale_item_repo.create(
                sale_item_id=item_id,
                sale_id=sale.sale_id,
                product_id=product_id,
                quantity=quantity,
                unit_price_toman=unit_price
            )
            total_amount += quantity * unit_price
            self.inventory_service.confirm_sale(product_id, quantity)

        self.update(sale.sale_id, total_amount_toman=total_amount)
        return sale

    def get_sale_items(self, sale_id: str) -> List[SaleItem]:
        return self.sale_item_repo.find_by_sale(sale_id)
