"""G2 — minimal Research Draft orchestration on the existing Evidence boundary.

A research draft is a batch of source-traceable assertions attached to one
existing product_id. It does not create a Product, change P4 lifecycle fields,
approve evidence, or activate a Product.
"""
from __future__ import annotations
from typing import Dict, List, Set
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationError
from app.models.product import Product
from app.services.evidence_service import EvidenceService
from app.services.product_knowledge_service import ProductKnowledgeService


_ALLOWED_CLAIM_TYPES = {
    "FACT", "MANUFACTURER_CLAIM", "EVIDENCE", "INFERENCE", "UNKNOWN", "CONFLICT"
}


class ResearchDraftService:
    def __init__(self, db: Session):
        self.db = db
        self.evidence = EvidenceService(db)

    def create_draft(
        self,
        product_id: str,
        assertions: List[Dict],
        *,
        actor_id: str,
        actor_role: str | None,
    ) -> List:
        product = self.db.query(Product).filter(Product.product_id == product_id).first()
        if not product:
            raise NotFoundError(f"Product {product_id} not found")
        if not assertions:
            raise ValidationError("At least one research assertion is required")

        created = []
        for index, assertion in enumerate(assertions):
            data = dict(assertion)
            claim = data.get("claim")
            source_type = data.get("source_type")
            source_reference = data.get("source_reference")
            claim_type = (data.get("claim_type") or "UNKNOWN").upper()

            if not claim or not str(claim).strip():
                raise ValidationError(f"Assertion {index + 1}: claim is required")
            if not source_type or not str(source_type).strip():
                raise ValidationError(f"Assertion {index + 1}: source_type is required")
            if not source_reference or not str(source_reference).strip():
                raise ValidationError(f"Assertion {index + 1}: source_reference is required")
            if claim_type not in _ALLOWED_CLAIM_TYPES:
                raise ValidationError(
                    f"Assertion {index + 1}: invalid claim_type {claim_type}"
                )

            data["product_id"] = product_id
            data["claim_type"] = claim_type
            data["qa_status"] = "PENDING"
            data["evidence_status"] = "UNKNOWN"
            data["evidence_strength"] = data.get("evidence_strength") or "UNVERIFIED"
            data["notes"] = self._research_note(data.get("notes"), actor_id)
            created.append(
                self.evidence.add_evidence(
                    data,
                    actor_id=actor_id,
                    actor_role=actor_role,
                    action="RESEARCH_DRAFT_CREATE",
                    reason="Research draft assertion",
                )
            )

        # PENDING research assertions are intentionally excluded from Knowledge.
        ProductKnowledgeService(self.db).update_from_evidence(product_id)
        return created

    @staticmethod
    def _research_note(existing: str | None, actor_id: str) -> str:
        marker = f"[RESEARCH_DRAFT actor={actor_id}]"
        return f"{marker} {existing}".strip() if existing else marker
