"""Isolated HBI hair-colour engine adapter boundary.

This module is deliberately engine-neutral. It does not implement hair-colour
chemistry, infer facts from images, access the database, or publish results.
The caller supplies an engine callable; tests use synthetic-only engines.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from copy import deepcopy
from typing import Any


CONTRACT_VERSION = "0.3-draft"

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
    "NO_VALID_OPTION",
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
_FORBIDDEN_REQUEST_KEYS = frozenset({
    "chemical_instruction_allowed",
    "formula",
    "oxidant_percentage",
    "processing_time",
})
_FORBIDDEN_RESPONSE_KEYS = _FORBIDDEN_REQUEST_KEYS | frozenset({
    "chemical_execution_instructions",
})
_FORBIDDEN_DECISION_KEYS = frozenset({
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


def _has_forbidden_key(value: Any, forbidden_keys: frozenset[str]) -> str | None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            normalized = str(key).strip().lower()
            if normalized in forbidden_keys:
                return str(key)
            found = _has_forbidden_key(nested, forbidden_keys)
            if found is not None:
                return found
    elif isinstance(value, (list, tuple)):
        for nested in value:
            found = _has_forbidden_key(nested, forbidden_keys)
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

    if not isinstance(request["operation"], str) or request["operation"] not in OPERATIONS:
        raise AdapterContractError("unsupported operation")

    _require_version(request["case_version"], "case_version")
    _require_version(request["target_version"], "target_version")

    if not isinstance(request["case_context"], Mapping):
        raise AdapterContractError("case_context must be an object")
    if not isinstance(request["evidence_context"], list):
        raise AdapterContractError("evidence_context must be an array")
    if not isinstance(request["policy_context"], Mapping):
        raise AdapterContractError("policy_context must be an object")

    if request["operation"] == "ANSWER_QUESTION":
        _require_nonempty_string(request.get("question"), "question")
        question_about = request.get("question_about")
        if question_about is not None:
            if not isinstance(question_about, Mapping):
                raise AdapterContractError("question_about must be an object")
            _require_nonempty_string(question_about.get("suggestion_ref"), "question_about.suggestion_ref")
            _require_version(question_about.get("suggestion_version"), "question_about.suggestion_version")
    elif "question" in request or "question_about" in request:
        raise AdapterContractError("question fields are allowed only for ANSWER_QUESTION")

    forbidden = _has_forbidden_key(request, _FORBIDDEN_REQUEST_KEYS)
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

    _require_version(response["evaluated_case_version"], "evaluated_case_version")
    _require_version(response["evaluated_target_version"], "evaluated_target_version")

    if response["evaluated_case_version"] != request["case_version"]:
        raise AdapterContractError("engine response case version does not match request")
    if response["evaluated_target_version"] != request["target_version"]:
        raise AdapterContractError("engine response target version does not match request")

    if not isinstance(response["engine_state"], str) or response["engine_state"] not in ENGINE_STATES:
        raise AdapterContractError("unknown engine_state")
    if not isinstance(response["consultation_status"], str) or response["consultation_status"] not in CONSULTATION_STATES:
        raise AdapterContractError("unknown consultation_status")

    reason_codes = response["reason_codes"]
    if not isinstance(reason_codes, list) or any(
        not isinstance(code, str) or code not in REASON_CODES for code in reason_codes
    ):
        raise AdapterContractError("reason_codes contains an unknown or malformed value")
    if len(reason_codes) != len(set(reason_codes)):
        raise AdapterContractError("reason_codes must not contain duplicates")

    if "ENGINE_FAIL" in reason_codes:
        raise EngineExecutionFailure("engine failure cannot be returned as a successful consultation")

    _require_nonempty_string(response["summary"], "summary")

    forbidden = _has_forbidden_key(response, _FORBIDDEN_RESPONSE_KEYS | _FORBIDDEN_DECISION_KEYS)
    if forbidden is not None:
        raise AdapterContractError(f"engine response contains prohibited field: {forbidden}")



    for field in ("options", "missing_information", "evidence_refs", "limitations"):
        if not isinstance(response[field], list):
            raise AdapterContractError(f"{field} must be an array")

    if len(response["options"]) > 3:
        raise AdapterContractError("engine returned more than three candidate options")
    if any(not isinstance(option, Mapping) for option in response["options"]):
        raise AdapterContractError("each candidate option must be an object")
    if any(not isinstance(ref, str) or not ref.strip() for ref in response["evidence_refs"]):
        raise AdapterContractError("evidence_refs must contain non-empty strings")
    if len(response["evidence_refs"]) != len(set(response["evidence_refs"])):
        raise AdapterContractError("evidence_refs must not contain duplicates")

    supplied_evidence_refs = set()
    for item in request["evidence_context"]:
        if not isinstance(item, Mapping):
            raise AdapterContractError("each evidence_context item must be an object")
        evidence_ref = item.get("evidence_ref")
        _require_nonempty_string(evidence_ref, "evidence_context.evidence_ref")
        if evidence_ref in supplied_evidence_refs:
            raise AdapterContractError("request evidence_context references must be unique")
        supplied_evidence_refs.add(evidence_ref)
    if response["options"] and not response["evidence_refs"]:
        raise AdapterContractError("candidate options require traceable evidence references")
    if any(ref not in supplied_evidence_refs for ref in response["evidence_refs"]):
        raise AdapterContractError("engine response references evidence absent from the request context")

    # Minimal synthetic candidate envelope: traceability structure only; no domain validation.
    candidate_keys = []
    candidate_ranks = []
    for option in response["options"]:
        required_candidate_fields = {"candidate_key", "rank", "summary", "claims"}
        if not required_candidate_fields <= set(option):
            raise AdapterContractError("candidate missing required structural fields")
        if set(option) != required_candidate_fields:
            raise AdapterContractError("candidate contains unexpected structural fields")
        _require_nonempty_string(option["candidate_key"], "candidate_key")
        _require_nonempty_string(option["summary"], "candidate summary")
        rank = option["rank"]
        if isinstance(rank, bool) or not isinstance(rank, int) or rank < 1 or rank > 3:
            raise AdapterContractError("candidate rank must be an integer from 1 to 3")
        if not isinstance(option["claims"], list) or not option["claims"]:
            raise AdapterContractError("candidate claims must be a non-empty array")
        candidate_keys.append(option["candidate_key"])
        candidate_ranks.append(rank)
        for claim in option["claims"]:
            required_claim_fields = {"claim_ref", "claim_text", "rule_ref", "evidence_refs", "support_status"}
            if not isinstance(claim, Mapping) or not required_claim_fields <= set(claim):
                raise AdapterContractError("candidate claim missing required structural fields")
            if set(claim) != required_claim_fields:
                raise AdapterContractError("candidate claim contains unexpected structural fields")
            for field in ("claim_ref", "claim_text", "rule_ref"):
                _require_nonempty_string(claim[field], f"claim {field}")
            if claim["support_status"] != "MOCK_SUPPORTED":
                raise AdapterContractError("candidate claim support_status must be MOCK_SUPPORTED in synthetic contract")
            refs = claim["evidence_refs"]
            if not isinstance(refs, list) or not refs or any(
                not isinstance(ref, str) or not ref.strip() for ref in refs
            ):
                raise AdapterContractError("candidate claim evidence_refs must be non-empty")
            if len(refs) != len(set(refs)):
                raise AdapterContractError("candidate claim evidence_refs must not contain duplicates")
            if any(ref not in supplied_evidence_refs for ref in refs):
                raise AdapterContractError("candidate claim references evidence absent from request context")
            if any(ref not in response["evidence_refs"] for ref in refs):
                raise AdapterContractError("candidate claim evidence must be included in response evidence_refs")
    if len(candidate_keys) != len(set(candidate_keys)):
        raise AdapterContractError("candidate_key values must be unique")
    if candidate_ranks and candidate_ranks != list(range(1, len(candidate_ranks) + 1)):
        raise AdapterContractError("candidate ranks must be unique, contiguous, and ordered starting at 1")

    if any(not isinstance(item, (str, Mapping)) for item in response["missing_information"]):
        raise AdapterContractError("missing_information items must be strings or objects")
    if any(not isinstance(item, str) or not item.strip() for item in response["limitations"]):
        raise AdapterContractError("limitations must contain non-empty strings")
    if not isinstance(response["next_step"], Mapping):
        raise AdapterContractError("next_step must be an object")

    blocking = (
        response["engine_state"] in {"NEEDS_MORE_INFORMATION", "STOP_OR_REFER_WITH_REASON"}
        or response["consultation_status"] in {
            "NEEDS_INFORMATION_OR_TEST",
            "NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW",
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
            "NO_VALID_OPTION",
        })
    )
    if blocking and response["options"]:
        raise AdapterContractError("a blocked consultation response cannot contain candidate options")

    state, status, reasons = response["engine_state"], response["consultation_status"], set(reason_codes)
    is_question = request["operation"] == "ANSWER_QUESTION"
    if state in {"SUGGESTION_REVIEWABLE", "CONDITIONAL_SUGGESTION"}:
        if status != "SYSTEM_REASONED_SUGGESTION" or reasons & {
            "DATA_GAP", "KNOWLEDGE_GAP", "ENGINE_FAIL", "CONFLICTING_DATA",
            "SAFETY_CONCERN", "OUT_OF_SCOPE", "STALE_CASE_VERSION", "NO_VALID_OPTION",
        } or (not is_question and not response["options"]):
            raise AdapterContractError("state/reason/status compatibility violation")
        if is_question and response["options"]:
            raise AdapterContractError("question responses cannot return candidate options")
    elif state == "NEEDS_MORE_INFORMATION":
        if status != "NEEDS_INFORMATION_OR_TEST" or not reasons or not reasons <= {
            "DATA_GAP", "KNOWLEDGE_GAP", "CONFLICTING_DATA",
        } or response["options"]:
            raise AdapterContractError("state/reason/status compatibility violation")
        if "DATA_GAP" in reasons and not response["missing_information"]:
            raise AdapterContractError("DATA_GAP requires explicit missing_information")
    elif state == "STOP_OR_REFER_WITH_REASON":
        if response["options"] or not reasons:
            raise AdapterContractError("state/reason/status compatibility violation")
        if status == "SAFETY_STOP_NO_EXECUTION_SUGGESTION" and reasons != {"SAFETY_CONCERN"}:
            raise AdapterContractError("state/reason/status compatibility violation")
        if status == "OUT_OF_V1_SCOPE" and reasons != {"OUT_OF_SCOPE"}:
            raise AdapterContractError("state/reason/status compatibility violation")
        if status == "NEEDS_INFORMATION_OR_TEST" and reasons != {"NO_VALID_OPTION"}:
            raise AdapterContractError("state/reason/status compatibility violation")
        if status == "NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW" and not reasons <= {
            "SAFETY_CONCERN", "KNOWLEDGE_GAP", "CONFLICTING_DATA", "DATA_GAP",
            "OUT_OF_SCOPE", "STALE_CASE_VERSION",
        }:
            raise AdapterContractError("state/reason/status compatibility violation")
        if status == "SYSTEM_REASONED_SUGGESTION":
            raise AdapterContractError("state/reason/status compatibility violation")




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
