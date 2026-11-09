"""Controlled, read-only API boundary for HBI hair catalog identity lookup.

This endpoint is intentionally limited to CATALOG_READY. It accepts observed
identity fields only; callers cannot submit or assert catalog approval,
edition, capture metadata, or content hashes. The server-side reference
provider is fail-closed until a primary approved catalog artifact is wired.
No database writes, customer profile reads, event persistence, or service
execution occur here.
"""
from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict

from app.core.authorization import require_any_role
from app.domain.hair_service_scope import evaluate_hair_service_scope
from app.domain.hair_catalog_identity_lookup import (
    CatalogIdentity,
    CatalogReference,
    build_catalog_decision_output,
    decide_catalog_output_presentation,
    lookup_catalog_identity,
)
from app.models.user_role import ROLE_ADMIN, ROLE_PO, ROLE_REVIEWER_QA

router = APIRouter()


class CatalogIdentityInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    brand: str | None = None
    series: str | None = None
    shade_number: str | None = None
    shade_name: str | None = None
    size_value: str | None = None
    size_unit: str | None = None

    def to_domain(self) -> CatalogIdentity:
        return CatalogIdentity(
            brand=self.brand,
            series=self.series,
            shade_number=self.shade_number,
            shade_name=self.shade_name,
            size_value=self.size_value,
            size_unit=self.size_unit,
        )


class HairCatalogLookupRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    service_kind: str
    expected: CatalogIdentityInput
    observed: CatalogIdentityInput


class HairCatalogLookupResponse(BaseModel):
    status: str
    display_allowed: bool
    message: str


def get_approved_hair_catalog_reference() -> tuple[str, CatalogReference] | None:
    """Return the PO-approved, server-owned Raeaka Bijourka snapshot reference.

    The source snapshot manifest is stored in
    data/catalogs/hair/bijourka/raeaka_catalog_snapshot_2026-11-09.json.
    Its snapshot label is a capture identifier, not a publisher-issued edition.
    """
    return (
        "HBI-HAIR-CATALOG-BIJOURKA-RAEAKA-SNAPSHOT-2026-11-09",
        CatalogReference(
            source_kind="RAEAKA_BIJOURKA_CATALOG",
            approval_status="PO_APPROVED",
            url="https://raeaka.com/آلبوم-رنگ-مو-بیجورکا/",
            edition_label="RAEAKA-WEB-CATALOG-SNAPSHOT-2026-11-09",
            captured_at="2026-11-09T15:00:00+01:00",
            content_sha256=None,
        ),
    )


@router.post(
    "/catalog-identity/lookup",
    response_model=HairCatalogLookupResponse,
)
async def lookup_hair_catalog_identity(
    payload: HairCatalogLookupRequest,
    approved_reference: tuple[str, CatalogReference] | None = Depends(
        get_approved_hair_catalog_reference
    ),
    _auth=Depends(require_any_role(ROLE_REVIEWER_QA, ROLE_PO, ROLE_ADMIN)),
):
    scope = evaluate_hair_service_scope(payload.service_kind)
    if not scope.allowed:
        return HairCatalogLookupResponse(
            status=scope.stop_class or "OUT_OF_DOMAIN",
            display_allowed=False,
            message="این نوع درخواست در محدودهٔ این مسیر نیست؛ نتیجهٔ قطعی ارائه نمی‌شود.",
        )

    # No request field can create, approve, version, or replace this reference.
    if approved_reference is None:
        return HairCatalogLookupResponse(
            status="KNOWLEDGE_GAP",
            display_allowed=False,
            message="مرجع اصلیِ مصوب و نسخه‌دار کاتالوگ هنوز در سامانه ثبت نشده است؛ نتیجهٔ قطعی ارائه نمی‌شود.",
        )

    reference_id, reference = approved_reference
    expected = payload.expected.to_domain()
    observed = payload.observed.to_domain()

    result = lookup_catalog_identity(
        service_kind=payload.service_kind,
        expected=expected,
        observed=observed,
        reference=reference,
    )
    output = build_catalog_decision_output(
        service_kind=payload.service_kind,
        result=result,
        reference_id=reference_id,
        reference=reference,
        expected=expected,
        observed=observed,
        provenance=("SERVER_OWNED_APPROVED_CATALOG_REFERENCE",),
        evidence_reference_pointers=(reference.url,),
        decision_output_id=f"hair-catalog-lookup-{uuid4()}",
    )
    presentation = decide_catalog_output_presentation(output)

    return HairCatalogLookupResponse(
        status=presentation.status,
        display_allowed=presentation.display_allowed,
        message=presentation.public_message_fa,
    )
