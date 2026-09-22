"""Evidence Service — Framework 3/4/5 enforcement + QA verdicts.

HBI-CATALOG-INTAKE-FIX-001: after QA status change, ProductKnowledge is rebuilt
from APPROVED/VERIFIED evidence only (via ProductKnowledgeService).
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationError
from app.models.evidence import Evidence
from app.repositories.evidence_repository import EvidenceRepository
from app.services.base import BaseService

logger = logging.getLogger(__name__)


class EvidenceService(BaseService[Evidence, EvidenceRepository]):
    """
    Evidence domain service.

    Notes:
    - A resolved conflict is represented by conflict_status="NONE";
      resolution detail is stored in notes when provided.
    """

    def __init__(self, db: Session):
        super().__init__(EvidenceRepository(db), db)

    def _validate_claim_boundary(self, claim_type: str, source_type: str) -> None:
        # Framework 4 — lightweight boundary (kept as pre-existing behavior).
        if not claim_type or not source_type:
            raise ValidationError("claim_type and source_type are required")

    def _generate_claim_id(self, product_id: str) -> str:
        return f"CLM-{product_id}-{uuid.uuid4().hex[:8]}"

    def _generate_evidence_id(self, product_id: str) -> str:
        return f"EV-{product_id}-{uuid.uuid4().hex[:8]}"

    def _log_unknown(self, product_id: str, field: Optional[str], value: Optional[str]) -> None:
        logger.info(
            "UNKNOWN evidence registered: product_id=%s, field=%s, value=%s, status=UNVERIFIED",
            product_id,
            field,
            value,
        )

    def _log_conflict(self, product_id: str, field: str, values) -> None:
        logger.warning(
            "CONFLICT detected: product_id=%s, field=%s, values=%s, severity=HIGH, status=UNRESOLVED",
            product_id,
            field,
            values,
        )

    def add_evidence(self, evidence_data: dict) -> Evidence:
        required = ["product_id", "source_type", "source_reference", "claim"]
        for field in required:
            if field not in evidence_data or not evidence_data[field]:
                raise ValidationError(f"Missing required field: {field}")

        product_id = evidence_data["product_id"]
        claim_type = evidence_data.get("claim_type") or "UNKNOWN"
        source_type = evidence_data.get("source_type") or "UNKNOWN"
        self._validate_claim_boundary(claim_type, source_type)

        if claim_type == "UNKNOWN":
            self._log_unknown(product_id, evidence_data.get("field"), evidence_data.get("claim"))

        evidence_data.setdefault("evidence_id", self._generate_evidence_id(product_id))
        evidence_data.setdefault("claim_id", self._generate_claim_id(product_id))
        evidence_data["claim_type"] = claim_type
        evidence_data["source_type"] = source_type
        evidence_data.setdefault("evidence_status", "UNKNOWN")
        evidence_data.setdefault("conflict_status", "NONE")
        evidence_data.setdefault("qa_status", "PENDING")
        evidence_data.setdefault("evidence_date", datetime.now(timezone.utc))

        evidence = self.repository.create(**evidence_data)

        conflicts = self.detect_conflicts(product_id)
        if conflicts:
            for conf in conflicts:
                self._log_conflict(product_id, conf["field"], conf["values"])
            if any(conf.get("new_evidence_id") == evidence.evidence_id for conf in conflicts):
                self.repository.update(evidence.evidence_id, conflict_status="CONFLICT")
                evidence = self.get_by_id(evidence.evidence_id) or evidence

        return evidence

    def verify_evidence(self, evidence_id: str, verdict: str) -> Optional[Evidence]:
        """Apply QA verdict and rebuild ProductKnowledge for the product."""
        valid_verdicts = ["VERIFIED", "REJECTED", "NEEDS_REVIEW"]
        if verdict not in valid_verdicts:
            raise ValidationError(f"Invalid verdict. Allowed: {valid_verdicts}")

        evidence = self.get_by_id(evidence_id)
        if not evidence:
            raise NotFoundError(f"Evidence {evidence_id} not found")

        updated = self.repository.update(evidence_id, qa_status=verdict)
        # PO HBI-CATALOG-INTAKE-FIX-001: QA change must rebuild ProductKnowledge.
        if updated is not None:
            from app.services.product_knowledge_service import ProductKnowledgeService

            ProductKnowledgeService(self.db).update_from_evidence(updated.product_id)
        return updated

    def detect_conflicts(self, product_id: str) -> List[Dict]:
        evidences = self.repository.find_by_product(product_id)
        if not evidences:
            return []

        field_map: Dict[str, list] = {}
        for ev in evidences:
            field = ev.field or "general"
            field_map.setdefault(field, []).append(
                {
                    "evidence_id": ev.evidence_id,
                    "value": ev.claim,
                    "claim_type": ev.claim_type,
                    "source_type": ev.source_type,
                    "date": ev.source_date,
                }
            )

        conflicts = []
        for field, entries in field_map.items():
            if len(entries) > 1:
                unique_values = set(entry["value"] for entry in entries)
                if len(unique_values) > 1:
                    conflicts.append(
                        {
                            "field": field,
                            "values": list(unique_values),
                            "evidence_ids": [e["evidence_id"] for e in entries],
                            "new_evidence_id": entries[-1]["evidence_id"],
                        }
                    )
        return conflicts

    def resolve_conflict(self, evidence_id: str, resolution: str) -> Evidence:
        evidence = self.get_by_id(evidence_id)
        if not evidence:
            raise NotFoundError(f"Evidence {evidence_id} not found")
        if evidence.conflict_status != "CONFLICT":
            raise ValidationError("This evidence is not in conflict status.")

        note = evidence.notes or ""
        if resolution:
            note = (note + " | " if note else "") + f"resolution={resolution}"

        updated = self.repository.update(
            evidence_id,
            conflict_status="NONE",
            notes=note,
        )
        if not updated:
            raise NotFoundError(f"Evidence {evidence_id} not found")
        return updated
