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
import json
from pathlib import Path

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
    catalog_item_id: str
    observed: CatalogIdentityInput


class HairCatalogLookupResponse(BaseModel):
    status: str
    display_allowed: bool
    message: str


_CATALOG_SNAPSHOT_PATH = (
    Path(__file__).resolve().parents[3]
    / "data/catalogs/hair/bijourka/raeaka_catalog_snapshot_2026-11-09.json"
)


def _read_catalog_snapshot() -> dict | None:
    """Read the committed server-owned catalog manifest; fail closed on corruption."""
    try:
        manifest = json.loads(_CATALOG_SNAPSHOT_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    if (
        manifest.get("artifact_id")
        != "HBI-HAIR-CATALOG-BIJOURKA-RAEAKA-SNAPSHOT-2026-11-09"
        or manifest.get("status") != "PO_APPROVED_SOURCE_CAPTURE"
        or manifest.get("brand") != "Bijourka"
        or not isinstance(manifest.get("catalog_items"), list)
    ):
        return None
    return manifest


def get_approved_hair_catalog_reference() -> tuple[str, CatalogReference] | None:
    """Return a server-owned reference derived from the committed PO-approved manifest."""
    manifest = _read_catalog_snapshot()
    if manifest is None:
        return None
    source = manifest.get("source", {})
    return (
        manifest["artifact_id"],
        CatalogReference(
            source_kind=source.get("source_kind"),
            approval_status="PO_APPROVED",
            url=source.get("url"),
            edition_label=source.get("snapshot_label"),
            captured_at=source.get("captured_at"),
            content_sha256=source.get("source_content_sha256"),
        ),
    )


def get_approved_hair_catalog_items() -> dict[str, CatalogIdentity]:
    """Return catalog identities keyed by server-owned stable item IDs."""
    manifest = _read_catalog_snapshot()
    if manifest is None:
        return {}
    items: dict[str, CatalogIdentity] = {}
    for item in manifest["catalog_items"]:
        if not isinstance(item, dict):
            return {}
        item_id = item.get("item_id")
        values = {
            key: item.get(key)
            for key in (
                "brand", "series", "shade_number", "shade_name",
                "size_value", "size_unit",
            )
        }
        if (
            not isinstance(item_id, str)
            or not item_id
            or item_id in items
            or not all(isinstance(value, str) and value.strip() for value in values.values())
        ):
            return {}
        items[item_id] = CatalogIdentity(**values)
    return items


@router.post(
    "/catalog-identity/lookup",
    response_model=HairCatalogLookupResponse,
)
async def lookup_hair_catalog_identity(
    payload: HairCatalogLookupRequest,
    approved_reference: tuple[str, CatalogReference] | None = Depends(
        get_approved_hair_catalog_reference
    ),
    catalog_items: dict[str, CatalogIdentity] = Depends(
        get_approved_hair_catalog_items
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

    # Catalog identity and approval metadata are server-owned, never caller-supplied.
    if approved_reference is None or not catalog_items:
        return HairCatalogLookupResponse(
            status="KNOWLEDGE_GAP",
            display_allowed=False,
            message="Snapshot کاتالوگ مصوب در سامانه قابل بازیابی نیست؛ نتیجهٔ قطعی ارائه نمی‌شود.",
        )

    expected = catalog_items.get(payload.catalog_item_id)
    if expected is None:
        return HairCatalogLookupResponse(
            status="KNOWLEDGE_GAP",
            display_allowed=False,
            message="شناسهٔ قلم در Snapshot کاتالوگ ثبت‌شده وجود ندارد؛ نتیجهٔ قطعی ارائه نمی‌شود.",
        )

    reference_id, reference = approved_reference
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
