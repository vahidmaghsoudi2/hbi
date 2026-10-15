import uuid
import logging
from typing import List, Dict, Optional
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.evidence import Evidence
from app.repositories.evidence_repository import EvidenceRepository
from app.services.base import BaseService
from app.core.exceptions import ValidationError, ConflictError, NotFoundError
from app.domain.claim_taxonomy import CLAIM_TYPES
from app.services.evidence_mutation_log_service import EvidenceMutationLogService

logger = logging.getLogger(__name__)


class EvidenceService(BaseService[Evidence, EvidenceRepository]):
    """Evidence lifecycle with claim boundaries, conflict handling and G4 audit."""

    def __init__(self, db: Session):
        super().__init__(EvidenceRepository(db), db)
        self.audit = EvidenceMutationLogService(db)

    def _validate_claim_boundary(self, claim_type: str, source_type: str) -> None:
        if claim_type not in CLAIM_TYPES:
            raise ValidationError(
                f"Unsupported claim_type {claim_type!r}; allowed values: {sorted(CLAIM_TYPES)}"
            )
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

    def _log_conflict(
        self, product_id: str, field: str, values: List[str],
        severity: str = "HIGH", status: str = "UNRESOLVED",
    ) -> None:
        logger.warning(
            "Evidence conflict/review group: product_id=%s, field=%s, values=%s, severity=%s, status=%s",
            product_id, field, values, severity, status
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
        claim_type = str(data.get("claim_type") or "UNKNOWN").strip().upper() or "UNKNOWN"
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
        for conf in conflicts:
            self._log_conflict(
                product_id, conf["field"], conf["values"],
                conf.get("severity", "HIGH"), conf.get("status", "UNRESOLVED"),
            )
            # A detected conflict is a pair/group state, not merely a flag on
            # the newest row. Every member must be blocked until explicit
            # resolution selects one claim.
            for conflicting_id in conf["evidence_ids"]:
                self.repository.update(conflicting_id, conflict_status="CONFLICT")
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
            # REJECTED rows are governance-excluded (e.g. conflict losers).
            # They must not re-open conflicts when a new claim is added on the same field.
            if (getattr(ev, "qa_status", None) or "").strip().upper() == "REJECTED":
                continue
            field = ev.field or "general"
            field_map.setdefault(field, []).append({
                "evidence_id": ev.evidence_id,
                "value": ev.claim,
                "claim_type": ev.claim_type,
                "source_type": ev.source_type,
                "source_reference": (ev.source_reference or "").strip(),
                "date": ev.source_date,
            })

        conflicts = []
        for field, entries in field_map.items():
            if len(entries) > 1:
                unique_values = {entry["value"] for entry in entries}
                if len(unique_values) > 1:
                    # Distinct wording from the same source is ambiguous, not
                    # proof of a factual contradiction. Keep the persisted
                    # CONFLICT block fail-closed, but report it for review
                    # rather than asserting HIGH / UNRESOLVED contradiction.
                    normalized_references = [
                        (entry.get("source_reference") or "").strip().rstrip("/").casefold()
                        for entry in entries
                    ]
                    # Missing source references cannot establish source identity.
                    same_source_group = (
                        all(normalized_references)
                        and len(set(normalized_references)) == 1
                        and len({
                            (
                                (entry.get("source_type") or "").strip().upper(),
                                (entry.get("claim_type") or "").strip().upper(),
                            )
                            for entry in entries
                        }) == 1
                    )
                    conflicts.append({
                        "field": field,
                        "values": [entry["value"] for entry in entries],
                        "evidence_ids": [entry["evidence_id"] for entry in entries],
                        "new_evidence_id": entries[-1]["evidence_id"],
                        "severity": "REVIEW_REQUIRED" if same_source_group else "HIGH",
                        "status": "NEEDS_REVIEW" if same_source_group else "UNRESOLVED",
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

        selected = self.get_by_id(evidence_id)
        if not selected:
            raise NotFoundError(f"Evidence {evidence_id} not found")
        if selected.conflict_status != "CONFLICT":
            raise ValidationError("This evidence is not in conflict status.")

        # The evidence_id is the explicit winning claim. Resolution is a
        # governance decision, so every competing claim in the same field
        # must be excluded from Knowledge/Recommendation.
        field = selected.field or "general"
        related = [
            ev for ev in self.repository.find_by_product(selected.product_id)
            if (ev.field or "general") == field
            and ev.evidence_id != selected.evidence_id
            and (ev.conflict_status or "").upper() == "CONFLICT"
        ]

        before = self.audit.snapshot(selected)
        current_notes = selected.notes or ""
        new_notes = (
            f"{current_notes}\n"
            f"[RESOLVED] {resolution} at {datetime.now(timezone.utc).isoformat()}"
        )
        updated = self.repository.update(
            selected.evidence_id, conflict_status="NONE", notes=new_notes
        )

        for competing in related:
            competing_notes = competing.notes or ""
            rejected_notes = (
                f"{competing_notes}\n"
                f"[REJECTED_BY_CONFLICT_RESOLUTION winner={selected.evidence_id}] "
                f"{resolution} at {datetime.now(timezone.utc).isoformat()}"
            )
            self.repository.update(
                competing.evidence_id,
                conflict_status="NONE",
                qa_status="REJECTED",
                notes=rejected_notes,
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
                diff={
                    "conflict_status": {"old": "CONFLICT", "new": "NONE"},
                    "competing_evidence_ids": [ev.evidence_id for ev in related],
                    "competing_resolution_state": "REJECTED",
                },
                reason=resolution,
                resulting_state=updated.conflict_status,
                correlation_id=correlation_id or f"EVID-{uuid.uuid4().hex}",
            )
        return updated
