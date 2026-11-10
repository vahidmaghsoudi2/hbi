"""Fail-closed specialist output and review contract for HBI Hair row 69.

This module defines a synthetic-only, non-persistent contract. It does not
produce hair-colour advice, chemical parameters, client-visible output, or
permission to execute a service. Professional review is an explicit,
version-bound event and is never inferred from a technical QA role.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re
from typing import Iterable


_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class ResponseType(str, Enum):
    REVIEWABLE_SUGGESTION = "REVIEWABLE_SUGGESTION"
    NEEDS_MORE_INFORMATION = "NEEDS_MORE_INFORMATION"
    NEEDS_IN_PERSON_REVIEW = "NEEDS_IN_PERSON_REVIEW"
    SAFETY_STOP = "SAFETY_STOP"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"


class MotorState(str, Enum):
    REVIEWABLE_SUGGESTION = "REVIEWABLE_SUGGESTION"
    CONDITIONAL_SUGGESTION = "CONDITIONAL_SUGGESTION"
    REQUEST_MORE_INFORMATION = "REQUEST_MORE_INFORMATION"
    STOP_OR_REFER = "STOP_OR_REFER"


class GateStatus(str, Enum):
    READY_FOR_SPECIALIST_REVIEW = "READY_FOR_SPECIALIST_REVIEW"
    DATA_GAP = "DATA_GAP"
    KNOWLEDGE_GAP = "KNOWLEDGE_GAP"
    ENGINE_FAIL = "ENGINE_FAIL"
    SAFETY_STOP = "SAFETY_STOP"
    REQUIRES_IN_PERSON_REVIEW = "REQUIRES_IN_PERSON_REVIEW"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"


class ReviewDecision(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    REQUEST_REVISION = "REQUEST_REVISION"


@dataclass(frozen=True)
class EvidenceRef:
    evidence_id: str
    evidence_type: str
    source_reference: str
    verification_status: str
    content_sha256: str
    scope: str


@dataclass(frozen=True)
class SpecialistOutput:
    """Proposed response envelope; all fields are bound to one synthetic run."""

    case_id: str
    case_version: str
    goal_version: str
    run_id: str
    proposal_id: str
    response_type: ResponseType
    motor_state: MotorState
    data_complete: bool
    missing_data_fields: tuple[str, ...] = ()
    reason_code: str | None = None
    evidence: tuple[EvidenceRef, ...] = ()
    synthetic_data: bool = True
    # Deliberately not a place to carry a chemical or client-facing suggestion.
    recommendation_payload: None = None


@dataclass(frozen=True)
class GateResult:
    status: GateStatus
    publishable_to_internal_review: bool
    reason_codes: tuple[str, ...]
    missing_evidence_types: tuple[str, ...] = ()


@dataclass(frozen=True)
class SpecialistReview:
    proposal_id: str
    run_id: str
    case_id: str
    case_version: str
    goal_version: str
    reviewer_id: str
    reviewer_role: str
    professional_qualification_verified: bool
    decision: ReviewDecision
    reason: str
    # Explicit invariants: a review never means client acceptance or consent.
    client_acceptance: bool = False
    execution_consent: bool = False
    client_visible: bool = False
    execution_authorized: bool = False
    persisted: bool = False


# A positive specialist review is blocked unless all four evidence classes
# are present, verified, source-addressable, scoped, and hash-bound.
REQUIRED_EVIDENCE_BY_RESPONSE: dict[ResponseType, frozenset[str]] = {
    ResponseType.REVIEWABLE_SUGGESTION: frozenset({
        "PRODUCT_IDENTITY",
        "PRODUCT_DOCUMENTATION",
        "APPLICABLE_RULE_SOURCE",
        "RULE_VALIDATION",
    }),
    ResponseType.NEEDS_MORE_INFORMATION: frozenset(),
    ResponseType.NEEDS_IN_PERSON_REVIEW: frozenset(),
    ResponseType.SAFETY_STOP: frozenset(),
    ResponseType.OUT_OF_SCOPE: frozenset(),
}


def _evidence_is_valid(item: EvidenceRef) -> bool:
    return bool(
        item.evidence_id.strip()
        and item.evidence_type.strip()
        and item.source_reference.strip()
        and item.scope.strip()
        and item.verification_status == "VERIFIED"
        and _SHA256_RE.fullmatch(item.content_sha256 or "")
    )


def evaluate_specialist_output(output: SpecialistOutput, *, engine_ok: bool = True) -> GateResult:
    """Apply ordered gates; internal review is the maximum permitted exposure."""
    if not isinstance(output, SpecialistOutput):
        raise TypeError("output must be a SpecialistOutput")

    # Internal control failure takes precedence over every other state.
    if not engine_ok:
        return GateResult(GateStatus.ENGINE_FAIL, False, ("ENGINE_FAIL",))

    if (
        output.synthetic_data is not True
        or not isinstance(output.case_id, str)
        or not output.case_id.startswith("SYNTHETIC-")
    ):
        return GateResult(GateStatus.ENGINE_FAIL, False, ("SYNTHETIC_ONLY_POLICY_VIOLATION",))

    if not all((output.case_version.strip(), output.goal_version.strip(), output.run_id.strip(), output.proposal_id.strip())):
        return GateResult(GateStatus.DATA_GAP, False, ("VERSION_OR_RUN_ID_MISSING",))

    if not isinstance(output.response_type, ResponseType) or not isinstance(output.motor_state, MotorState):
        return GateResult(GateStatus.ENGINE_FAIL, False, ("UNKNOWN_RESPONSE_OR_MOTOR_STATE",))

    # Terminal response classes are handled before generic data completeness:
    # an active safety stop must never be downgraded to a routine data gap.
    if output.response_type == ResponseType.SAFETY_STOP:
        if output.motor_state != MotorState.STOP_OR_REFER or not output.reason_code:
            return GateResult(GateStatus.ENGINE_FAIL, False, ("SAFETY_STOP_CONTRACT_INVALID",))
        return GateResult(GateStatus.SAFETY_STOP, False, ("SAFETY_STOP",))

    if output.response_type == ResponseType.OUT_OF_SCOPE:
        if output.motor_state != MotorState.STOP_OR_REFER or not output.reason_code:
            return GateResult(GateStatus.ENGINE_FAIL, False, ("OUT_OF_SCOPE_CONTRACT_INVALID",))
        return GateResult(GateStatus.OUT_OF_SCOPE, False, ("OUT_OF_SCOPE",))

    if output.response_type == ResponseType.NEEDS_IN_PERSON_REVIEW:
        if output.motor_state != MotorState.STOP_OR_REFER or not output.reason_code:
            return GateResult(GateStatus.ENGINE_FAIL, False, ("IN_PERSON_REVIEW_CONTRACT_INVALID",))
        return GateResult(
            GateStatus.REQUIRES_IN_PERSON_REVIEW,
            False,
            ("IN_PERSON_REVIEW_REQUIRED",),
        )

    if output.response_type == ResponseType.NEEDS_MORE_INFORMATION:
        if output.motor_state != MotorState.REQUEST_MORE_INFORMATION or not output.missing_data_fields:
            return GateResult(GateStatus.DATA_GAP, False, ("REQUIRED_MISSING_DATA_FIELDS_NOT_DECLARED",))
        return GateResult(GateStatus.DATA_GAP, False, ("REQUIRED_DATA_MISSING",))

    if output.motor_state not in {
        MotorState.REVIEWABLE_SUGGESTION,
        MotorState.CONDITIONAL_SUGGESTION,
    }:
        return GateResult(GateStatus.ENGINE_FAIL, False, ("RESPONSE_MOTOR_STATE_MISMATCH",))
    if output.recommendation_payload is not None:
        return GateResult(GateStatus.ENGINE_FAIL, False, ("RAW_RECOMMENDATION_PAYLOAD_FORBIDDEN",))

    if not output.data_complete:
        return GateResult(GateStatus.DATA_GAP, False, ("REQUIRED_DATA_INCOMPLETE",))

    required = REQUIRED_EVIDENCE_BY_RESPONSE[output.response_type]
    verified_types = {
        item.evidence_type
        for item in output.evidence
        if _evidence_is_valid(item)
    }
    missing = tuple(sorted(required - verified_types))
    if missing:
        return GateResult(
            GateStatus.KNOWLEDGE_GAP,
            False,
            ("REQUIRED_EVIDENCE_MISSING_OR_UNVERIFIED",),
            missing,
        )

    return GateResult(GateStatus.READY_FOR_SPECIALIST_REVIEW, True, ())


def record_specialist_review(
    output: SpecialistOutput,
    gate: GateResult,
    *,
    reviewer_id: str,
    reviewer_role: str,
    professional_qualification_verified: bool,
    decision: ReviewDecision,
    reason: str,
    reviewed_case_version: str,
    reviewed_goal_version: str,
) -> SpecialistReview:
    """Validate a one-version specialist review; returns an in-memory record only.

    Product Owner owns specialist designation and qualification attestation.
    This pure contract checks the explicit attestation flag and designated role;
    it does not independently investigate or certify a person's credentials.
    """
    if not gate.publishable_to_internal_review or gate.status != GateStatus.READY_FOR_SPECIALIST_REVIEW:
        raise ValueError("Output is not eligible for specialist review")
    if reviewer_role != "HAIR_DOMAIN_EXPERT" or professional_qualification_verified is not True:
        raise PermissionError("A PO-designated Hair Domain Expert with explicit PO qualification attestation is required; operational QA/PO/Admin roles alone are not specialist designation")
    if not isinstance(decision, ReviewDecision):
        raise ValueError("A recognized specialist review decision is required")
    if not reviewer_id.strip() or not reason.strip():
        raise ValueError("Reviewer identity and decision reason are required")
    if (
        reviewed_case_version != output.case_version
        or reviewed_goal_version != output.goal_version
    ):
        raise ValueError("Review must target the exact case and goal versions")
    return SpecialistReview(
        proposal_id=output.proposal_id,
        run_id=output.run_id,
        case_id=output.case_id,
        case_version=output.case_version,
        goal_version=output.goal_version,
        reviewer_id=reviewer_id,
        reviewer_role=reviewer_role,
        professional_qualification_verified=True,
        decision=decision,
        reason=reason,
    )


def rejected_proposal_may_be_reactivated(
    proposal_id: str,
    reviews: Iterable[SpecialistReview],
) -> bool:
    """A rejected proposal is terminal; alternatives require a new proposal ID."""
    return not any(
        item.proposal_id == proposal_id and item.decision == ReviewDecision.REJECT
        for item in reviews
    )


def revision_requires_new_proposal_id(
    previous: SpecialistReview,
    next_proposal_id: str,
) -> bool:
    """A revision request cannot be satisfied by silently mutating the old proposal."""
    if previous.decision != ReviewDecision.REQUEST_REVISION:
        raise ValueError("Previous review did not request a revision")
    return bool(next_proposal_id.strip() and next_proposal_id != previous.proposal_id)


__all__ = [
    "EvidenceRef",
    "GateResult",
    "GateStatus",
    "MotorState",
    "REQUIRED_EVIDENCE_BY_RESPONSE",
    "ResponseType",
    "ReviewDecision",
    "SpecialistOutput",
    "SpecialistReview",
    "evaluate_specialist_output",
    "record_specialist_review",
    "rejected_proposal_may_be_reactivated",
    "revision_requires_new_proposal_id",
]
