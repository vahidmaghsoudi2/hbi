"""D3 Conditional Evidence Policy (PO decision) — Controlled Hybrid.

PO rule (authoritative):
- Identity Evidence establishes what the product is.
- Products that carry performance / benefit / feature claims also require
  claim-related Evidence before QA VALID is authorized under this policy.
- Identity Evidence alone is not a general license for QA VALID /
  Recommendation / Sale when such claims exist.
- Sufficiency is proportional to the product's claim surface.
- No invented evidence standards beyond fields already in the model.

This module evaluates the claim surface from ProductKnowledge + Evidence
rows already stored; it does not invent claims.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.evidence import Evidence
from app.models.product_knowledge import ProductKnowledge

ACCEPTABLE_QA = frozenset({"APPROVED", "VERIFIED"})

# Fields that only support identity (what the product is), not performance claims.
IDENTITY_FIELDS = frozenset({
    "brand",
    "product_name",
    "variant",
    "size_value",
    "size_unit",
    "barcode_gtin",
    "market_region",
    "country_of_origin",
    "packaging_version",
})

# Fields that express performance / benefit / use-case / feature claims.
CLAIM_FIELDS = frozenset({
    "claimed_benefits",
    "benefit",
    "known_use_cases",
    "use_case",
    "contraindications",
    "ingredients",
    "ingredient_roles",
    "usage_instructions",
    "manufacturer_claims",
})


@dataclass
class D3PolicyResult:
    allowed: bool
    has_performance_claims: bool
    identity_evidence_ids: List[str] = field(default_factory=list)
    claim_evidence_ids: List[str] = field(default_factory=list)
    summary: str = ""


def _norm(value: Optional[str]) -> str:
    return (value or "").strip().upper()


def _field_norm(value: Optional[str]) -> str:
    return (value or "").strip().lower()


def _classify_evidence(ev: Evidence) -> str:
    """Return 'claim' or 'identity' for an evidence row."""
    claim_type = _norm(getattr(ev, "claim_type", None))
    if claim_type == "BENEFIT":
        return "claim"
    f = _field_norm(getattr(ev, "field", None))
    if f in CLAIM_FIELDS:
        return "claim"
    if f in IDENTITY_FIELDS:
        return "identity"
    # Unspecified field + non-BENEFIT: identity-class for identity-only path.
    return "identity"


class D3ConditionalEvidencePolicy:
    def __init__(self, db: Session):
        self.db = db

    def _product_claim_surface(self, product_id: str, evidences: List[Evidence]) -> bool:
        pk = (
            self.db.query(ProductKnowledge)
            .filter(ProductKnowledge.product_id == product_id)
            .first()
        )
        if pk is not None:
            for attr in ("known_use_cases", "claimed_benefits", "manufacturer_claims"):
                if (getattr(pk, attr, None) or "").strip():
                    return True
        for ev in evidences:
            if _classify_evidence(ev) == "claim":
                return True
        return False

    def evaluate_for_qa_valid(self, product_id: str) -> D3PolicyResult:
        evidences = (
            self.db.query(Evidence).filter(Evidence.product_id == product_id).all()
        )
        has_claims = self._product_claim_surface(product_id, evidences)

        identity_ok: List[str] = []
        claim_ok: List[str] = []
        for ev in evidences:
            qa = _norm(getattr(ev, "qa_status", None) or "PENDING")
            if qa not in ACCEPTABLE_QA:
                continue
            eid = getattr(ev, "evidence_id", None) or "?"
            kind = _classify_evidence(ev)
            if kind == "claim":
                claim_ok.append(eid)
            else:
                identity_ok.append(eid)

        if has_claims:
            if claim_ok:
                return D3PolicyResult(
                    allowed=True,
                    has_performance_claims=True,
                    identity_evidence_ids=identity_ok,
                    claim_evidence_ids=claim_ok,
                    summary="PASS D3: performance/claim surface present; claim Evidence APPROVED/VERIFIED",
                )
            return D3PolicyResult(
                allowed=False,
                has_performance_claims=True,
                identity_evidence_ids=identity_ok,
                claim_evidence_ids=[],
                summary=(
                    "FAIL D3: product has performance/benefit/use-case claims but no "
                    "APPROVED/VERIFIED claim-related Evidence (identity Evidence alone is not sufficient)"
                ),
            )

        if identity_ok or claim_ok:
            return D3PolicyResult(
                allowed=True,
                has_performance_claims=False,
                identity_evidence_ids=identity_ok,
                claim_evidence_ids=claim_ok,
                summary="PASS D3: no performance-claim surface; identity Evidence sufficient under Conditional policy",
            )
        return D3PolicyResult(
            allowed=False,
            has_performance_claims=False,
            identity_evidence_ids=[],
            claim_evidence_ids=[],
            summary="FAIL D3: no APPROVED/VERIFIED Evidence available for QA VALID",
        )
