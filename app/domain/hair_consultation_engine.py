"""Fail-closed, computed-only HBI Hair consultation decision kernel.

This is a safety-gate kernel, not a product-selection or colour-formula engine.
It evaluates synthetic case completeness, current service scope, and safety.
Any supplied candidate payload is immediately blocked as out of scope; no
product options, chemical instructions, or client recommendations are returned.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
import re

from app.domain.hair_data_governance import (
    is_permitted_synthetic_case,
    is_permitted_synthetic_identifier,
    is_permitted_field_name,
    is_permitted_numeric_version,
)
from app.domain.hair_service_scope import evaluate_hair_service_scope


EngineState = Literal[
    "SUGGESTION_REVIEWABLE",
    "CONDITIONAL_SUGGESTION",
    "NEEDS_MORE_INFORMATION",
    "STOP_OR_REFER_WITH_REASON",
]
ConsultationStatus = Literal[
    "SYSTEM_REASONED_SUGGESTION",
    "NEEDS_INFORMATION_OR_TEST",
    "NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW",
    "SAFETY_STOP_NO_EXECUTION_SUGGESTION",
    "OUT_OF_V1_SCOPE",
]
ReasonCode = Literal[
    "DATA_GAP",
    "KNOWLEDGE_GAP",
    "ENGINE_FAIL",
    "CONFLICTING_DATA",
    "SAFETY_CONCERN",
    "OUT_OF_SCOPE",
    "STALE_CASE_VERSION",
]
SafetyState = Literal["CLEAR", "STOP", "UNKNOWN"]
EvidenceStatus = Literal[
    "DISCOVERED",
    "IDENTITY_UNCONFIRMED",
    "SECONDARY_ONLY",
    "CAPTURED_UNVERIFIED",
    "VERIFIED_SOURCE",
    "VERIFIED_APPLICABLE",
    "CONFLICTED",
    "SUPERSEDED",
    "REJECTED",
]
NoOptionCause = Literal[
    "NEEDS_INFORMATION",
    "NEEDS_IN_PERSON_REVIEW",
    "SAFETY_CONCERN",
    "OUT_OF_SCOPE",
    "NOT_FEASIBLE_REQUIRES_SPECIALIST",
]


@dataclass(frozen=True)
class HairFact:
    field_key: str
    value: str | None
    knowledge_state: str
    source_ref: str | None


@dataclass(frozen=True)
class HairProductEvidence:
    evidence_ref: str
    source_ref: str
    status: EvidenceStatus
    claim_id: str
    product_identity_ref: str
    product_version: str
    market_region: str
    content_sha256: str


@dataclass(frozen=True)
class HairSpecialistRule:
    rule_ref: str
    rule_version: str
    status: Literal["DRAFT", "REVIEWED", "APPROVED", "ACTIVE", "RETIRED"]
    scope: str
    product_identity_ref: str
    product_version: str
    market_region: str
    evidence_refs: tuple[str, ...]
    specialist_review_ref: str


@dataclass(frozen=True)
class HairCandidateOption:
    option_ref: str
    summary: str
    rank: int
    rule_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]


@dataclass(frozen=True)
class HairConsultationRequest:
    case_id: str
    synthetic_data: bool
    case_version: str
    target_version: str
    service_kind: str
    required_fields: tuple[str, ...]
    facts: tuple[HairFact, ...]
    safety_state: SafetyState
    product_identity_ref: str | None
    product_version: str | None
    market_region: str | None
    evidence: tuple[HairProductEvidence, ...] = ()
    rules: tuple[HairSpecialistRule, ...] = ()
    candidates: tuple[HairCandidateOption, ...] = ()
    specialist_assessment_required: bool = False
    no_option_cause: NoOptionCause | None = None
    engine_ok: bool = True


@dataclass(frozen=True)
class HairConsultationOption:
    option_ref: str
    summary: str
    rank: int
    rule_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]


@dataclass(frozen=True)
class HairConsultationResult:
    run_outcome: Literal["SUCCESS", "ENGINE_FAILURE"]
    case_id: str
    case_version: str
    target_version: str
    engine_state: EngineState | None
    consultation_status: ConsultationStatus | None
    reason_codes: tuple[ReasonCode, ...]
    summary: str
    options: tuple[HairConsultationOption, ...]
    missing_information: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    limitations: tuple[str, ...]
    next_step: str
    persistence: Literal["COMPUTED_ONLY"] = "COMPUTED_ONLY"
    publication_eligible: bool = False


_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_ALLOWED_RULE_SCOPE = "HAIR_COLOR_RECOMMENDATION"
CANDIDATE_SELECTION_ENABLED = False
_ALLOWED_NO_OPTION_CAUSES = frozenset({
    "NEEDS_INFORMATION",
    "NEEDS_IN_PERSON_REVIEW",
    "SAFETY_CONCERN",
    "OUT_OF_SCOPE",
    "NOT_FEASIBLE_REQUIRES_SPECIALIST",
})


def _failure(request: HairConsultationRequest, summary: str) -> HairConsultationResult:
    # Invalid/non-synthetic envelopes must not echo caller-supplied identifiers.
    # Keep trace identifiers only when the case itself passes the synthetic
    # namespace check; this kernel never returns real-client identifiers.
    synthetic_case = is_permitted_synthetic_identifier(request.case_id)
    return HairConsultationResult(
        run_outcome="ENGINE_FAILURE",
        case_id=request.case_id if synthetic_case else "",
        # Failure envelopes carry no caller-controlled version tokens.
        # This prevents accidental echo of opaque/private values on failed runs.
        case_version="",
        target_version="",
        engine_state=None,
        consultation_status=None,
        reason_codes=("ENGINE_FAIL",),
        summary=summary,
        options=(),
        missing_information=(),
        evidence_refs=(),
        limitations=("No consultation result is available for this run.",),
        next_step="Discard this run and investigate the internal control failure.",
    )


def _blocked(
    request: HairConsultationRequest,
    *,
    engine_state: EngineState,
    consultation_status: ConsultationStatus,
    reason_code: ReasonCode,
    summary: str,
    missing: tuple[str, ...] = (),
    evidence_refs: tuple[str, ...] = (),
    next_step: str,
) -> HairConsultationResult:
    return HairConsultationResult(
        run_outcome="SUCCESS",
        # Blocked outputs are non-publishable and must not echo caller-controlled
        # identifiers, version tokens, or evidence references. Internal trace
        # correlation belongs in a separately governed audit channel, not here.
        case_id="",
        case_version="",
        target_version="",
        engine_state=engine_state,
        consultation_status=consultation_status,
        reason_codes=(reason_code,),
        summary=summary,
        options=(),
        missing_information=missing,
        evidence_refs=(),
        limitations=("No execution instruction or guaranteed colour outcome is produced.",),
        next_step=next_step,
    )


def _validate_envelope(request: HairConsultationRequest) -> tuple[bool, str]:
    if not isinstance(request, HairConsultationRequest):
        return False, "request must be a HairConsultationRequest"
    if not is_permitted_synthetic_case(
        case_id=request.case_id,
        synthetic_data=request.synthetic_data,
    ):
        return False, "PO-66-09 permits synthetic case data only"
    if not is_permitted_numeric_version(request.case_version):
        return False, "case_version must be a bounded numeric version token"
    if not is_permitted_numeric_version(request.target_version):
        return False, "target_version must be a bounded numeric version token"
    if not isinstance(request.service_kind, str) or not request.service_kind.strip():
        return False, "service_kind must be a non-empty string"
    if not isinstance(request.required_fields, tuple) or not all(
        is_permitted_field_name(item) for item in request.required_fields
    ):
        return False, "required_fields must contain bounded schema field names"
    if len(set(request.required_fields)) != len(request.required_fields):
        return False, "required_fields must not contain duplicates"
    if not isinstance(request.facts, tuple) or not all(
        isinstance(item, HairFact) for item in request.facts
    ):
        return False, "facts must contain HairFact records"
    if not isinstance(request.evidence, tuple) or not all(
        isinstance(item, HairProductEvidence) for item in request.evidence
    ):
        return False, "evidence must contain HairProductEvidence records"
    if not isinstance(request.rules, tuple) or not all(
        isinstance(item, HairSpecialistRule) for item in request.rules
    ):
        return False, "rules must contain HairSpecialistRule records"
    if not isinstance(request.candidates, tuple) or not all(
        isinstance(item, HairCandidateOption) for item in request.candidates
    ):
        return False, "candidates must contain HairCandidateOption records"
    if not isinstance(request.safety_state, str) or request.safety_state not in {"CLEAR", "STOP", "UNKNOWN"}:
        return False, "safety_state is invalid"
    if not isinstance(request.engine_ok, bool):
        return False, "engine_ok must be a boolean"
    if not isinstance(request.specialist_assessment_required, bool):
        return False, "specialist_assessment_required must be a boolean"
    if request.no_option_cause is not None and (
        not isinstance(request.no_option_cause, str)
        or request.no_option_cause not in _ALLOWED_NO_OPTION_CAUSES
    ):
        return False, "no_option_cause is invalid"
    return True, ""


def _known_fields(request: HairConsultationRequest) -> set[str]:
    known: set[str] = set()
    seen: set[str] = set()
    for fact in request.facts:
        if (
            not is_permitted_field_name(fact.field_key)
            or fact.field_key in seen
            or fact.knowledge_state not in {
                "KNOWN", "UNKNOWN", "NOT_ASKED", "MISSING", "CONFLICT", "NOT_APPLICABLE"
            }
        ):
            raise ValueError("fact record is malformed or duplicated")
        seen.add(fact.field_key)
        if fact.knowledge_state == "KNOWN":
            if fact.value is None or not isinstance(fact.source_ref, str) or not fact.source_ref.strip():
                raise ValueError("KNOWN facts require a value and source reference")
            known.add(fact.field_key)
        elif fact.value is not None:
            raise ValueError("non-KNOWN facts must not carry a value")
    return known


def _verified_evidence(request: HairConsultationRequest) -> dict[str, HairProductEvidence]:
    result: dict[str, HairProductEvidence] = {}
    for item in request.evidence:
        if (
            not is_permitted_synthetic_identifier(item.evidence_ref)
            or item.evidence_ref in result
            or not isinstance(item.source_ref, str)
            or not item.source_ref.strip()
            or not isinstance(item.claim_id, str)
            or not item.claim_id.strip()
            or item.status not in {
                "DISCOVERED", "IDENTITY_UNCONFIRMED", "SECONDARY_ONLY",
                "CAPTURED_UNVERIFIED", "VERIFIED_SOURCE", "VERIFIED_APPLICABLE",
                "CONFLICTED", "SUPERSEDED", "REJECTED",
            }
            or not isinstance(item.content_sha256, str)
            or not _SHA256_RE.fullmatch(item.content_sha256)
            or not all(
                isinstance(value, str) and value.strip()
                for value in (
                    item.product_identity_ref,
                    item.product_version,
                    item.market_region,
                )
            )
        ):
            raise ValueError("evidence record is malformed or duplicated")
        if item.status == "VERIFIED_APPLICABLE" and (
            item.product_identity_ref != request.product_identity_ref
            or item.product_version != request.product_version
            or item.market_region != request.market_region
        ):
            continue
        if item.status == "VERIFIED_APPLICABLE":
            result[item.evidence_ref] = item
    return result


def _active_rules(
    request: HairConsultationRequest,
    verified_evidence: dict[str, HairProductEvidence],
) -> dict[str, HairSpecialistRule]:
    result: dict[str, HairSpecialistRule] = {}
    for rule in request.rules:
        if (
            not isinstance(rule.rule_ref, str)
            or not rule.rule_ref.strip()
            or not isinstance(rule.rule_version, str)
            or not rule.rule_version.strip()
            or rule.rule_ref in result
            or rule.status not in {"DRAFT", "REVIEWED", "APPROVED", "ACTIVE", "RETIRED"}
            or not isinstance(rule.scope, str)
            or not is_permitted_synthetic_identifier(rule.specialist_review_ref)
            or not isinstance(rule.evidence_refs, tuple)
            or not rule.evidence_refs
            or not all(is_permitted_synthetic_identifier(ref) for ref in rule.evidence_refs)
            or len(set(rule.evidence_refs)) != len(rule.evidence_refs)
            or not all(
                isinstance(value, str) and value.strip()
                for value in (
                    rule.product_identity_ref,
                    rule.product_version,
                    rule.market_region,
                )
            )
        ):
            raise ValueError("rule record is malformed or duplicated")
        if (
            rule.status == "ACTIVE"
            and rule.scope == _ALLOWED_RULE_SCOPE
            and rule.product_identity_ref == request.product_identity_ref
            and rule.product_version == request.product_version
            and rule.market_region == request.market_region
            and set(rule.evidence_refs).issubset(verified_evidence)
        ):
            result[rule.rule_ref] = rule
    return result


def _no_option_result(
    request: HairConsultationRequest,
    cause: NoOptionCause,
    evidence_refs: tuple[str, ...],
) -> HairConsultationResult:
    if cause == "NEEDS_INFORMATION":
        return _blocked(
            request,
            engine_state="STOP_OR_REFER_WITH_REASON",
            consultation_status="NEEDS_INFORMATION_OR_TEST",
            reason_code="KNOWLEDGE_GAP",
            summary="No defensible option is available until the applicable information or evidence gap is resolved.",
            missing=("applicable_information_or_evidence",),
            evidence_refs=evidence_refs,
            next_step="Resolve the identified information or evidence gap, then run a fresh evaluation.",
        )
    if cause == "NEEDS_IN_PERSON_REVIEW" or cause == "NOT_FEASIBLE_REQUIRES_SPECIALIST":
        return _blocked(
            request,
            engine_state="STOP_OR_REFER_WITH_REASON",
            consultation_status="NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW",
            reason_code="DATA_GAP",
            summary="No defensible option is available without the required in-person or qualified specialist assessment.",
            missing=("in_person_or_specialist_assessment",),
            evidence_refs=evidence_refs,
            next_step="Obtain the required assessment and run a fresh evaluation.",
        )
    if cause == "SAFETY_CONCERN":
        return _blocked(
            request,
            engine_state="STOP_OR_REFER_WITH_REASON",
            consultation_status="SAFETY_STOP_NO_EXECUTION_SUGGESTION",
            reason_code="SAFETY_CONCERN",
            summary="A safety constraint blocks an execution suggestion.",
            evidence_refs=evidence_refs,
            next_step="Keep the case stopped and follow the relevant professional-health or product-safety pathway.",
        )
    return _blocked(
        request,
        engine_state="STOP_OR_REFER_WITH_REASON",
        consultation_status="OUT_OF_V1_SCOPE",
        reason_code="OUT_OF_SCOPE",
        summary="The requested action is outside the current first-release scope.",
        evidence_refs=evidence_refs,
        next_step="Use an approved in-scope service or defer the request.",
    )


def evaluate_hair_consultation(request: HairConsultationRequest) -> HairConsultationResult:
    """Evaluate a synthetic case through ordered, fail-closed decision gates.

    The function does not generate colour formulas or application directions.
    Candidate selection is disabled. Any candidate payload is withheld as
    OUT_OF_V1_SCOPE; this function only handles safety and information gates.
    """
    if not isinstance(request, HairConsultationRequest):
        raise TypeError("request must be a HairConsultationRequest")
    if request.engine_ok is not True:
        return _failure(request, "The consultation engine failed; no consultation result is available.")

    valid, error = _validate_envelope(request)
    if not valid:
        return _failure(request, error)

    # Safety takes precedence over routine data gaps.
    if request.safety_state == "STOP":
        return _blocked(
            request,
            engine_state="STOP_OR_REFER_WITH_REASON",
            consultation_status="SAFETY_STOP_NO_EXECUTION_SUGGESTION",
            reason_code="SAFETY_CONCERN",
            summary="A safety constraint blocks an execution suggestion.",
            next_step="Keep the case stopped and follow the applicable safety pathway.",
        )

    scope = evaluate_hair_service_scope(request.service_kind)
    if not scope.allowed:
        return _blocked(
            request,
            engine_state="STOP_OR_REFER_WITH_REASON",
            consultation_status="OUT_OF_V1_SCOPE",
            reason_code="OUT_OF_SCOPE",
            summary="This service kind is outside the currently enabled Hair service scope.",
            next_step="Do not route this request through the catalog-only service.",
        )

    if request.candidates:
        return _blocked(
            request,
            engine_state="STOP_OR_REFER_WITH_REASON",
            consultation_status="OUT_OF_V1_SCOPE",
            reason_code="OUT_OF_SCOPE",
            summary="Product-option selection is disabled in this non-operational safety kernel.",
            next_step="Do not present or rank product options; use only safety, data-gap, and referral handling.",
        )

    try:
        known = _known_fields(request)
    except (TypeError, ValueError):
        return _failure(request, "Case fact integrity validation failed.")

    missing = tuple(field for field in request.required_fields if field not in known)
    if missing or request.safety_state == "UNKNOWN":
        if request.safety_state == "UNKNOWN":
            missing = tuple(dict.fromkeys((*missing, "safety_status")))
        return _blocked(
            request,
            engine_state="NEEDS_MORE_INFORMATION",
            consultation_status="NEEDS_INFORMATION_OR_TEST",
            reason_code="DATA_GAP",
            summary="Required case information is missing or unresolved; no definitive suggestion is available.",
            missing=missing,
            next_step="Collect only the named missing information and run a fresh evaluation.",
        )

    if request.specialist_assessment_required:
        return _blocked(
            request,
            engine_state="STOP_OR_REFER_WITH_REASON",
            consultation_status="NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW",
            reason_code="DATA_GAP",
            summary="The current case requires an in-person or qualified specialist assessment.",
            missing=("in_person_or_specialist_assessment",),
            next_step="Obtain the assessment and run a fresh evaluation.",
        )

    identity_fields = (request.product_identity_ref, request.product_version, request.market_region)
    if not all(isinstance(value, str) and value.strip() for value in identity_fields):
        return _blocked(
            request,
            engine_state="NEEDS_MORE_INFORMATION",
            consultation_status="NEEDS_INFORMATION_OR_TEST",
            reason_code="DATA_GAP",
            summary="Exact product identity, version, or market is missing.",
            missing=("product_identity_ref", "product_version", "market_region"),
            next_step="Resolve the exact product identity and applicable market/version.",
        )

    try:
        verified_evidence = _verified_evidence(request)
        active_rules = _active_rules(request, verified_evidence)
    except (TypeError, ValueError, AttributeError):
        return _failure(request, "Evidence or rule integrity validation failed.")

    if not verified_evidence or not active_rules:
        return _blocked(
            request,
            engine_state="STOP_OR_REFER_WITH_REASON",
            consultation_status="NEEDS_INFORMATION_OR_TEST",
            reason_code="KNOWLEDGE_GAP",
            summary="No active specialist-reviewed rule is supported by exact applicable product evidence.",
            evidence_refs=tuple(sorted(verified_evidence)),
            next_step="Obtain and review the exact product documents and applicable rule evidence; do not infer chemistry.",
        )

    if request.no_option_cause is not None:
        return _no_option_result(
            request,
            request.no_option_cause,
            tuple(sorted(verified_evidence)),
        )

    return _failure(
        request,
        "No candidate payload or explicit blocking cause was supplied; no valid outcome can be determined.",
    )




__all__ = [
    "HairFact",
    "HairProductEvidence",
    "HairSpecialistRule",
    "HairCandidateOption",
    "HairConsultationRequest",
    "HairConsultationOption",
    "HairConsultationResult",
    "evaluate_hair_consultation",
]
