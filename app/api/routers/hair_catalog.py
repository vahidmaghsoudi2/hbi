"""Controlled, read-only API boundary for HBI hair catalog identity lookup.

This endpoint is intentionally limited to CATALOG_READY. The expected
identity must be an exact row in the PO-approved server-side CSV; the observed
identity is compared field-by-field. Callers cannot submit or assert catalog
approval, edition, capture metadata, or content hashes. Definitive output
remains fail-closed while publisher edition/capture provenance is incomplete.
No database writes, customer profile reads, event persistence, or service
execution occur here.
"""
from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict

from app.core.authorization import require_any_role
from app.domain.hair_service_scope import evaluate_hair_service_scope
from app.domain.hair_catalog_provider import (
    approved_catalog_contains_identity,
    load_approved_hair_catalog_reference,
)
from app.domain.hair_catalog_identity_lookup import (
    CatalogIdentity,
    CatalogReference,
    build_catalog_decision_output,
    decide_catalog_output_presentation,
    lookup_catalog_identity,
)
from app.models.user_role import ROLE_ADMIN, ROLE_PO, ROLE_REVIEWER_QA
from app.domain.hair_knowledge_case_bridge import (
    HairCaseSnapshot,
    HairKnowledgeCaseBridge,
    build_approved_catalog_knowledge_package,
    build_catalog_identity_rule,
)
from app.domain.hair_specialist_view import build_hair_specialist_view

router = APIRouter()


class CatalogIdentityInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    brand: str | None = None
    series: str | None = None
    shade_number: str | None = None
    shade_name: str | None = None
    product_specification: str | None = None
    product_volume: str | None = None

    def to_domain(self) -> CatalogIdentity:
        return CatalogIdentity(
            brand=self.brand,
            series=self.series,
            shade_number=self.shade_number,
            shade_name=self.shade_name,
            product_specification=self.product_specification,
            product_volume=self.product_volume,
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
    """Return the validated server-owned CSV reference, never caller metadata.

    The exact 88-row artifact is loaded and hashed on the server. The API also
    verifies that the submitted expected identity exists in this same
    content-hash snapshot. Publisher edition and capture provenance remain
    unknown, so definitive lookup output stays withheld.
    """
    return load_approved_hair_catalog_reference()




class HairSpecialistPreviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str
    case_version: str
    goal_version: str
    service_kind: str
    catalog_identity: CatalogIdentityInput


@router.post("/specialist-preview")
async def preview_hair_specialist_view(
    payload: HairSpecialistPreviewRequest,
    _auth=Depends(require_any_role(ROLE_REVIEWER_QA, ROLE_PO, ROLE_ADMIN)),
):
    """Render a non-persistent, synthetic-only specialist review projection."""
    if not payload.case_id.startswith("SYNTHETIC-"):
        raise HTTPException(
            status_code=422,
            detail="PO-66-09 permits synthetic case identifiers only.",
        )

    package = build_approved_catalog_knowledge_package()
    if package is None:
        raise HTTPException(
            status_code=503,
            detail="Approved HBI catalog snapshot is unavailable; preview withheld.",
        )
    rule = build_catalog_identity_rule(package)
    case = HairCaseSnapshot(
        case_id=payload.case_id,
        case_version=payload.case_version,
        goal_version=payload.goal_version,
        service_kind=payload.service_kind,
        catalog_identity=payload.catalog_identity.to_domain(),
        synthetic_data=True,
    )
    run = HairKnowledgeCaseBridge().run(
        case=case,
        package=package,
        rule=rule,
        run_id=f"hair-specialist-preview-{uuid4()}",
    )
    return build_hair_specialist_view(run)


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

    # The baseline must be an exact row in the PO-approved server-side CSV.
    # A caller cannot nominate an arbitrary "expected" identity as canonical.
    if not approved_catalog_contains_identity(
        expected,
        expected_content_sha256=reference.content_sha256,
    ):
        return HairCatalogLookupResponse(
            status="WITHHOLD_INCONCLUSIVE",
            display_allowed=False,
            message="مشخصات مبنا در ردیف‌های کاتالوگ مصوب سمت سرور یافت نشد؛ نتیجهٔ قطعی ارائه نمی‌شود.",
        )

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
