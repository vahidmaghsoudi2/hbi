from typing import Optional, List, Set
import json
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
from app.core.exceptions import ValidationError, NotFoundError, ConflictError
from app.services.mutation_log_service import MutationLogService
from app.services.evidence_service import EvidenceService
from app.services.product_knowledge_service import ProductKnowledgeService
from app.services.duplicate_check_service import DuplicateCheckService
from app.models.duplicate_check_audit import DuplicateCheckAudit
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

    def list_all(self) -> List[Product]:
        """Return all products for authorized operational catalog views."""
        return self.repository.list_all()

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
        knowledge_use_cases = data.pop("knowledge_use_cases", None)
        knowledge_evidence_claim = data.pop("knowledge_evidence_claim", None)
        knowledge_evidence_source_reference = data.pop("knowledge_evidence_source_reference", None)
        # Intake-only resolution token (not a Product column). Allows create after
        # POSSIBLE_MATCH when operator recorded decision=NEW on that check_id.
        duplicate_check_id = data.pop("duplicate_check_id", None)
        product_id = data.get("product_id")
        if product_id and self.get_by_id(product_id):
            raise ConflictError(f"Product {product_id} already exists")

        # WP-01: enforce existing DuplicateCheck on real create path (no new algorithm).
        self._enforce_duplicate_check_on_create(
            data, actor_id=actor_id, roles=roles, duplicate_check_id=duplicate_check_id
        )
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

        # Product Intake now creates the governed knowledge/evidence seed used
        # by Recommendation. The seed remains UNKNOWN/PENDING until QA verifies it.
        if knowledge_use_cases:
            EvidenceService(self.db).add_evidence({
                "product_id": product.product_id,
                "source_type": "OPERATOR_DECLARATION",
                "source_reference": knowledge_evidence_source_reference or "PRODUCT_INTAKE",
                "claim": knowledge_evidence_claim or knowledge_use_cases,
                "claim_type": "UNKNOWN",
                "field": "known_use_cases",
                "market_region": product.market_region,
                "evidence_strength": "UNVERIFIED",
                "evidence_status": "UNKNOWN",
                "qa_status": "PENDING",
            })
            knowledge = ProductKnowledgeService(self.db)
            knowledge.update_from_evidence(product.product_id)

        return product

    def _enforce_duplicate_check_on_create(
        self,
        data: dict,
        *,
        actor_id: str,
        roles: Set[str],
        duplicate_check_id: Optional[str],
    ) -> None:
        """Enforce DuplicateCheck on intake create without changing match rules.

        - NEW → allow create
        - EXISTING → ConflictError (exact product_id or barcode)
        - POSSIBLE_MATCH → require prior operator decision=NEW on duplicate_check_id
        """
        dup = DuplicateCheckService(self.db).check(dict(data), actor_id=actor_id, roles=roles)
        result = dup.get("result")
        check_id = dup.get("check_id")
        reason = dup.get("reason")
        if result == "NEW":
            return
        if result == "EXISTING":
            raise ConflictError(
                f"DuplicateCheck EXISTING ({reason}); check_id={check_id}. "
                "Create is blocked for exact product_id or barcode match."
            )
        if result == "POSSIBLE_MATCH":
            if not duplicate_check_id:
                raise ValidationError(
                    f"DuplicateCheck POSSIBLE_MATCH requires operator review "
                    f"(check_id={check_id}; operator_decision_required=true). "
                    "Record decision=NEW via duplicate-check audit, then retry create "
                    "with duplicate_check_id."
                )
            audit = (
                self.db.query(DuplicateCheckAudit)
                .filter(DuplicateCheckAudit.check_id == duplicate_check_id)
                .first()
            )
            if audit is None:
                raise ValidationError(
                    f"duplicate_check_id={duplicate_check_id} not found for POSSIBLE_MATCH resolution"
                )
            decision = json.loads(audit.operator_decision) if audit.operator_decision else None
            if not decision or str(decision.get("decision", "")).upper() != "NEW":
                raise ValidationError(
                    f"POSSIBLE_MATCH check_id={duplicate_check_id} has no operator decision=NEW"
                )
            return
        raise ValidationError(f"Unexpected DuplicateCheck result={result} check_id={check_id}")

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
