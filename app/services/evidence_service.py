import uuid
from typing import List, Dict, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.evidence import Evidence
from app.repositories.evidence_repository import EvidenceRepository
from app.services.base import BaseService
from app.core.exceptions import ValidationError, ConflictError, NotFoundError


class EvidenceService(BaseService[Evidence, EvidenceRepository]):
    """
    Evidence Service — Framework 3, 4, 5 compliant.

    Framework 3:
    - Generates semantic claim_id values using:
      EV-[PRODUCT_ID]-[SEQ]

    Framework 4:
    - Enforces claim-boundary rules.
    - Prevents MANUFACTURER_CLAIM/UNKNOWN source promotion to FACT.

    Framework 5:
    - Handles UNKNOWN evidence through the Unknown Register.
    - Detects and logs conflicts through the Conflict Register.
    - Never silently selects a conflicting value.
    - A resolved conflict is represented by conflict_status="NONE";
      resolution details remain preserved in notes.
    """

    def __init__(self, db: Session):
        super().__init__(EvidenceRepository(db), db)

    # ─── Framework 4: Claim Boundary Rules ───────────────────

    def _validate_claim_boundary(
        self,
        claim_type: str,
        source_type: str
    ) -> None:
        """
        Framework 4 RULE 2: Promotion Forbidden.

        Forbidden:
        - INFERENCE → FACT
        - MANUFACTURER_CLAIM → FACT
        - UNKNOWN → FACT

        Manufacturer claims may only become FACT after independent
        verification, which is represented through the verification flow.
        """
        if claim_type == "FACT":
            if source_type in ("MANUFACTURER", "OFFICIAL_MANUFACTURER"):
                raise ValidationError(
                    "Manufacturer claim cannot be promoted to FACT "
                    "without independent verification."
                )

            if source_type == "UNKNOWN":
                raise ValidationError(
                    "UNKNOWN source cannot be promoted to FACT."
                )

    # ─── ID Generators ───────────────────────────────────────

    def _generate_claim_id(self, product_id: str) -> str:
        """
        Framework 3:
        Generate claim identifier in the format:

        EV-[PRODUCT_ID]-[SEQ]
        """
        seq = self.repository.get_next_claim_seq(product_id)
        return f"EV-{product_id}-{seq:03d}"

    def _generate_evidence_id(self, product_id: str) -> str:
        """
        Generate the internal Evidence primary key.

        This is separate from claim_id because evidence_id is the
        database primary key while claim_id is the Framework 3
        semantic identifier.
        """
        return f"EV-{product_id}-{uuid.uuid4().hex[:8]}"

    # ─── Framework 5: Unknown/Conflict Registers ─────────────

    def _log_unknown(
        self,
        product_id: str,
        field: str,
        value: str
    ) -> None:
        """
        Framework 5:
        Record UNKNOWN evidence in the in-memory Unknown Register.

        Status is explicitly UNVERIFIED.
        """
        if not hasattr(self, "_unknown_register"):
            self._unknown_register = []

        self._unknown_register.append(
            {
                "product_id": product_id,
                "field": field,
                "value": value,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "UNVERIFIED",
            }
        )

    def _log_conflict(
        self,
        product_id: str,
        field: str,
        values: List[str]
    ) -> None:
        """
        Framework 5:
        Record an unresolved conflict in the in-memory Conflict Register.

        Conflicts are never silently resolved.
        """
        if not hasattr(self, "_conflict_register"):
            self._conflict_register = []

        self._conflict_register.append(
            {
                "product_id": product_id,
                "field": field,
                "values": values,
                "timestamp": datetime.utcnow().isoformat(),
                "severity": "HIGH",
                "status": "UNRESOLVED",
            }
        )

    # ─── CRUD Operations ─────────────────────────────────────

    def add_evidence(self, evidence_data: dict) -> Evidence:
        """
        Add an Evidence record with Framework 3, 4 and 5 enforcement.
        """
        required = [
            "product_id",
            "source_type",
            "source_reference",
            "claim",
        ]

        for field in required:
            if field not in evidence_data or not evidence_data[field]:
                raise ValidationError(
                    f"Missing required field: {field}"
                )

        product_id = evidence_data["product_id"]
        claim_type = evidence_data.get("claim_type") or "UNKNOWN"
        source_type = evidence_data.get("source_type") or "UNKNOWN"

        # Framework 4: Claim Boundary Rules
        self._validate_claim_boundary(
            claim_type,
            source_type
        )

        # Framework 5: UNKNOWN handling
        if claim_type == "UNKNOWN":
            self._log_unknown(
                product_id,
                evidence_data.get("field"),
                evidence_data.get("claim")
            )

        # Generate IDs
        evidence_data.setdefault(
            "evidence_id",
            self._generate_evidence_id(product_id)
        )

        evidence_data.setdefault(
            "claim_id",
            self._generate_claim_id(product_id)
        )

        evidence_data["claim_type"] = claim_type
        evidence_data["source_type"] = source_type

        # Defaults
        evidence_data.setdefault(
            "evidence_status",
            "UNKNOWN"
        )

        evidence_data.setdefault(
            "conflict_status",
            "NONE"
        )

        evidence_data.setdefault(
            "qa_status",
            "PENDING"
        )

        evidence_data.setdefault(
            "evidence_date",
            datetime.utcnow()
        )

        evidence = self.repository.create(
            **evidence_data
        )

        # Framework 5: Conflict detection
        conflicts = self.detect_conflicts(product_id)

        if conflicts:
            for conf in conflicts:
                self._log_conflict(
                    product_id,
                    conf["field"],
                    conf["values"]
                )

            if any(
                conf["new_evidence_id"] == evidence.evidence_id
                for conf in conflicts
            ):
                self.repository.update(
                    evidence.evidence_id,
                    conflict_status="CONFLICT"
                )

                evidence = self.repository.get_by_id(
                    evidence.evidence_id
                )

        return evidence

    def verify_evidence(
        self,
        evidence_id: str,
        verdict: str
    ) -> Optional[Evidence]:
        """
        Verify an Evidence record.

        Allowed QA verdicts:
        - VERIFIED
        - REJECTED
        - NEEDS_REVIEW
        """
        valid_verdicts = [
            "VERIFIED",
            "REJECTED",
            "NEEDS_REVIEW",
        ]

        if verdict not in valid_verdicts:
            raise ValidationError(
                f"Invalid verdict. Allowed: {valid_verdicts}"
            )

        evidence = self.get_by_id(evidence_id)

        if not evidence:
            raise NotFoundError(
                f"Evidence {evidence_id} not found"
            )

        return self.repository.update(
            evidence_id,
            qa_status=verdict
        )

    def detect_conflicts(
        self,
        product_id: str
    ) -> List[Dict]:
        """
        Framework 5:
        Detect conflicting claims for the same product field.

        Cross-product contamination is prevented because only evidence
        belonging to the requested product_id is evaluated.

        No conflicting value is silently selected.
        """
        evidences = self.repository.find_by_product(
            product_id
        )

        if not evidences:
            return []

        field_map = {}

        for ev in evidences:
            field = ev.field or "general"

            if field not in field_map:
                field_map[field] = []

            field_map[field].append(
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
                unique_values = set(
                    entry["value"]
                    for entry in entries
                )

                if len(unique_values) > 1:
                    conflicts.append(
                        {
                            "field": field,
                            "values": [
                                entry["value"]
                                for entry in entries
                            ],
                            "evidence_ids": [
                                entry["evidence_id"]
                                for entry in entries
                            ],
                            "new_evidence_id": entries[-1][
                                "evidence_id"
                            ],
                        }
                    )

        return conflicts

    def resolve_conflict(
        self,
        evidence_id: str,
        resolution: str
    ) -> Optional[Evidence]:
        """
        Framework 5:
        Resolve a conflict only through an explicit resolution record.

        IMPORTANT:
        Schema v1.2 permits conflict_status values:
            NONE
            CONFLICT

        Therefore a resolved conflict MUST NOT use "RESOLVED" as the
        database status because that value violates the locked CHECK
        constraint.

        The conflict status is changed to NONE and the resolution
        decision is preserved in notes with a [RESOLVED] marker.

        This does NOT silently choose a value; the explicit resolution
        remains auditable in the notes field.
        """
        evidence = self.get_by_id(evidence_id)

        if not evidence:
            raise NotFoundError(
                f"Evidence {evidence_id} not found"
            )

        if evidence.conflict_status != "CONFLICT":
            raise ValidationError(
                "This evidence is not in conflict status."
            )

        current_notes = evidence.notes or ""

        new_notes = (
            f"{current_notes}\n"
            f"[RESOLVED] {resolution} "
            f"at {datetime.utcnow().isoformat()}"
        )

        return self.repository.update(
            evidence_id,
            conflict_status="NONE",
            notes=new_notes
        )
