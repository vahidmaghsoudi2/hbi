"""P4 P0 — Controlled Product lifecycle. Sole writer of Product.status."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, Set
from sqlalchemy.orm import Session
from app.core.exceptions import NotFoundError, ValidationError
from app.core.governance import (
    ACTION_ACTIVATE, ACTION_APPROVE, ACTION_ARCHIVE, ACTION_ENTER_QA_REVIEW,
    ACTION_IDENTITY_CHANGE, ACTION_QA_CHANGE, ACTION_REJECT, ACTION_SUBMIT,
    ALLOWED_TRANSITIONS, TRANSITION_ROLES,
)
from app.models.product import Product
from app.models.user_role import ROLE_PO, ROLE_REVIEWER_QA
from app.services.evidence_readiness_service import EvidenceReadinessService
from app.services.mutation_log_service import MutationLogService


class ProductTransitionService:
    def __init__(self, db: Session):
        self.db = db
        self.log = MutationLogService(db)
        self.readiness = EvidenceReadinessService(db)

    def _get_product(self, product_id: str) -> Product:
        product = self.db.query(Product).filter(Product.product_id == product_id).first()
        if not product:
            raise NotFoundError(f"Product {product_id} not found")
        return product

    def _assert_role(self, roles: Set[str], action: str) -> str:
        allowed = TRANSITION_ROLES.get(action, frozenset())
        matched = roles.intersection(allowed)
        if not matched:
            raise ValidationError(
                f"Unauthorized for {action}: required {sorted(allowed)}, have {sorted(roles) or 'none'}"
            )
        return ROLE_PO if ROLE_PO in matched else sorted(matched)[0]

    def _transition(self, product_id, action, actor_id, roles, reason=None) -> Product:
        product = self._get_product(product_id)
        actor_role = self._assert_role(roles, action)
        key = (product.status, action)
        if key not in ALLOWED_TRANSITIONS:
            raise ValidationError(f"Invalid transition: status={product.status} action={action}")
        target = ALLOWED_TRANSITIONS[key]
        before = self.log.product_snapshot(product)
        product.status = target
        self.db.flush()
        after = self.log.product_snapshot(product)
        self.log.append(actor_id=actor_id, actor_role=actor_role, action=action,
                        target_id=product_id, before=before, after=after,
                        reason=reason, resulting_state=target)
        return product

    def submit(self, product_id, actor_id, roles):
        product = self._get_product(product_id)
        if product.status != "DRAFT":
            raise ValidationError("SUBMIT requires status=DRAFT")
        if not (product.brand and product.product_name):
            raise ValidationError("SUBMIT requires brand and product_name")
        return self._transition(product_id, ACTION_SUBMIT, actor_id, roles)

    def enter_qa_review(self, product_id, actor_id, roles):
        return self._transition(product_id, ACTION_ENTER_QA_REVIEW, actor_id, roles)

    def approve(self, product_id, actor_id, roles):
        product = self._get_product(product_id)
        if product.status != "QA_REVIEW":
            raise ValidationError("APPROVE requires status=QA_REVIEW")
        if ROLE_PO not in roles:
            raise ValidationError("APPROVE requires PO role")
        if product.qa_verdict != "VALID":
            raise ValidationError("APPROVE requires qa_verdict=VALID")
        readiness = self.readiness.evaluate(product_id)
        if not readiness.ready:
            raise ValidationError(f"Evidence Readiness FAIL: {readiness.summary}")
        if product.identity_status != "VERIFIED":
            raise ValidationError("APPROVE requires identity_status=VERIFIED")
        return self._transition(product_id, ACTION_APPROVE, actor_id, roles)

    def reject(self, product_id, actor_id, roles, reason):
        if not reason or not str(reason).strip():
            raise ValidationError("REJECT requires non-empty reason")
        return self._transition(product_id, ACTION_REJECT, actor_id, roles, reason=reason.strip())

    def activate(self, product_id, actor_id, roles):
        product = self._get_product(product_id)
        if product.status != "APPROVED":
            raise ValidationError("ACTIVATE requires status=APPROVED")
        if ROLE_PO not in roles:
            raise ValidationError("ACTIVATE requires PO role")
        if product.qa_verdict != "VALID":
            raise ValidationError("ACTIVATE requires qa_verdict=VALID")
        if product.identity_status != "VERIFIED":
            raise ValidationError("ACTIVATE requires identity_status=VERIFIED")
        readiness = self.readiness.evaluate(product_id)
        if not readiness.ready:
            raise ValidationError(f"Evidence Readiness FAIL: {readiness.summary}")
        return self._transition(product_id, ACTION_ACTIVATE, actor_id, roles)

    def archive(self, product_id, actor_id, roles, reason=None):
        return self._transition(product_id, ACTION_ARCHIVE, actor_id, roles, reason=reason)

    def set_product_qa(self, product_id, actor_id, roles, verdict, notes=None):
        if not roles.intersection({ROLE_REVIEWER_QA, ROLE_PO}):
            raise ValidationError("Product QA decision requires Reviewer/QA or PO")
        allowed = {"PENDING", "VALID", "INVALID", "CONFLICT", "UNKNOWN", "NEEDS_REVIEW"}
        if verdict not in allowed:
            raise ValidationError(f"Invalid qa_verdict: {verdict}")
        product = self._get_product(product_id)
        before = self.log.product_snapshot(product)
        product.qa_verdict = verdict
        product.qa_reviewed_at = datetime.now(timezone.utc)
        if notes is not None:
            product.qa_notes = notes
        self.db.flush()
        after = self.log.product_snapshot(product)
        role = ROLE_PO if ROLE_PO in roles else ROLE_REVIEWER_QA
        self.log.append(actor_id=actor_id, actor_role=role, action=ACTION_QA_CHANGE,
                        target_id=product_id, before=before, after=after,
                        resulting_state=product.status)
        return product

    def verify_identity(self, product_id, actor_id, roles, identity_status,
                        source_refs=None, confidence=None):
        if not roles.intersection({ROLE_REVIEWER_QA, ROLE_PO}):
            raise ValidationError("Identity verification requires Reviewer/QA or PO")
        allowed = {"VERIFIED", "PARTIAL_IDENTITY", "CONFLICT", "NEEDS_REVIEW"}
        if identity_status not in allowed:
            raise ValidationError(f"Invalid identity_status: {identity_status}")
        product = self._get_product(product_id)
        before = self.log.product_snapshot(product)
        product.identity_status = identity_status
        if source_refs is not None:
            product.identity_source_refs = source_refs
        if confidence is not None:
            product.identity_confidence = confidence
        self.db.flush()
        after = self.log.product_snapshot(product)
        role = ROLE_PO if ROLE_PO in roles else ROLE_REVIEWER_QA
        self.log.append(actor_id=actor_id, actor_role=role, action=ACTION_IDENTITY_CHANGE,
                        target_id=product_id, before=before, after=after,
                        resulting_state=product.status)
        return product
