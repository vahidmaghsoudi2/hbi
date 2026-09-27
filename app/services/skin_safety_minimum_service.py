"""Mission #283 / WP-02 — minimum product-side skin safety gate.

Contract v1.1 §3: for SKIN products, before APPROVE/ACTIVATE,
contraindication status must be represented by verified supported information
or an explicit UNKNOWN assertion. Generic EvidenceReadiness is unchanged.

This service is deliberately scoped by Product.product_line and never infers
Skin from Accounting Category, name, free text, use case, brand, or AI.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.evidence import Evidence
from app.models.product import Product

_FIELD = "contraindications"
_QA_OK = "VERIFIED"


@dataclass
class SkinSafetyMinimumResult:
    satisfied: bool
    summary: str
    matching_evidence_ids: List[str]


class SkinSafetyMinimumService:
    def __init__(self, db: Session):
        self.db = db

    def evaluate(self, product_id: str) -> SkinSafetyMinimumResult:
        product = self.db.query(Product).filter(Product.product_id == product_id).first()
        if product is None:
            return SkinSafetyMinimumResult(
                satisfied=False,
                summary="Product not found",
                matching_evidence_ids=[],
            )

        # Explicit Product Line boundary. No inference.
        if product.product_line != "SKIN":
            return SkinSafetyMinimumResult(
                satisfied=True,
                summary=f"NOT_APPLICABLE product_line={product.product_line!r}",
                matching_evidence_ids=[],
            )

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
            if qa != _QA_OK:
                continue

            conflict = (getattr(ev, "conflict_status", None) or "NONE").strip().upper()
            if conflict == "CONFLICT":
                continue

            claim_type = (getattr(ev, "claim_type", None) or "").strip().upper()
            claim = (getattr(ev, "claim", None) or "").strip()

            # Explicit field-specific UNKNOWN.
            if claim_type == "UNKNOWN":
                matches.append(ev.evidence_id)
                continue

            # Verified non-empty contraindication content.
            if claim:
                matches.append(ev.evidence_id)

        if matches:
            return SkinSafetyMinimumResult(
                satisfied=True,
                summary=f"PASS contraindications evidence={matches}",
                matching_evidence_ids=matches,
            )

        return SkinSafetyMinimumResult(
            satisfied=False,
            summary=(
                "require field=contraindications with qa_status=VERIFIED and "
                "(non-empty claim OR claim_type=UNKNOWN); "
                "PENDING/NEEDS_REVIEW/REJECTED/CONFLICT/unrelated fields do not satisfy"
            ),
            matching_evidence_ids=[],
        )

    @staticmethod
    def _is_contraindications_field(field: Optional[str]) -> bool:
        return (field or "").strip().casefold() == _FIELD
