from typing import Optional, List, Set
import uuid
from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.inventory import Inventory
from app.repositories.product_repository import ProductRepository
from app.services.base import BaseService
from app.core.governance import (
    ACTION_CREATE, ACTION_EDIT, PRODUCT_GOVERNANCE_KEYS, PRODUCT_INFORMATIONAL_KEYS,
    can_create_product, can_edit_informational,
)
from app.core.exceptions import ValidationError, NotFoundError
from app.services.mutation_log_service import MutationLogService
from app.models.user_role import ROLE_ADMIN, ROLE_EDITOR, ROLE_PO, ROLE_REVIEWER_QA


class ProductService(BaseService[Product, ProductRepository]):
    def __init__(self, db: Session):
        super().__init__(ProductRepository(db), db)
        self.log = MutationLogService(db)

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

    def update(self, id: str, **kwargs) -> Optional[Product]:
        blocked = set(kwargs.keys()) & PRODUCT_GOVERNANCE_KEYS
        if blocked:
            raise ValidationError(
                f"Governance fields cannot be updated via generic service update: {sorted(blocked)}"
            )
        return self.repository.update(id, **kwargs)

    def create_product_with_inventory(
        self, product_data: dict, actor_id: str = "system", roles: Optional[Set[str]] = None,
    ) -> Product:
        roles = roles or set()
        if roles and not can_create_product(roles):
            raise ValidationError("Unauthorized to CREATE Product")
        data = dict(product_data)
        for k in list(PRODUCT_GOVERNANCE_KEYS):
            data.pop(k, None)
        data["status"] = "DRAFT"
        data["qa_verdict"] = "PENDING"
        data["identity_status"] = "NEEDS_REVIEW"
        product = self.create(**data)
        inventory = self.db.query(Inventory).filter(
            Inventory.product_id == product.product_id
        ).first()
        if not inventory:
            inventory = Inventory(
                inventory_id=f"INV-{product.product_id}-{uuid.uuid4().hex[:8]}",
                product_id=product.product_id,
                quantity_available=1, quantity_reserved=0,
                stock_status="AVAILABLE", sale_price_toman=0,
            )
            self.db.add(inventory)
            self.db.flush()
        role = next((r for r in (ROLE_PO, ROLE_REVIEWER_QA, ROLE_EDITOR, ROLE_ADMIN) if r in roles), None)
        self.log.append(
            actor_id=actor_id, actor_role=role, action=ACTION_CREATE,
            target_id=product.product_id, before=None,
            after=self.log.product_snapshot(product), resulting_state=product.status,
        )
        return product

    def edit_informational(self, product_id: str, updates: dict, actor_id: str, roles: Set[str]) -> Product:
        if not can_edit_informational(roles):
            raise ValidationError("Unauthorized to EDIT informational Product fields")
        blocked = set(updates.keys()) & PRODUCT_GOVERNANCE_KEYS
        if blocked:
            raise ValidationError(f"Governance fields forbidden on informational edit: {sorted(blocked)}")
        clean = {k: v for k, v in updates.items() if k in PRODUCT_INFORMATIONAL_KEYS}
        product = self.get_by_id(product_id)
        if not product:
            raise NotFoundError(f"Product {product_id} not found")
        before = self.log.product_snapshot(product)
        updated = self.repository.update(product_id, **clean)
        if not updated:
            raise NotFoundError(f"Product {product_id} not found")
        after = self.log.product_snapshot(updated)
        role = next((r for r in (ROLE_PO, ROLE_REVIEWER_QA, ROLE_EDITOR, ROLE_ADMIN) if r in roles), None)
        field_diff = {k: {"old": before.get(k), "new": after.get(k)}
                      for k in clean if before.get(k) != after.get(k)}
        self.log.append(
            actor_id=actor_id, actor_role=role, action=ACTION_EDIT, target_id=product_id,
            before=before, after=after, diff=field_diff, resulting_state=updated.status,
        )
        return updated
