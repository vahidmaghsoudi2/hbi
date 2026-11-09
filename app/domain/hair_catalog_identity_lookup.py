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

    if not traceability_complete:
        reason = (
            "CATALOG_EDITION_UNKNOWN_FIELD_CONFLICT_UNVERIFIED"
            if mismatched
            else "CATALOG_EDITION_OR_CAPTURE_METADATA_INCOMPLETE"
        )
        return CatalogLookupResult(
            "INCONCLUSIVE", "KNOWLEDGE_GAP", reason,
            matched, mismatched, (), reference.url, reference.edition_label,
            reference.captured_at, reference.content_sha256, False,
        )

    if mismatched:
        return CatalogLookupResult(
            "MISMATCH", None, "CATALOG_IDENTITY_FIELD_CONFLICT",
            matched, mismatched, (), reference.url, reference.edition_label,
            reference.captured_at, reference.content_sha256, True,
        )

    return CatalogLookupResult(
        "MATCH", None, "EXACT_CATALOG_IDENTITY_MATCH",
        matched, (), (), reference.url, reference.edition_label,
        reference.captured_at, reference.content_sha256, True,
    )


# ---------------------------------------------------------------------------
# Slice 5: decision-output lineage, dependency invalidation, and idempotency.
# This remains a pure domain contract: no persistence, events, API, or runtime.
# ---------------------------------------------------------------------------

DependencyImpact = Literal["EFFECTIVE", "NON_EFFECTIVE", "UNKNOWN"]
InvalidationDecision = Literal["INVALIDATE", "PRESERVE", "UNRESOLVED"]
_UNVERSIONED = "UNVERSIONED"
_UNKNOWN_EDITION_LABELS = frozenset(("unknown", "نامشخص"))


@dataclass(frozen=True)
class DependencyChange:
    """An assessed change to one logical dependency of a decision output."""

    dependency_key: str
    impact: DependencyImpact


@dataclass(frozen=True)
class CatalogDecisionOutput:
    """Immutable logical output envelope; it is not a persisted DB record."""

    service_kind: Literal["CATALOG_READY"]
    reference_id: str
    source_kind: str
    source_url: str
    version_label: str
    source_approval_status: str
    source_captured_at: str | None
    source_content_sha256: str | None
    traceability_complete: bool
    provenance: tuple[str, ...]
    outcome: LookupOutcome
    evidence_reference_pointers: tuple[str, ...]
    dependency_keys: tuple[str, ...]
    idempotency_key: tuple[str | None, ...]
    decision_output_id: str
    prior_output_id: str | None = None
    inherited_approval_state: Literal["NONE"] = "NONE"


def _edition_or_unversioned(value: str | None) -> str:
    if not isinstance(value, str) or not value.strip():
        return _UNVERSIONED
    label = value.strip()
    if label.casefold() in _UNKNOWN_EDITION_LABELS:
        return _UNVERSIONED
    return label


def catalog_lookup_idempotency_key(
    *,
    service_kind: str,
    reference_id: str,
    reference: CatalogReference,
    expected: CatalogIdentity,
    observed: CatalogIdentity,
    provenance: tuple[str, ...] = (),
    evidence_reference_pointers: tuple[str, ...] = (),
) -> tuple[str | None, ...]:
    """Return a semantic key; identical inputs yield the same key.

    This key is a logical deduplication contract, not a database uniqueness
    constraint, generated output ID, or cryptographic content hash.
    """
    identity_values = tuple(
        getattr(identity, field)
        for identity in (expected, observed)
        for field in _REQUIRED_IDENTITY_FIELDS
    )
    return (
        "service_kind", service_kind,
        "reference_id", reference_id,
        "source_kind", reference.source_kind,
        "approval_status", reference.approval_status,
        "source_url", reference.url,
        "version_label", _edition_or_unversioned(reference.edition_label),
        "captured_at", reference.captured_at,
        "content_sha256", reference.content_sha256,
        "identity_values", *identity_values,
        "provenance_count", str(len(provenance)), *provenance,
        "evidence_pointer_count", str(len(evidence_reference_pointers)),
        *evidence_reference_pointers,
    )


def build_catalog_decision_output(
    *,
    service_kind: str,
    result: CatalogLookupResult,
    reference_id: str,
    reference: CatalogReference,
    expected: CatalogIdentity,
    observed: CatalogIdentity,
    provenance: tuple[str, ...],
    evidence_reference_pointers: tuple[str, ...],
    decision_output_id: str,
    prior_output_id: str | None = None,
) -> CatalogDecisionOutput:
    """Wrap a completed lookup result with source and dependency lineage."""
    if service_kind != "CATALOG_READY" or not isinstance(service_kind, str):
        raise ValueError("service_kind must be the exact CATALOG_READY identifier")
    if not isinstance(reference_id, str) or not reference_id.strip():
        raise ValueError("reference_id must be a non-empty stable reference")
    if not isinstance(decision_output_id, str) or not decision_output_id.strip():
        raise ValueError("decision_output_id must be a non-empty stable output reference")
    if not isinstance(result, CatalogLookupResult):
        raise TypeError("result must be a CatalogLookupResult")
    if not isinstance(reference, CatalogReference):
        raise TypeError("reference must be a CatalogReference")
    if not isinstance(expected, CatalogIdentity) or not isinstance(observed, CatalogIdentity):
        raise TypeError("expected and observed must be CatalogIdentity values")
    if not isinstance(provenance, tuple) or not all(isinstance(item, str) for item in provenance):
        raise TypeError("provenance must be a tuple of strings")
    if not isinstance(evidence_reference_pointers, tuple) or not all(
        isinstance(item, str) for item in evidence_reference_pointers
    ):
        raise TypeError("evidence_reference_pointers must be a tuple of strings")

    version_label = _edition_or_unversioned(reference.edition_label)
    if result.outcome in ("MATCH", "MISMATCH") and (
        version_label == _UNVERSIONED or not result.traceability_complete
    ):
        raise ValueError("definitive lookup outcomes require a traceable versioned reference")
    if result.outcome in ("MATCH", "MISMATCH") and (
        result.source_url != reference.url
        or result.source_edition != reference.edition_label
        or result.source_captured_at != reference.captured_at
        or result.source_sha256 != reference.content_sha256
    ):
        raise ValueError("definitive lookup outcome metadata must match its reference")

    dependencies = (
        "service_kind",
        "catalog_reference.identity",
        "catalog_reference.version",
        "catalog_reference.source_and_approval",
        "catalog_item.brand",
        "catalog_item.series",
        "catalog_item.shade_number",
        "catalog_item.shade_name",
        "catalog_item.size_value",
        "catalog_item.size_unit",
    )
    return CatalogDecisionOutput(
        service_kind="CATALOG_READY",
        reference_id=reference_id,
        source_kind=reference.source_kind,
        source_url=reference.url,
        version_label=version_label,
        source_approval_status=reference.approval_status,
        source_captured_at=reference.captured_at,
        source_content_sha256=reference.content_sha256,
        traceability_complete=result.traceability_complete,
        provenance=tuple(provenance),
        outcome=result.outcome,
        evidence_reference_pointers=tuple(evidence_reference_pointers),
        dependency_keys=dependencies,
        idempotency_key=catalog_lookup_idempotency_key(
            service_kind=service_kind,
            reference_id=reference_id,
            reference=reference,
            expected=expected,
            observed=observed,
            provenance=tuple(provenance),
            evidence_reference_pointers=tuple(evidence_reference_pointers),
        ),
        decision_output_id=decision_output_id,
        prior_output_id=prior_output_id,
        inherited_approval_state="NONE",
    )


def assess_output_invalidation(
    output: CatalogDecisionOutput,
    changes: tuple[DependencyChange, ...],
) -> InvalidationDecision:
    """Invalidate only on known effective dependencies; unknown stays unresolved."""
    dependencies = frozenset(output.dependency_keys)
    impacts = tuple(
        change.impact
        for change in changes
        if change.dependency_key in dependencies
    )
    if any(impact not in ("EFFECTIVE", "NON_EFFECTIVE", "UNKNOWN") for impact in impacts):
        return "UNRESOLVED"
    if "EFFECTIVE" in impacts:
        return "INVALIDATE"
    if "UNKNOWN" in impacts:
        return "UNRESOLVED"
    return "PRESERVE"


# ---------------------------------------------------------------------------
# Slice 6: controlled presentation and factual event contracts.
# Pure domain only: no UI, persistence, event emission, or state transitions.
# ---------------------------------------------------------------------------

CatalogDisplayStatus = Literal[
    "IDENTITY_MATCH_DISPLAYABLE",
    "IDENTITY_MISMATCH_DISPLAYABLE",
    "WITHHOLD_INCONCLUSIVE",
    "WITHHOLD_STOP",
]
CatalogEventKind = Literal[
    "LOOKUP_COMPLETED",
    "OUTPUT_PRESENTED",
    "CLIENT_QUESTION_RECORDED",
    "CLIENT_ACCEPTANCE_RECORDED",
    "CLIENT_REJECTION_RECORDED",
    "EXECUTION_CONSENT_RECORDED",
    "SPECIALIST_REVIEW_RECORDED",
]
CatalogActorKind = Literal["SYSTEM", "CLIENT", "SPECIALIST", "OPERATOR"]


@dataclass(frozen=True)
class CatalogDisplayDecision:
    """A minimal customer-facing identity status, never a product recommendation."""

    status: CatalogDisplayStatus
    display_allowed: bool
    public_message_code: str
    public_message_fa: str


@dataclass(frozen=True)
class CatalogOccurredEvent:
    """A factual event assertion; construction requires explicit occurrence data."""

    event_kind: CatalogEventKind
    occurred_at: str
    actor_kind: CatalogActorKind
    decision_output_id: str
    evidence_reference_pointer: str


def _valid_timezone_aware_timestamp(value: str) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def decide_catalog_output_presentation(
    output: CatalogDecisionOutput,
) -> CatalogDisplayDecision:
    """Separate internal lookup detail from the only permitted public identity text.

    A displayable result confirms catalog identity only. It does not assert
    suitability for a person, chemical safety, expected color result, or
    authorization to perform a service.
    """
    if not isinstance(output, CatalogDecisionOutput):
        raise TypeError("output must be a CatalogDecisionOutput")

    traceable = (
        output.service_kind == "CATALOG_READY"
        and output.source_kind == _APPROVED_SOURCE_KIND
        and output.source_approval_status == _APPROVED_SOURCE_STATUS
        and output.version_label != _UNVERSIONED
        and output.traceability_complete
        and _valid_capture_timestamp(output.source_captured_at)
        and _valid_sha256(output.source_content_sha256)
    )
    if not traceable:
        return CatalogDisplayDecision(
            "WITHHOLD_INCONCLUSIVE",
            False,
            "CATALOG_IDENTITY_NOT_VERIFIABLE",
            "هویت قلم از مرجع نسخه‌دار و قابل‌ردیابی قابل تأیید نیست؛ نتیجهٔ قطعی نمایش داده نمی‌شود.",
        )

    if output.outcome == "MATCH":
        return CatalogDisplayDecision(
            "IDENTITY_MATCH_DISPLAYABLE",
            True,
            "CATALOG_IDENTITY_MATCH_ONLY",
            "مشخصات این قلم با مرجع نسخه‌دار کاتالوگ تطبیق دارد. این نتیجه به‌معنی تأیید تناسب با فرد، ایمنی یا تضمین نتیجه نیست.",
        )
    if output.outcome == "MISMATCH":
        return CatalogDisplayDecision(
            "IDENTITY_MISMATCH_DISPLAYABLE",
            True,
            "CATALOG_IDENTITY_MISMATCH_ONLY",
            "مشخصات این قلم با مرجع نسخه‌دار کاتالوگ تطبیق ندارد؛ از این تطبیق برای انتخاب یا اجرای خدمت استفاده نشود.",
        )
    if output.outcome == "INCONCLUSIVE":
        return CatalogDisplayDecision(
            "WITHHOLD_INCONCLUSIVE",
            False,
            "CATALOG_LOOKUP_INCONCLUSIVE",
            "اطلاعات موجود برای تأیید هویت این قلم کافی نیست.",
        )
    return CatalogDisplayDecision(
        "WITHHOLD_STOP",
        False,
        "CATALOG_LOOKUP_STOPPED",
        "فرایند شناسایی این قلم متوقف شده است و خروجی قطعی ارائه نمی‌شود.",
    )


_EVENT_ACTOR_RULES: dict[str, str] = {
    "LOOKUP_COMPLETED": "SYSTEM",
    "OUTPUT_PRESENTED": "SYSTEM",
    "CLIENT_QUESTION_RECORDED": "CLIENT",
    "CLIENT_ACCEPTANCE_RECORDED": "CLIENT",
    "CLIENT_REJECTION_RECORDED": "CLIENT",
    "EXECUTION_CONSENT_RECORDED": "CLIENT",
    "SPECIALIST_REVIEW_RECORDED": "SPECIALIST",
}


def build_catalog_occurred_event(
    *,
    event_kind: str,
    occurred_at: str,
    actor_kind: str,
    decision_output_id: str,
    evidence_reference_pointer: str,
    display_decision: CatalogDisplayDecision | None = None,
) -> CatalogOccurredEvent:
    """Describe an event only when its occurrence time and evidence are supplied.

    This constructor does not emit, persist, infer, or backfill events. Client
    acceptance and execution consent are separate event kinds and never imply
    one another. A question is not acceptance. A presented output is not proof
    of client acceptance or execution.
    """
    if not isinstance(event_kind, str) or event_kind not in _EVENT_ACTOR_RULES:
        raise ValueError("event_kind is outside the catalog event contract")
    if not isinstance(actor_kind, str) or actor_kind != _EVENT_ACTOR_RULES[event_kind]:
        raise ValueError("actor_kind does not match the event kind")
    if event_kind == "OUTPUT_PRESENTED" and (
        not isinstance(display_decision, CatalogDisplayDecision)
        or not display_decision.display_allowed
    ):
        raise ValueError("OUTPUT_PRESENTED requires an explicitly displayable output decision")
    if not _valid_timezone_aware_timestamp(occurred_at):
        raise ValueError("occurred_at must be an explicit timezone-aware timestamp")
    if not isinstance(decision_output_id, str) or not decision_output_id.strip():
        raise ValueError("decision_output_id must be an explicit non-empty reference")
    if (
        not isinstance(evidence_reference_pointer, str)
        or not evidence_reference_pointer.strip()
    ):
        raise ValueError("an evidence pointer for the actual occurrence is required")
    return CatalogOccurredEvent(
        event_kind=event_kind,
        occurred_at=occurred_at,
        actor_kind=actor_kind,
        decision_output_id=decision_output_id,
        evidence_reference_pointer=evidence_reference_pointer,
    )
