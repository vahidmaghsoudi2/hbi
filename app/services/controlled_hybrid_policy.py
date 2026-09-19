"""D3 Controlled Hybrid Evidence Policy — operational gates.

PO Controlled Hybrid (Option 3):
  Seed / identity input is not Engine-Ready by itself.
  Engine-Ready requires governed Identity + Evidence + Product QA,
  with claim-level (non-identity) acceptable evidence.

Acceptance Matrix (claim-level):
  field in {claimed_benefits, known_use_cases}
  OR claim_type in {BENEFIT, CLAIM, USE, SAFETY, INDICATION}
  Identity fields never count as claim-level.

Does not change scoring weights, Need vocabulary, or Issue #37.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from sqlalchemy.orm import Session

from app.models.evidence import Evidence
from app.services.evidence_readiness_service import (
    EvidenceReadinessResult,
    EvidenceReadinessService,
)

# --- Acceptance Matrix (executable) ---

IDENTITY_FIELDS: frozenset = frozenset(
    {
        "brand",
        "product_name",
        "name",
        "identity",
        "product_id",
        "identity_status",
    }
)

# Explicit claim surfaces from the mission Acceptance Matrix only.
CLAIM_FIELDS: frozenset = frozenset(
    {
        "claimed_benefits",
        "known_use_cases",
    }
)

# Explicit claim_type set from the mission Acceptance Matrix (no FACT).
CLAIM_TYPES: frozenset = frozenset(
    {
        "BENEFIT",
        "CLAIM",
        "USE",
        "SAFETY",
        "INDICATION",
    }
)

ACCEPTABLE_QA = EvidenceReadinessService.ACCEPTABLE_QA


@dataclass
class HybridReadinessResult:
    """Claim-Ready vs Engine-Ready under Controlled Hybrid."""

    claim_ready: bool
    engine_ready: bool
    base: EvidenceReadinessResult
    claim_evidence_ids: List[str] = field(default_factory=list)
    identity_only_evidence_ids: List[str] = field(default_factory=list)
    summary: str = ""


def _is_claim_level(ev: Evidence) -> bool:
    """True only when field/claim_type match the Acceptance Matrix."""
    field_name = (getattr(ev, "field", None) or "").strip().lower()
    claim_type = (getattr(ev, "claim_type", None) or "").strip().upper()

    if field_name in IDENTITY_FIELDS:
        return False
    if field_name in CLAIM_FIELDS:
        return True
    if claim_type in CLAIM_TYPES:
        return True
    return False


class ControlledHybridPolicy:
    """Evaluate Claim-Ready and Engine-Ready for a product."""

    def __init__(self, db: Session):
        self.db = db
        self.readiness = EvidenceReadinessService(db)

    def evaluate(self, product_id: str) -> HybridReadinessResult:
        base = self.readiness.evaluate(product_id)
        evidences = (
            self.db.query(Evidence).filter(Evidence.product_id == product_id).all()
        )
        claim_ids: List[str] = []
        identity_ids: List[str] = []
        for e in evidences:
            eid = getattr(e, "evidence_id", None) or "?"
            qa = (getattr(e, "qa_status", None) or "PENDING").upper()
            conflict = (getattr(e, "conflict_status", None) or "NONE").upper()
            if qa not in ACCEPTABLE_QA or conflict == "CONFLICT":
                continue
            if _is_claim_level(e):
                claim_ids.append(eid)
            else:
                identity_ids.append(eid)

        claim_ready = base.ready
        engine_ready = claim_ready and len(claim_ids) > 0
        if not claim_ready:
            summary = f"CLAIM_NOT_READY: {base.summary}"
        elif not engine_ready:
            summary = (
                "CLAIM_READY_IDENTITY_ONLY: acceptable evidence exists but no "
                "claim-level (non-identity) APPROVED/VERIFIED evidence — not Engine-Ready"
            )
        else:
            summary = "ENGINE_READY"
        return HybridReadinessResult(
            claim_ready=claim_ready,
            engine_ready=engine_ready,
            base=base,
            claim_evidence_ids=claim_ids,
            identity_only_evidence_ids=identity_ids,
            summary=summary,
        )
