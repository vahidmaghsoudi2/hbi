"""Pure, fail-closed catalog identity lookup for HBI CATALOG_READY.

Scope: compare one catalog item with one PO-approved catalog reference.
This module does not access Product Master, GTIN, databases, APIs, Skin,
legacy recommendation services, customer data, or chemical/safety rules.

A MATCH requires complete exact identity fields and a traceable, versioned
approved reference. An unknown catalog edition is never silently upgraded
to a verified match.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re
from typing import Literal
from urllib.parse import unquote, urlparse


LookupOutcome = Literal["MATCH", "MISMATCH", "INCONCLUSIVE", "STOP"]
LookupStop = Literal["DATA_GAP", "KNOWLEDGE_GAP", "OUT_OF_DOMAIN", "ENGINE_FAIL"]

_APPROVED_SOURCE_KIND = "RAEAKA_BIJOURKA_CATALOG"
_APPROVED_SOURCE_STATUS = "PO_APPROVED"
_APPROVED_HOST = "raeaka.com"
_APPROVED_PATHS = frozenset((
    "/آلبوم-رنگ-مو-بیجورکا/",
    "/product/رنگ-موی-بیجورکا-سِری-طبیعی-شماره-1-مشکی/",
))
_REQUIRED_IDENTITY_FIELDS = (
    "brand",
    "series",
    "shade_number",
    "shade_name",
    "size_value",
    "size_unit",
)


@dataclass(frozen=True)
class CatalogIdentity:
    brand: str | None
    series: str | None
    shade_number: str | None
    shade_name: str | None
    size_value: str | None
    size_unit: str | None


@dataclass(frozen=True)
class CatalogReference:
    source_kind: str
    approval_status: str
    url: str
    edition_label: str | None
    captured_at: str | None
    content_sha256: str | None = None


@dataclass(frozen=True)
class CatalogLookupResult:
    outcome: LookupOutcome
    stop_class: LookupStop | None
    reason_code: str
    matched_fields: tuple[str, ...]
    mismatched_fields: tuple[str, ...]
    missing_fields: tuple[str, ...]
    source_url: str | None
    source_edition: str | None
    source_captured_at: str | None
    source_sha256: str | None
    traceability_complete: bool


def _is_approved_reference(reference: CatalogReference) -> bool:
    """Accept only the exact PO-approved Raeaka Bijourka catalog URL family."""
    if (
        not isinstance(reference.source_kind, str)
        or not isinstance(reference.approval_status, str)
        or reference.source_kind != _APPROVED_SOURCE_KIND
        or reference.approval_status != _APPROVED_SOURCE_STATUS
        or not isinstance(reference.url, str)
    ):
        return False
    try:
        parsed = urlparse(reference.url)
    except (TypeError, ValueError):
        return False
    if parsed.scheme != "https" or parsed.hostname != _APPROVED_HOST:
        return False
    try:
        port = parsed.port
    except ValueError:
        return False
    if parsed.username or parsed.password or port not in (None, 443):
        return False
    if parsed.query or parsed.fragment:
        return False
    return unquote(parsed.path) in _APPROVED_PATHS


def _valid_capture_timestamp(value: str | None) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def _valid_sha256(value: str | None) -> bool:
    return value is None or (
        isinstance(value, str) and re.fullmatch(r"[0-9a-fA-F]{64}", value) is not None
    )


def _missing_identity_fields(identity: CatalogIdentity) -> tuple[str, ...]:
    return tuple(
        field
        for field in _REQUIRED_IDENTITY_FIELDS
        if not isinstance(getattr(identity, field), str)
        or not getattr(identity, field).strip()
    )


def lookup_catalog_identity(
    *,
    service_kind: object,
    expected: CatalogIdentity,
    observed: CatalogIdentity,
    reference: CatalogReference,
) -> CatalogLookupResult:
    """Compare exact catalog identity fields and return a traceable outcome.

    No trimming, case folding, aliases, fuzzy matching, inferred values, or
    fallback to Product Master/GTIN are permitted. A missing edition label
    (including the literal "نامشخص" or "unknown") prevents MATCH and yields
    INCONCLUSIVE/KNOWLEDGE_GAP, while a known field conflict yields MISMATCH.
    """
    if service_kind != "CATALOG_READY" or not isinstance(service_kind, str):
        return CatalogLookupResult(
            "STOP", "OUT_OF_DOMAIN", "SERVICE_KIND_NOT_CATALOG_READY",
            (), (), (), None, None, None, None, False,
        )

    if not isinstance(expected, CatalogIdentity) or not isinstance(observed, CatalogIdentity):
        return CatalogLookupResult(
            "STOP", "DATA_GAP", "IDENTITY_INPUT_INVALID",
            (), (), ("expected_or_observed_identity",),
            reference.url if isinstance(reference, CatalogReference) else None,
            None, None, None, False,
        )

    if not isinstance(reference, CatalogReference) or not _is_approved_reference(reference):
        return CatalogLookupResult(
            "STOP", "KNOWLEDGE_GAP", "APPROVED_CATALOG_REFERENCE_NOT_ESTABLISHED",
            (), (), (), None, None, None, None, False,
        )

    missing = tuple(
        f"expected.{field}" for field in _missing_identity_fields(expected)
    ) + tuple(
        f"observed.{field}" for field in _missing_identity_fields(observed)
    )
    if missing:
        return CatalogLookupResult(
            "STOP", "DATA_GAP", "REQUIRED_IDENTITY_FIELD_MISSING",
            (), (), missing, reference.url, reference.edition_label,
            reference.captured_at, reference.content_sha256, False,
        )

    matched = tuple(
        field for field in _REQUIRED_IDENTITY_FIELDS
        if getattr(expected, field) == getattr(observed, field)
    )
    mismatched = tuple(
        field for field in _REQUIRED_IDENTITY_FIELDS
        if getattr(expected, field) != getattr(observed, field)
    )

    traceability_complete = bool(
        isinstance(reference.edition_label, str)
        and reference.edition_label.strip()
        and reference.edition_label.strip().casefold() not in ("unknown", "نامشخص")
        and _valid_capture_timestamp(reference.captured_at)
        and _valid_sha256(reference.content_sha256)
    )

    if mismatched:
        return CatalogLookupResult(
            "MISMATCH", None, "CATALOG_IDENTITY_FIELD_CONFLICT",
            matched, mismatched, (), reference.url, reference.edition_label,
            reference.captured_at, reference.content_sha256,
            traceability_complete,
        )

    if not traceability_complete:
        return CatalogLookupResult(
            "INCONCLUSIVE", "KNOWLEDGE_GAP",
            "CATALOG_EDITION_OR_CAPTURE_METADATA_INCOMPLETE",
            matched, (), (), reference.url, reference.edition_label,
            reference.captured_at, reference.content_sha256, False,
        )

    return CatalogLookupResult(
        "MATCH", None, "EXACT_CATALOG_IDENTITY_MATCH",
        matched, (), (), reference.url, reference.edition_label,
        reference.captured_at, reference.content_sha256, True,
    )
