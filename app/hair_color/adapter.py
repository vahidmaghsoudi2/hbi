"""Isolated HBI hair-colour engine adapter boundary.

This module is deliberately engine-neutral. It does not implement hair-colour
chemistry, infer facts from images, access the database, or publish results.
The caller supplies an engine callable; tests use synthetic-only engines.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from copy import deepcopy
from typing import Any


CONTRACT_VERSION = "0.2-draft"

OPERATIONS = frozenset({"EVALUATE_CASE", "ANSWER_QUESTION", "REEVALUATE"})
ENGINE_STATES = frozenset({
    "SUGGESTION_REVIEWABLE",
    "CONDITIONAL_SUGGESTION",
    "NEEDS_MORE_INFORMATION",
    "STOP_OR_REFER_WITH_REASON",
})
CONSULTATION_STATES = frozenset({
    "SYSTEM_REASONED_SUGGESTION",
    "NEEDS_INFORMATION_OR_TEST",
    "NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW",
    "SAFETY_STOP_NO_EXECUTION_SUGGESTION",
    "OUT_OF_V1_SCOPE",
})
REASON_CODES = frozenset({
    "DATA_GAP",
    "KNOWLEDGE_GAP",
    "ENGINE_FAIL",
    "CONFLICTING_DATA",
    "SAFETY_CONCERN",
    "OUT_OF_SCOPE",
    "STALE_CASE_VERSION",
})

_REQUEST_FIELDS = (
    "contract_version",
    "request_id",
    "operation",
    "case_ref",
    "case_version",
    "target_version",
    "case_context",
    "evidence_context",
    "policy_context",
)
_RESPONSE_FIELDS = (
    "request_id",
    "case_ref",
    "evaluated_case_version",
    "evaluated_target_version",
    "engine_state",
    "consultation_status",
    "reason_codes",
    "summary",
    "options",
    "missing_information",
    "evidence_refs",
    "limitations",
    "next_step",
)

# The contract explicitly excludes chemical execution instructions and
# excludes the engine from changing authoritative client/workflow decisions.
_FORBIDDEN_OUTPUT_KEYS = frozenset({
    "chemical_instruction_allowed",
    "formula",
    "oxidant_percentage",
    "processing_time",
    "acceptance",
    "execution_consent",
    "workflow_state",
    "decision_events",
    "stop_event",
    "performed_steps",
})


class AdapterContractError(ValueError):
    """Request or engine response violates the approved adapter boundary."""


class EngineExecutionFailure(RuntimeError):
    """The injected engine failed; no consultation result is returned."""

    reason_code = "ENGINE_FAIL"


def _has_forbidden_key(value: Any) -> str | None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            normalized = str(key).strip().lower()
            if normalized in _FORBIDDEN_OUTPUT_KEYS:
                return str(key)
            found = _has_forbidden_key(nested)
            if found is not None:
                return found
    elif isinstance(value, (list, tuple)):
        for nested in value:
            found = _has_forbidden_key(nested)
            if found is not None:
                return found
    return None


def _require_nonempty_string(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise AdapterContractError(f"{field} must be a non-empty string")


def _require_version(value: Any, field: str) -> None:
    # bool is an int subclass in Python, but is not a valid version number.
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise AdapterContractError(f"{field} must be a positive integer")


def validate_request(request: Mapping[str, Any]) -> None:
    """Validate only fields and values already named by Adapter Contract 0.2."""
    if not isinstance(request, Mapping):
        raise AdapterContractError("request must be an object")

    missing = [field for field in _REQUEST_FIELDS if field not in request]
    if missing:
        raise AdapterContractError("request missing required fields: " + ", ".join(missing))

    if request["contract_version"] != CONTRACT_VERSION:
        raise AdapterContractError("unsupported contract_version")

    _require_nonempty_string(request["request_id"], "request_id")
    _require_nonempty_string(request["case_ref"], "case_ref")

    if request["operation"] not in OPERATIONS:
        raise AdapterContractError("unsupported operation")

    _require_version(request["case_version"], "case_version")
    _require_version(request["target_version"], "target_version")

    if not isinstance(request["case_context"], Mapping):
        raise AdapterContractError("case_context must be an object")
    if not isinstance(request["evidence_context"], list):
        raise AdapterContractError("evidence_context must be an array")
    if not isinstance(request["policy_context"], Mapping):
        raise AdapterContractError("policy_context must be an object")

    forbidden = _has_forbidden_key(request)
    if forbidden is not None:
        raise AdapterContractError(f"request contains prohibited field: {forbidden}")


def validate_response(request: Mapping[str, Any], response: Mapping[str, Any]) -> None:
    """Fail closed on malformed, mismatched, or out-of-bound engine output."""
    if not isinstance(response, Mapping):
        raise AdapterContractError("engine response must be an object")

    missing = [field for field in _RESPONSE_FIELDS if field not in response]
    if missing:
        raise AdapterContractError("engine response missing required fields: " + ", ".join(missing))

    for field in ("request_id", "case_ref"):
        if response[field] != request[field]:
            raise AdapterContractError(f"engine response {field} does not match request")

    if response["evaluated_case_version"] != request["case_version"]:
        raise AdapterContractError("engine response case version does not match request")
    if response["evaluated_target_version"] != request["target_version"]:
        raise AdapterContractError("engine response target version does not match request")

    if response["engine_state"] not in ENGINE_STATES:
        raise AdapterContractError("unknown engine_state")
    if response["consultation_status"] not in CONSULTATION_STATES:
        raise AdapterContractError("unknown consultation_status")

    reason_codes = response["reason_codes"]
    if not isinstance(reason_codes, list) or any(
        not isinstance(code, str) or code not in REASON_CODES for code in reason_codes
    ):
        raise AdapterContractError("reason_codes contains an unknown or malformed value")

    if "ENGINE_FAIL" in reason_codes:
        raise EngineExecutionFailure("engine failure cannot be returned as a successful consultation")

    _require_nonempty_string(response["summary"], "summary")

    for field in ("options", "missing_information", "evidence_refs", "limitations"):
        if not isinstance(response[field], list):
            raise AdapterContractError(f"{field} must be an array")

    if len(response["options"]) > 3:
        raise AdapterContractError("engine returned more than three candidate options")
    if any(not isinstance(option, Mapping) for option in response["options"]):
        raise AdapterContractError("each candidate option must be an object")
    if any(not isinstance(ref, str) or not ref.strip() for ref in response["evidence_refs"]):
        raise AdapterContractError("evidence_refs must contain non-empty strings")

    if not isinstance(response["next_step"], Mapping):
        raise AdapterContractError("next_step must be an object")

    blocking = (
        response["engine_state"] in {"NEEDS_MORE_INFORMATION", "STOP_OR_REFER_WITH_REASON"}
        or response["consultation_status"] in {
            "NEEDS_INFORMATION_OR_TEST",
            "SAFETY_STOP_NO_EXECUTION_SUGGESTION",
            "OUT_OF_V1_SCOPE",
        }
        or any(code in reason_codes for code in {
            "DATA_GAP",
            "KNOWLEDGE_GAP",
            "CONFLICTING_DATA",
            "SAFETY_CONCERN",
            "OUT_OF_SCOPE",
            "STALE_CASE_VERSION",
        })
    )
    if blocking and response["options"]:
        raise AdapterContractError("a blocked consultation response cannot contain candidate options")

    forbidden = _has_forbidden_key(response)
    if forbidden is not None:
        raise AdapterContractError(f"engine response contains prohibited field: {forbidden}")


class HairColorAdapter:
    """Stateless adapter around an explicitly injected consultation engine."""

    def __init__(self, engine: Callable[[dict[str, Any]], Mapping[str, Any]]) -> None:
        if not callable(engine):
            raise TypeError("engine must be callable")
        self._engine = engine

    def evaluate(self, request: Mapping[str, Any]) -> dict[str, Any]:
        validate_request(request)
        engine_input = deepcopy(dict(request))
        try:
            raw_response = self._engine(engine_input)
        except Exception as exc:
            raise EngineExecutionFailure("consultation engine execution failed") from exc

        validate_response(request, raw_response)
        # Do not expose the engine's mutable object to downstream callers.
        return deepcopy(dict(raw_response))
