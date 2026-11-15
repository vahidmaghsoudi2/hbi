"""Stateless synthetic-only API adapter for the approved Hair dialogue contract.

This endpoint exercises the pure dialogue state machine end-to-end over HTTP.
It never stores cases, creates recommendations, exposes client data, or authorizes
service execution. All state is supplied and returned by the caller.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.authorization import get_roles_for_subject
from app.core.deps import get_current_customer_id, get_db
from app.domain.hair_dialogue_contract import (
    ClientDecision,
    EngineReadiness,
    DialogueCaseState,
    accept_proposal,
    answer_question,
    apply_dependency_reassessment,
    attach_proposal,
    change_goal,
    evaluate_advice_gate,
    explain_reason,
    record_execution_consent,
    reject_proposal,
    resolve_required_data,
    validate_dialogue_state,
    validate_proposal_id,
)
from app.models.user_role import ROLE_ADMIN, ROLE_PO, ROLE_REVIEWER_QA

router = APIRouter()


class DialogueStateInput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    case_id: str
    case_version: str
    goal_version: str
    active_proposal_id: str | None = None
    active_proposal_case_version: str | None = None
    active_proposal_goal_version: str | None = None
    rejected_proposal_ids: list[str] = Field(default_factory=list)
    client_decision: Literal["NONE", "ACCEPTED", "REJECTED"] = "NONE"
    execution_consent_for_proposal_id: str | None = None

    def to_domain(self) -> DialogueCaseState:
        return DialogueCaseState(
            case_id=self.case_id,
            case_version=self.case_version,
            goal_version=self.goal_version,
            active_proposal_id=self.active_proposal_id,
            active_proposal_case_version=self.active_proposal_case_version,
            active_proposal_goal_version=self.active_proposal_goal_version,
            rejected_proposal_ids=tuple(self.rejected_proposal_ids),
            client_decision=ClientDecision(self.client_decision),
            execution_consent_for_proposal_id=self.execution_consent_for_proposal_id,
        )


class HairDialogueTurnRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    action: Literal[
        "ANSWER_QUESTION",
        "EXPLAIN_REASON",
        "RESOLVE_REQUIRED_DATA",
        "EVALUATE_ADVICE_GATE",
        "ATTACH_PROPOSAL",
        "ACCEPT_PROPOSAL",
        "REJECT_PROPOSAL",
        "RECORD_EXECUTION_CONSENT",
        "CHANGE_GOAL",
        "REASSESS_DEPENDENCIES",
    ]
    state: DialogueStateInput
    question_code: Literal["STATUS_REASON", "MISSING_DATA", "PROCESS_LIMIT"] | None = None
    answer_code: Literal["STATUS_REASON", "MISSING_DATA", "PROCESS_LIMIT"] | None = None
    reason_code: Literal["CATALOG_ONLY", "DATA_GAP", "KNOWLEDGE_GAP", "SAFETY_STOP"] | None = None
    recorded_fields: list[str] | None = None
    required_fields: list[str] | None = None
    proposal_id: str | None = None
    explicit_consent: bool = False
    new_goal_version: str | None = None
    # PRESERVE is intentionally excluded at the HTTP boundary: callers cannot prove dependencies are unchanged.
    invalidation_status: Literal["INVALIDATE", "UNRESOLVED"] | None = None

    @model_validator(mode="after")
    def reject_action_irrelevant_fields(self):
        """Reject cross-action fields instead of silently ignoring caller intent."""
        allowed_fields = {
            "ANSWER_QUESTION": {"question_code", "answer_code"},
            "EXPLAIN_REASON": {"reason_code"},
            "RESOLVE_REQUIRED_DATA": {"recorded_fields", "required_fields"},
            "EVALUATE_ADVICE_GATE": set(),
            "ATTACH_PROPOSAL": {"proposal_id"},
            "ACCEPT_PROPOSAL": {"proposal_id"},
            "REJECT_PROPOSAL": {"proposal_id"},
            "RECORD_EXECUTION_CONSENT": {"proposal_id", "explicit_consent"},
            "CHANGE_GOAL": {"new_goal_version"},
            "REASSESS_DEPENDENCIES": {"invalidation_status"},
        }
        supplied = self.model_fields_set - {"action", "state"}
        irrelevant = supplied - allowed_fields[self.action]
        if irrelevant:
            names = ", ".join(sorted(irrelevant))
            raise ValueError(f"Fields not valid for {self.action}: {names}")
        return self


@dataclass(frozen=True)
class AdviceGateInputs:
    """Trusted server-side gate facts; never populated from an HTTP request."""

    data_complete: bool
    safety_passed: bool
    rule_valid: bool
    evidence_valid: bool
    engine_readiness: EngineReadiness


def get_hair_dialogue_advice_gate_inputs() -> AdviceGateInputs:
    """Fail closed until independently implemented server-side evaluators exist."""
    return AdviceGateInputs(
        data_complete=False,
        safety_passed=False,
        rule_valid=False,
        evidence_valid=False,
        engine_readiness=EngineReadiness.UNAVAILABLE,
    )


def _state_payload(state: DialogueCaseState) -> dict[str, Any]:
    result = asdict(state)
    result["client_decision"] = state.client_decision.value
    result["rejected_proposal_ids"] = list(state.rejected_proposal_ids)
    return result


async def require_hair_dialogue_internal_role(
    subject_id=Depends(get_current_customer_id),
    db=Depends(get_db),
):
    """Require a canonical authenticated actor and an exact internal role."""
    if (
        not isinstance(subject_id, str)
        or not subject_id
        or subject_id != subject_id.strip()
    ):
        raise HTTPException(
            status_code=401,
            detail="A non-empty canonical authenticated actor is required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        roles = get_roles_for_subject(db, subject_id)
    except Exception as exc:
        # Authorization must fail closed without exposing database diagnostics.
        raise HTTPException(
            status_code=503,
            detail="Internal authorization service is temporarily unavailable",
        ) from exc
    allowed_roles = {ROLE_REVIEWER_QA, ROLE_PO, ROLE_ADMIN}
    if not roles.intersection(allowed_roles):
        raise HTTPException(
            status_code=403,
            detail="Hair dialogue runtime requires an authorized internal role",
        )
    return subject_id, roles


@router.post("/dialogue/turn")
async def run_hair_dialogue_turn(
    payload: HairDialogueTurnRequest,
    _auth=Depends(require_hair_dialogue_internal_role),
):
    """Apply one approved dialogue transition to a synthetic state, without persistence."""
    try:
        state = payload.state.to_domain()
        # Validate every caller-supplied state reference before any action can echo it.
        validate_dialogue_state(state)
        if payload.proposal_id is not None:
            validate_proposal_id(payload.proposal_id)
        if payload.action in {
            "ATTACH_PROPOSAL",
            "ACCEPT_PROPOSAL",
            "REJECT_PROPOSAL",
            "RECORD_EXECUTION_CONSENT",
        }:
            validate_proposal_id(payload.proposal_id)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    try:
        result: Any = None
        next_state = state
        action = payload.action

        if action == "ANSWER_QUESTION":
            question_text = {
                "STATUS_REASON": "وضعیت این پرونده چیست؟",
                "MISSING_DATA": "چه داده‌ای هنوز موجود نیست؟",
                "PROCESS_LIMIT": "محدودیت این مسیر چیست؟",
            }.get(payload.question_code or "", "")
            answer_text = {
                "STATUS_REASON": "این پاسخ فقط وضعیت اجرای مصنوعی را توضیح می‌دهد.",
                "MISSING_DATA": "فیلدهای مفقود فقط به‌صورت نام فیلد گزارش می‌شوند.",
                "PROCESS_LIMIT": "این مسیر پیشنهاد شیمیایی یا مجوز اجرای خدمت تولید نمی‌کند.",
            }.get(payload.answer_code or "", "")
            reply = answer_question(state, question=question_text, answer=answer_text)
            result = {"answer": reply.answer, "decision_changed": reply.decision_changed}
        elif action == "EXPLAIN_REASON":
            reason_text = {
                "CATALOG_ONLY": "این خروجی فقط زمینهٔ هویت کاتالوگی مصنوعی را پوشش می‌دهد.",
                "DATA_GAP": "دادهٔ ضروری کافی نیست؛ نتیجهٔ قطعی ارائه نمی‌شود.",
                "KNOWLEDGE_GAP": "شاهد یا قاعدهٔ معتبر کافی نیست؛ حدس زده نمی‌شود.",
                "SAFETY_STOP": "شرط ایمنی تأیید نشده است؛ مسیر متوقف می‌ماند.",
            }.get(payload.reason_code or "", "")
            result = {"summary_fa": explain_reason(reason_text)}
        elif action == "RESOLVE_REQUIRED_DATA":
            fields = payload.recorded_fields or []
            if any(
                not isinstance(field, str)
                or not field.strip()
                or field != field.strip()
                for field in fields
            ):
                raise ValueError(
                    "recorded_fields must contain non-empty, unpadded field names"
                )
            if len(set(fields)) != len(fields):
                raise ValueError("recorded_fields must not contain duplicates")
            # The HTTP contract accepts field-presence markers only, never client values.
            synthetic_presence = {field: "SYNTHETIC_FIXTURE_VALUE" for field in fields}
            resolved = resolve_required_data(synthetic_presence, tuple(payload.required_fields or ()))
            result = {
                "known_fields": [field for field, _value in resolved.known_values],
                "missing_fields": list(resolved.missing_fields),
                "complete": resolved.complete,
            }
        elif action == "EVALUATE_ADVICE_GATE":
            inputs = get_hair_dialogue_advice_gate_inputs()
            if (
                not isinstance(inputs, AdviceGateInputs)
                or any(type(value) is not bool for value in (
                    inputs.data_complete, inputs.safety_passed,
                    inputs.rule_valid, inputs.evidence_valid,
                ))
                or not isinstance(inputs.engine_readiness, EngineReadiness)
            ):
                inputs = AdviceGateInputs(False, False, False, False, EngineReadiness.UNAVAILABLE)
            gate = evaluate_advice_gate(
                data_complete=inputs.data_complete,
                safety_passed=inputs.safety_passed,
                rule_valid=inputs.rule_valid,
                evidence_valid=inputs.evidence_valid,
                engine_readiness=inputs.engine_readiness,
            )
            result = {"advice_allowed": gate.advice_allowed, "reason_codes": list(gate.reason_codes)}
        elif action == "ATTACH_PROPOSAL":
            next_state = attach_proposal(state, payload.proposal_id or "")
        elif action == "ACCEPT_PROPOSAL":
            next_state = accept_proposal(state, payload.proposal_id or "")
        elif action == "REJECT_PROPOSAL":
            next_state = reject_proposal(state, payload.proposal_id or "")
        elif action == "RECORD_EXECUTION_CONSENT":
            next_state = record_execution_consent(
                state, payload.proposal_id or "", explicit_consent=payload.explicit_consent
            )
        elif action == "CHANGE_GOAL":
            next_state = change_goal(state, payload.new_goal_version or "")
        elif action == "REASSESS_DEPENDENCIES":
            if payload.invalidation_status is None:
                raise ValueError("A dependency reassessment outcome is required.")
            reassessment = apply_dependency_reassessment(
                state, payload.invalidation_status
            )
            next_state = reassessment.state
            result = {"status": reassessment.status}
        if result is None:
            result = {"status": "STATE_UPDATED"}

    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return {
        "action": payload.action,
        "state": _state_payload(next_state),
        "result": result,
        "recommendation": None,
        "display_allowed": False,
        "client_visible": False,
        "persistence": "COMPUTED_ONLY",
    }
