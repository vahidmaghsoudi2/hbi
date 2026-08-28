from typing import Optional, List
import uuid
from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.inventory import Inventory
from app.repositories.product_repository import ProductRepository
from app.services.base import BaseService

class ProductService(BaseService[Product, ProductRepository]):
    def __init__(self, db: Session):
        super().__init__(ProductRepository(db), db)

    def find_by_brand(self, brand: str) -> List[Product]:
        return self.repository.find_by_brand(brand)

    def find_by_identity_status(self, status: str) -> List[Product]:
        return self.repository.find_by_identity_status(status)

    def find_by_qa_verdict(self, verdict: str) -> List[Product]:
        return self.repository.find_by_qa_verdict(verdict)

    def get_with_inventory(self, product_id: str) -> Optional[Product]:
        return self.repository.get_with_inventory(product_id)

    def get_verified_products(self) -> List[Product]:
        return self.repository.find_by_identity_status("VERIFIED")

    def get_products_with_valid_qa(self) -> List[Product]:
        return self.repository.find_by_qa_verdict("VALID")

    def create_product_with_inventory(self, product_data: dict) -> Product:
        """
        Create Product and ensure an Inventory record exists with
        quantity_available > 0 and stock_status = AVAILABLE.
        """
        product = self.create(**product_data)

        inventory = self.db.query(Inventory).filter(
            Inventory.product_id == product.product_id
        ).first()

        if not inventory:
            inventory = Inventory(
                inventory_id=f"INV-{product.product_id}-{uuid.uuid4().hex[:8]}",
                product_id=product.product_id,
                quantity_available=1,
                quantity_reserved=0,
                stock_status="AVAILABLE",
                sale_price_toman=0
            )
            self.db.add(inventory)
            self.db.commit()

        return product
