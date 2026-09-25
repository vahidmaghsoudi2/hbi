import uuid
import logging
from typing import List, Dict, Optional
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.evidence import Evidence
from app.repositories.evidence_repository import EvidenceRepository
from app.services.base import BaseService
from app.core.exceptions import ValidationError, ConflictError, NotFoundError
from app.services.evidence_mutation_log_service import EvidenceMutationLogService

logger = logging.getLogger(__name__)


class EvidenceService(BaseService[Evidence, EvidenceRepository]):
    """Evidence lifecycle with claim boundaries, conflict handling and G4 audit."""

    def __init__(self, db: Session):
        super().__init__(EvidenceRepository(db), db)
        self.audit = EvidenceMutationLogService(db)

    def _validate_claim_boundary(self, claim_type: str, source_type: str) -> None:
        if claim_type == "FACT":
            allowed_sources = {"PEER_REVIEWED", "CLINICAL_TRIAL", "REGULATORY"}
            if source_type not in allowed_sources:
                raise ValidationError(
                    "FACT claims require independent verification from "
                    "PEER_REVIEWED, CLINICAL_TRIAL, or REGULATORY sources."
                )

    def _generate_claim_id(self, product_id: str) -> str:
        seq = self.repository.get_next_claim_seq(product_id)
        return f"EV-{product_id}-{seq:03d}"

    def _generate_evidence_id(self, product_id: str) -> str:
        return f"EV-{product_id}-{uuid.uuid4().hex[:8]}"

    def _log_unknown(self, product_id: str, field: str, value: str) -> None:
        logger.info(
            "UNKNOWN evidence registered: product_id=%s, field=%s, value=%s, status=UNVERIFIED",
            product_id, field, value
        )

    def _log_conflict(self, product_id: str, field: str, values: List[str]) -> None:
        logger.warning(
            "CONFLICT detected: product_id=%s, field=%s, values=%s, severity=HIGH, status=UNRESOLVED",
            product_id, field, values
        )

    def add_evidence(
        self,
        evidence_data: dict,
        *,
        actor_id: str = "system",
        actor_role: Optional[str] = None,
        action: str = "CREATE",
        reason: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> Evidence:
        required = ["product_id", "source_type", "source_reference", "claim"]
        for field in required:
            if field not in evidence_data or not evidence_data[field]:
                raise ValidationError(f"Missing required field: {field}")

        data = dict(evidence_data)
        product_id = data["product_id"]
        claim_type = (data.get("claim_type") or "UNKNOWN").upper()
        source_type = data.get("source_type") or "UNKNOWN"
        self._validate_claim_boundary(claim_type, source_type)

        if claim_type == "UNKNOWN":
            self._log_unknown(product_id, data.get("field"), data.get("claim"))

        data.setdefault("evidence_id", self._generate_evidence_id(product_id))
        data.setdefault("claim_id", self._generate_claim_id(product_id))
        data["claim_type"] = claim_type
        data["source_type"] = source_type
        data.setdefault("evidence_status", "UNKNOWN")
        data.setdefault("conflict_status", "NONE")
        data.setdefault("qa_status", "PENDING")
        data.setdefault("evidence_date", datetime.now(timezone.utc))

        evidence = self.repository.create(**data)
        conflicts = self.detect_conflicts(product_id)
        if conflicts:
            for conf in conflicts:
                self._log_conflict(product_id, conf["field"], conf["values"])
            if any(conf["new_evidence_id"] == evidence.evidence_id for conf in conflicts):
                self.repository.update(evidence.evidence_id, conflict_status="CONFLICT")
                evidence = self.repository.get_by_id(evidence.evidence_id)

        self.audit.append(
            actor_id=actor_id,
            actor_role=actor_role,
            action=action,
            target_id=evidence.evidence_id,
            product_id=product_id,
            before=None,
            after=self.audit.snapshot(evidence),
            reason=reason,
            resulting_state=evidence.qa_status,
            correlation_id=correlation_id or f"EVID-{uuid.uuid4().hex}",
        )
        return evidence

    def verify_evidence(
        self,
        evidence_id: str,
        verdict: str,
        *,
        actor_id: str = "system",
        actor_role: Optional[str] = None,
        reason: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> Optional[Evidence]:
        valid_verdicts = ["VERIFIED", "REJECTED", "NEEDS_REVIEW"]
        if verdict not in valid_verdicts:
            raise ValidationError(f"Invalid verdict. Allowed: {valid_verdicts}")

        evidence = self.get_by_id(evidence_id)
        if not evidence:
            raise NotFoundError(f"Evidence {evidence_id} not found")

        before = self.audit.snapshot(evidence)
        updated = self.repository.update(evidence_id, qa_status=verdict)
        if updated is not None:
            from app.services.product_knowledge_service import ProductKnowledgeService
            ProductKnowledgeService(self.db).update_from_evidence(updated.product_id)
            self.audit.append(
                actor_id=actor_id,
                actor_role=actor_role,
                action="VERIFY",
                target_id=updated.evidence_id,
                product_id=updated.product_id,
                before=before,
                after=self.audit.snapshot(updated),
                diff={"qa_status": {"old": before.get("qa_status"), "new": verdict}},
                reason=reason,
                resulting_state=updated.qa_status,
                correlation_id=correlation_id or f"EVID-{uuid.uuid4().hex}",
            )
        return updated

    def detect_conflicts(self, product_id: str) -> List[Dict]:
        evidences = self.repository.find_by_product(product_id)
        if not evidences:
            return []

        field_map = {}
        for ev in evidences:
            field = ev.field or "general"
            field_map.setdefault(field, []).append({
                "evidence_id": ev.evidence_id,
                "value": ev.claim,
                "claim_type": ev.claim_type,
                "source_type": ev.source_type,
                "date": ev.source_date,
            })

        conflicts = []
        for field, entries in field_map.items():
            if len(entries) > 1:
                unique_values = {entry["value"] for entry in entries}
                if len(unique_values) > 1:
                    conflicts.append({
                        "field": field,
                        "values": [entry["value"] for entry in entries],
                        "evidence_ids": [entry["evidence_id"] for entry in entries],
                        "new_evidence_id": entries[-1]["evidence_id"],
                    })
        return conflicts

    def resolve_conflict(
        self,
        evidence_id: str,
        resolution: str,
        *,
        actor_id: str = "system",
        actor_role: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> Optional[Evidence]:
        if not resolution or not resolution.strip():
            raise ValidationError("Conflict resolution reason is required")

        evidence = self.get_by_id(evidence_id)
        if not evidence:
            raise NotFoundError(f"Evidence {evidence_id} not found")
        if evidence.conflict_status != "CONFLICT":
            raise ValidationError("This evidence is not in conflict status.")

        before = self.audit.snapshot(evidence)
        current_notes = evidence.notes or ""
        new_notes = (
            f"{current_notes}\n"
            f"[RESOLVED] {resolution} at {datetime.now(timezone.utc).isoformat()}"
        )
        updated = self.repository.update(
            evidence_id, conflict_status="NONE", notes=new_notes
        )
        if updated is not None:
            from app.services.product_knowledge_service import ProductKnowledgeService
            ProductKnowledgeService(self.db).update_from_evidence(updated.product_id)
            self.audit.append(
                actor_id=actor_id,
                actor_role=actor_role,
                action="RESOLVE_CONFLICT",
                target_id=updated.evidence_id,
                product_id=updated.product_id,
                before=before,
                after=self.audit.snapshot(updated),
                diff={"conflict_status": {"old": "CONFLICT", "new": "NONE"}},
                reason=resolution,
                resulting_state=updated.conflict_status,
                correlation_id=correlation_id or f"EVID-{uuid.uuid4().hex}",
            )
        return updated
