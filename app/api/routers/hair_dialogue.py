"""Stateless synthetic-only API adapter for the approved Hair dialogue contract.

This endpoint exercises the pure dialogue state machine end-to-end over HTTP.
It never stores cases, creates recommendations, exposes client data, or authorizes
service execution. All state is supplied and returned by the caller.
"""
from __future__ import annotations

from dataclasses import asdict
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.core.authorization import require_any_role
from app.domain.hair_dialogue_contract import (
    ClientDecision,
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
)
from app.models.user_role import ROLE_ADMIN, ROLE_PO, ROLE_REVIEWER_QA

router = APIRouter()


class DialogueStateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

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
    model_config = ConfigDict(extra="forbid")

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
    data_complete: bool | None = None
    safety_passed: bool | None = None
    rule_valid: bool | None = None
    evidence_valid: bool | None = None
    engine_ok: bool = True
    proposal_id: str | None = None
    explicit_consent: bool = False
    new_goal_version: str | None = None
    invalidation_status: str | None = None


def _state_payload(state: DialogueCaseState) -> dict[str, Any]:
    result = asdict(state)
    result["client_decision"] = state.client_decision.value
    result["rejected_proposal_ids"] = list(state.rejected_proposal_ids)
    return result


@router.post("/dialogue/turn")
async def run_hair_dialogue_turn(
    payload: HairDialogueTurnRequest,
    _auth=Depends(require_any_role(ROLE_REVIEWER_QA, ROLE_PO, ROLE_ADMIN)),
):
    """Apply one approved dialogue transition to a synthetic state, without persistence."""
    state = payload.state.to_domain()
    if not isinstance(state.case_id, str) or not state.case_id.startswith("SYNTHETIC-"):
        raise HTTPException(status_code=422, detail="PO-66-09 permits synthetic case identifiers only.")
    if not state.case_version.strip() or not state.goal_version.strip():
        raise HTTPException(status_code=422, detail="Synthetic case and goal versions must be non-empty.")

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
            if None in (payload.data_complete, payload.safety_passed, payload.rule_valid, payload.evidence_valid):
                raise ValueError("All advice gate inputs must be explicit.")
            gate = evaluate_advice_gate(
                data_complete=payload.data_complete,
                safety_passed=payload.safety_passed,
                rule_valid=payload.rule_valid,
                evidence_valid=payload.evidence_valid,
                engine_ok=payload.engine_ok,
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
            reassessment = apply_dependency_reassessment(state, payload.invalidation_status or "")
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
