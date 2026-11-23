"""Fail-closed publication gate for the current synthetic Hair Color contract.

Only non-advice triage states with no candidate options may pass. Candidate or
specialist-advice publication is deliberately disabled until domain validation
and a separate approved activation path exist.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any


_TRIAGE_STATUSES = frozenset({
    "SAFETY_STOP_NO_EXECUTION_SUGGESTION",
    "OUT_OF_V1_SCOPE",
    "NEEDS_INFORMATION_OR_TEST",
    "NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW",
})
_ALLOWED_REASON_CODES = frozenset({
    "DATA_GAP", "KNOWLEDGE_GAP", "CONFLICTING_DATA", "SAFETY_CONCERN",
    "OUT_OF_SCOPE", "STALE_CASE_VERSION", "NO_VALID_OPTION",
})


def evaluate_publication_gate(
    response: Mapping[str, Any],
    *,
    current_case_version: int,
    current_target_version: int,
) -> dict[str, Any]:
    """Return a publication decision. Never publishes candidates or advice."""
    reasons: list[str] = []
    if not isinstance(response, Mapping):
        response = {}
        reasons.append("RESPONSE_NOT_OBJECT")
    for version_name, current_version in (
        ("evaluated_case_version", current_case_version),
        ("evaluated_target_version", current_target_version),
    ):
        response_version = response.get(version_name)
        if isinstance(response_version, bool) or not isinstance(response_version, int) or response_version < 1:
            reasons.append("INVALID_VERSION_FIELD")
        if isinstance(current_version, bool) or not isinstance(current_version, int) or current_version < 1:
            reasons.append("INVALID_CURRENT_VERSION")
    if response.get("evaluated_case_version") != current_case_version:
        reasons.append("STALE_CASE_VERSION")
    if response.get("evaluated_target_version") != current_target_version:
        reasons.append("STALE_TARGET_VERSION")

    options = response.get("options")
    if not isinstance(options, list) or options:
        reasons.append("CANDIDATE_OUTPUT_DISABLED")

    status = response.get("consultation_status")
    state = response.get("engine_state")
    reason_codes = response.get("reason_codes")
    if not isinstance(status, str) or status not in _TRIAGE_STATUSES:
        reasons.append("STATUS_NOT_ALLOWED_FOR_PUBLICATION")
    if not isinstance(state, str) or state not in {"NEEDS_MORE_INFORMATION", "STOP_OR_REFER_WITH_REASON"}:
        reasons.append("ENGINE_STATE_NOT_ALLOWED_FOR_TRIAGE_PUBLICATION")
    if (
        not isinstance(reason_codes, list)
        or not reason_codes
        or any(not isinstance(code, str) or code not in _ALLOWED_REASON_CODES for code in reason_codes)
    ):
        reasons.append("INVALID_REASON_CODES")
    elif len(reason_codes) != len(set(reason_codes)):
        reasons.append("DUPLICATE_REASON_CODES")

    # Validate status/reason compatibility independently of the adapter so the
    # publication boundary cannot be bypassed with a hand-crafted response.
    reason_codes_valid = isinstance(reason_codes, list) and all(
        isinstance(code, str) and code in _ALLOWED_REASON_CODES for code in reason_codes
    )
    if reason_codes_valid and status == "SAFETY_STOP_NO_EXECUTION_SUGGESTION" and reason_codes != ["SAFETY_CONCERN"]:
        reasons.append("STATUS_REASON_MISMATCH")
    if reason_codes_valid and status == "OUT_OF_V1_SCOPE" and reason_codes != ["OUT_OF_SCOPE"]:
        reasons.append("STATUS_REASON_MISMATCH")
    if reason_codes_valid and status == "NEEDS_INFORMATION_OR_TEST" and not set(reason_codes) <= {
        "DATA_GAP", "CONFLICTING_DATA", "NO_VALID_OPTION"
    }:
        reasons.append("STATUS_REASON_MISMATCH")
    if reason_codes_valid and status == "NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW" and not set(reason_codes) <= {
        "KNOWLEDGE_GAP", "CONFLICTING_DATA", "DATA_GAP", "STALE_CASE_VERSION"
    }:
        reasons.append("STATUS_REASON_MISMATCH")
    if reason_codes_valid and "DATA_GAP" in reason_codes and not response.get("missing_information"):
        reasons.append("DATA_GAP_WITHOUT_DETAILS")
    if not isinstance(response.get("summary"), str) or not response.get("summary", "").strip():
        reasons.append("INVALID_SUMMARY")
    if not isinstance(response.get("request_id"), str) or not response.get("request_id", "").strip():
        reasons.append("INVALID_REQUEST_ID")
    if not isinstance(response.get("case_ref"), str) or not response.get("case_ref", "").strip():
        reasons.append("INVALID_CASE_REF")

    allowed = not reasons
    safe_response = dict(response) if allowed else {
        "request_id": response.get("request_id"),
        "case_ref": response.get("case_ref"),
        "evaluated_case_version": current_case_version,
        "evaluated_target_version": current_target_version,
        "engine_state": "STOP_OR_REFER_WITH_REASON",
        "consultation_status": "NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW",
        "reason_codes": ["KNOWLEDGE_GAP"],
        "summary": "پاسخ از Gate انتشار عبور نکرد؛ پیشنهاد منتشر نمی‌شود و بررسی متخصص لازم است.",
        "options": [],
        "missing_information": [],
        "evidence_refs": [],
        "limitations": ["Publication gate fail-closed; no recommendation or execution advice is published."],
        "next_step": {"action": "SPECIALIST_REVIEW", "reason": "Publication validation failed."},
    }
    return {
        "publication_allowed": allowed,
        "publication_kind": "TRIAGE_ONLY" if allowed else "BLOCKED",
        "reason_codes": reasons,
        "safe_response": safe_response,
        "options": [],
        "execution_authorized": False,
    }
