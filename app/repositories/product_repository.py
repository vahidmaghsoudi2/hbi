from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.inventory import Inventory
from app.repositories.base import BaseRepository
from app.core.governance import PRODUCT_GOVERNANCE_KEYS
from app.core.exceptions import ValidationError


class ProductRepository(BaseRepository[Product]):
    def __init__(self, db: Session):
        super().__init__(Product, db)

    def update(self, id: str, **kwargs) -> Optional[Product]:
        blocked = set(kwargs.keys()) & PRODUCT_GOVERNANCE_KEYS
        if blocked:
            raise ValidationError(
                f"Governance fields cannot be updated via generic repository update: {sorted(blocked)}"
            )
        return super().update(id, **kwargs)

    def update_governance_privileged(
        self, id: str, *, authorized: bool = False, **kwargs
    ) -> Optional[Product]:
        """Internal escape hatch for governance fields only.

        Callers MUST pass authorized=True. Lifecycle transitions belong in
        ProductTransitionService — not this method. Public service/API layers
        must not expose this without an explicit authorization decision.
        """
        if not authorized:
            raise ValidationError(
                "update_governance_privileged requires authorized=True; "
                "use ProductTransitionService for controlled lifecycle changes"
            )
        return super().update(id, **kwargs)

    def find_by_brand(self, brand: str) -> List[Product]:
        return self.db.query(Product).filter(Product.brand.ilike(f"%{brand}%")).all()

    def find_by_identity_status(self, status: str) -> List[Product]:
        return self.db.query(Product).filter(Product.identity_status == status).all()

    def find_by_qa_verdict(self, verdict: str) -> List[Product]:
        return self.db.query(Product).filter(Product.qa_verdict == verdict).all()

    def get_with_inventory(self, product_id: str):
        return self.db.query(Product).filter(Product.product_id == product_id).first()

    def find_by_identity_status_and_active(self, identity_status: str) -> List[Product]:
        return self.db.query(Product).join(
            Inventory, Product.product_id == Inventory.product_id
        ).filter(
            Product.identity_status == identity_status,
            Product.status != "DRAFT",
            Inventory.quantity_available > 0
        ).all()
