"""WP-02 — minimum product-side skin safety before APPROVE/ACTIVATE.

Contract v1.1 §3: before APPROVE, contraindication status must be represented by
verified non-empty Evidence on field=contraindications, or an explicit
field-specific UNKNOWN assertion (claim_type=UNKNOWN, qa_status=VERIFIED).

Does not change generic EvidenceReadiness semantics.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.evidence import Evidence

_FIELD = "contraindications"
_QA_OK = "VERIFIED"


@dataclass
class SkinSafetyMinimumResult:
    satisfied: bool
    summary: str
    matching_evidence_ids: List[str]


class SkinSafetyMinimumService:
    """Server-side gate for skin product safety minimum (contraindications)."""

    def __init__(self, db: Session):
        self.db = db

    def evaluate(self, product_id: str) -> SkinSafetyMinimumResult:
        rows = (
            self.db.query(Evidence)
            .filter(Evidence.product_id == product_id)
            .all()
        )
        matches: List[str] = []
        for ev in rows:
            if not self._is_contraindications_field(getattr(ev, "field", None)):
                continue
            qa = (getattr(ev, "qa_status", None) or "").strip().upper()
            conflict = (getattr(ev, "conflict_status", None) or "NONE").strip().upper()
            if qa != _QA_OK:
                continue
            if conflict == "CONFLICT":
                continue
            claim_type = (getattr(ev, "claim_type", None) or "").strip().upper()
            claim = (getattr(ev, "claim", None) or "").strip()
            # Explicit field-specific UNKNOWN (Contract §3 / §7)
            if claim_type == "UNKNOWN":
                matches.append(ev.evidence_id)
                continue
            # Verified non-empty contraindications content
            if claim:
                matches.append(ev.evidence_id)

        if matches:
            return SkinSafetyMinimumResult(
                satisfied=True,
                summary=f"PASS contraindications safety evidence={matches}",
                matching_evidence_ids=matches,
            )
        return SkinSafetyMinimumResult(
            satisfied=False,
            summary=(
                "FAIL Skin safety minimum: require field=contraindications with "
                "qa_status=VERIFIED and (non-empty claim OR claim_type=UNKNOWN); "
                "PENDING/NEEDS_REVIEW/REJECTED/CONFLICT/unrelated fields do not satisfy"
            ),
            matching_evidence_ids=[],
        )

    @staticmethod
    def _is_contraindications_field(field: Optional[str]) -> bool:
        return (field or "").strip().casefold() == _FIELD
