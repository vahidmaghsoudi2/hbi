"""D3 Controlled Hybrid Evidence Policy — operational gates.

PO Controlled Hybrid (Option 3):
  Seed / identity input is not Engine-Ready by itself.
  Engine-Ready requires governed Identity + Evidence + Product QA,
  with claim-level (non-identity) acceptable evidence.

Does not change scoring weights, Need vocabulary, or Issue #37.
Does not invent medical standards — uses existing Evidence.field / claim_type.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Set

from sqlalchemy.orm import Session

from app.models.evidence import Evidence
from app.services.evidence_readiness_service import (
    EvidenceReadinessResult,
    EvidenceReadinessService,
)

# --- Acceptance Matrix (executable) ---

# Evidence that only supports product identity / catalog identity.
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

# ProductKnowledge / claim surfaces already used in repository.
CLAIM_FIELDS: frozenset = frozenset(
    {
        "claimed_benefits",
        "known_use_cases",
        "ingredients",
        "contraindications",
        "benefits",
        "use_case",
        "use_cases",
        "indication",
        "indications",
        "safety",
    }
)

CLAIM_TYPES: frozenset = frozenset(
    {
        "BENEFIT",
        "CLAIM",
        "USE",
        "SAFETY",
        "INDICATION",
        "FACT",  # non-identity FACT may still be claim-surface if field is claim
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
    field_name = (getattr(ev, "field", None) or "").strip().lower()
    claim_type = (getattr(ev, "claim_type", None) or "").strip().upper()

    if field_name in IDENTITY_FIELDS:
        # Explicit claim_type on identity field does not upgrade to claim-level.
        return False
    if field_name in CLAIM_FIELDS:
        return True
    if claim_type in {"BENEFIT", "CLAIM", "USE", "SAFETY", "INDICATION"}:
        return True
    # Unknown field + FACT/empty: not claim-level (no guessing).
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
