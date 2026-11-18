"""Synthetic-only logical case, version, dependency, and event contract.

This module is an in-memory contract implementation. It does not create a
database, persist events, connect customer records, expose recommendations,
or authorize service execution. PO-66-09 remains in force: synthetic data only.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal


class KnowledgeState(str, Enum):
    KNOWN = "KNOWN"
    UNKNOWN = "UNKNOWN"
    NOT_ASKED = "NOT_ASKED"
    MISSING = "MISSING"
    CONFLICT = "CONFLICT"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class SourceClass(str, Enum):
    CLIENT_REPORTED = "CLIENT_REPORTED"
    OPERATOR_RECORDED = "OPERATOR_RECORDED"
    SPECIALIST_OBSERVED = "SPECIALIST_OBSERVED"
    PRODUCT_DOCUMENT = "PRODUCT_DOCUMENT"
    INSTRUMENT_MEASURED = "INSTRUMENT_MEASURED"
    SYSTEM_DERIVED = "SYSTEM_DERIVED"


class EventType(str, Enum):
    QUESTION_ASKED = "QUESTION_ASKED"
    SUGGESTION_REJECTED = "SUGGESTION_REJECTED"
    SUGGESTION_ACCEPTED = "SUGGESTION_ACCEPTED"
    EXECUTION_CONSENT_GIVEN = "EXECUTION_CONSENT_GIVEN"
    SPECIALIST_REVIEW_RECORDED = "SPECIALIST_REVIEW_RECORDED"
    CASE_DATA_CHANGED = "CASE_DATA_CHANGED"
    TARGET_CHANGED = "TARGET_CHANGED"
    CLIENT_STOP_REQUESTED = "CLIENT_STOP_REQUESTED"
    WORKFLOW_STATE_CHANGED = "WORKFLOW_STATE_CHANGED"
    PERFORMED_STEP_RECORDED = "PERFORMED_STEP_RECORDED"
    SERVICE_EXECUTION_STARTED = "SERVICE_EXECUTION_STARTED"
    SERVICE_EXECUTION_COMPLETED = "SERVICE_EXECUTION_COMPLETED"
    WORKFLOW_RESTART_AUTHORIZED = "WORKFLOW_RESTART_AUTHORIZED"
    FOLLOW_UP_RECORDED = "FOLLOW_UP_RECORDED"
    CASE_CLOSED = "CASE_CLOSED"


WORKFLOW_STATES = (
    "پذیرش ناقص",
    "در انتظار ارزیابی",
    "در انتظار تست",
    "متوقف ایمنی",
    "آمادهٔ تصمیم متخصص",
    "در انتظار تأیید مشتری",
    "تأییدشده برای اجرا",
    "در حال اجرا",
    "نیازمند پیگیری",
    "بسته‌شده",
)

_SYNTHETIC_PREFIX = "SYNTHETIC-"
@dataclass(frozen=True)
class FactRecord:
    fact_id: str
    field_key: str
    value: object | None
    knowledge_state: KnowledgeState
    source_class: SourceClass
    source_ref: str
    recorded_at: str
    recorded_by: str
    supersedes_fact_id: str | None = None
    conflict_group_ref: str | None = None

    def __post_init__(self) -> None:
        _require_synthetic(self.fact_id, "fact_id")
        _require_text(self.field_key, "field_key")
        _require_text(self.source_ref, "source_ref")
        _require_text(self.recorded_at, "recorded_at")
        _require_synthetic(self.recorded_by, "recorded_by")
        if not isinstance(self.knowledge_state, KnowledgeState):
            raise ValueError("knowledge_state must be a KnowledgeState")
        if not isinstance(self.source_class, SourceClass):
            raise ValueError("source_class must be a SourceClass")
        if self.knowledge_state == KnowledgeState.KNOWN and self.value is None:
            raise ValueError("KNOWN facts require a value; false is a valid known value")
        if self.knowledge_state != KnowledgeState.KNOWN and self.value is not None:
            raise ValueError("Non-KNOWN facts must not carry a value")
        if self.knowledge_state == KnowledgeState.CONFLICT and not self.conflict_group_ref:
            raise ValueError("CONFLICT facts require conflict_group_ref")
        if self.supersedes_fact_id is not None:
            _require_synthetic(self.supersedes_fact_id, "supersedes_fact_id")


@dataclass(frozen=True)
class HairCaseRecord:
    case_id: str
    case_version: str
    target_version: str
    workflow_state: str
    facts: tuple[FactRecord, ...]

    def __post_init__(self) -> None:
        _require_synthetic(self.case_id, "case_id")
        _require_text(self.case_version, "case_version")
        _require_text(self.target_version, "target_version")
        if self.workflow_state not in WORKFLOW_STATES:
            raise ValueError("workflow_state must be one of the ten approved states")
        if not isinstance(self.facts, tuple) or not all(
            isinstance(fact, FactRecord) for fact in self.facts
        ):
            raise ValueError("facts must be a tuple of FactRecord values")
        fact_ids = [fact.fact_id for fact in self.facts]
        if len(fact_ids) != len(set(fact_ids)):
            raise ValueError("fact identifiers must be unique within a case snapshot")


@dataclass(frozen=True)
class DependencyRef:
    kind: str
    dependency_id: str
    version: str

    def __post_init__(self) -> None:
        _require_text(self.kind, "dependency kind")
        _require_text(self.dependency_id, "dependency_id")
        _require_text(self.version, "dependency version")

    @property
    def key(self) -> str:
        return f"{self.kind}:{self.dependency_id}"


@dataclass(frozen=True)
class HairEvaluationRun:
    run_id: str
    request_id: str
    case_id: str
    case_version: str
    target_version: str
    contract_version: str
    engine_version: str
    started_at: str
    completed_at: str
    dependencies: tuple[DependencyRef, ...]
    outcome: Literal["SUCCESS", "ENGINE_FAIL"]
    persistence: Literal["COMPUTED_ONLY"] = "COMPUTED_ONLY"
    display_allowed: bool = False
    recommendation: None = None

    def __post_init__(self) -> None:
        _require_synthetic(self.run_id, "run_id")
        _require_synthetic(self.request_id, "request_id")
        _require_synthetic(self.case_id, "case_id")
        for name in (
            "case_version",
            "target_version",
            "contract_version",
            "engine_version",
            "started_at",
            "completed_at",
        ):
            _require_text(getattr(self, name), name)
        if not isinstance(self.dependencies, tuple) or not all(
            isinstance(item, DependencyRef) for item in self.dependencies
        ):
            raise ValueError("dependencies must be a tuple of DependencyRef values")
        if len({item.key for item in self.dependencies}) != len(self.dependencies):
            raise ValueError("run dependency keys must be unique")
        if self.outcome not in {"SUCCESS", "ENGINE_FAIL"}:
            raise ValueError("outcome must be SUCCESS or ENGINE_FAIL")
        if self.persistence != "COMPUTED_ONLY" or self.display_allowed is not False:
            raise ValueError("runs must remain COMPUTED_ONLY and non-displayable")
        if self.recommendation is not None:
            raise ValueError("this contract does not permit recommendations")


@dataclass(frozen=True)
class SuggestionVersionRef:
    suggestion_id: str
    suggestion_version: str

    def __post_init__(self) -> None:
        _require_synthetic(self.suggestion_id, "suggestion_id")
        _require_text(self.suggestion_version, "suggestion_version")


@dataclass(frozen=True)
class CaseEvent:
    event_id: str
    case_id: str
    case_version: str
    target_version: str
    event_type: EventType
    actor_ref: str
    actor_kind: Literal["CLIENT", "OPERATOR", "SPECIALIST", "SYSTEM"]
    occurred_at: str
    correlation_ref: str
    suggestion: SuggestionVersionRef | None = None
    payload: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        _require_synthetic(self.event_id, "event_id")
        _require_synthetic(self.case_id, "case_id")
        _require_synthetic(self.actor_ref, "actor_ref")
        for name in ("case_version", "target_version", "occurred_at", "correlation_ref"):
            _require_text(getattr(self, name), name)
        if not isinstance(self.event_type, EventType):
            raise ValueError("event_type must be an EventType")
        if self.actor_kind not in {"CLIENT", "OPERATOR", "SPECIALIST", "SYSTEM"}:
            raise ValueError("actor_kind is not an approved actor kind")
        if self.suggestion is not None and not isinstance(
            self.suggestion, SuggestionVersionRef
        ):
            raise ValueError("suggestion must be a SuggestionVersionRef or None")
        if not isinstance(self.payload, tuple) or any(
            not isinstance(pair, tuple)
            or len(pair) != 2
            or not all(isinstance(part, str) and part.strip() for part in pair)
            for pair in self.payload
        ):
            raise ValueError("payload must be a tuple of non-empty string pairs")
        if len({key for key, _ in self.payload}) != len(self.payload):
            raise ValueError("payload keys must be unique")
        if self.event_type in {
            EventType.SUGGESTION_REJECTED,
            EventType.SUGGESTION_ACCEPTED,
            EventType.EXECUTION_CONSENT_GIVEN,
            EventType.SPECIALIST_REVIEW_RECORDED,
            EventType.PERFORMED_STEP_RECORDED,
            EventType.SERVICE_EXECUTION_STARTED,
            EventType.SERVICE_EXECUTION_COMPLETED,
        } and self.suggestion is None:
            raise ValueError("decision, review and execution events require an exact suggestion version")
        allowed_payload_keys = {
            "question_ref", "review_ref", "decision", "reason_code",
            "new_target_version", "from_state", "to_state", "step_ref",
            "service_record_ref", "fresh_evaluation_ref", "authorization_ref",
            "fact_ref", "follow_up_ref", "closure_ref",
        }
        for key, value in self.payload:
            if key not in allowed_payload_keys:
                raise ValueError("event payload contains an unsupported field")
            if key.endswith("_ref"):
                _require_synthetic(value, key)
            elif key == "decision" and value not in {"APPROVED", "REJECTED", "REVISION_REQUIRED"}:
                raise ValueError("specialist decision is not an approved value")
            elif key in {"from_state", "to_state"} and value not in WORKFLOW_STATES:
                raise ValueError("workflow event contains an unknown workflow state")
            elif key == "new_target_version":
                _require_text(value, key)
            elif key == "reason_code" and (
                not value or not value.replace("_", "").isalnum() or value.upper() != value
            ):
                raise ValueError("reason_code must be a controlled uppercase token")


@dataclass(frozen=True)
class WorkflowControl:
    resume_blocked: bool = False
    stop_event_id: str | None = None

    def __post_init__(self) -> None:
        if self.resume_blocked:
            _require_synthetic(self.stop_event_id, "stop_event_id")
        elif self.stop_event_id is not None:
            raise ValueError("an unblocked workflow cannot retain a stop_event_id")


@dataclass(frozen=True)
class EventAppendResult:
    events: tuple[CaseEvent, ...]
    workflow_control: WorkflowControl


@dataclass(frozen=True)
class DependencyAssessment:
    status: Literal["PRESERVE", "INVALIDATE", "UNRESOLVED"]
    changed_dependencies: tuple[str, ...]
    unresolved_dependencies: tuple[str, ...]


def _require_text(value: object, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")


def _require_synthetic(value: object, name: str) -> None:
    if not isinstance(value, str) or not value.startswith(_SYNTHETIC_PREFIX):
        raise ValueError(f"{name} must use a synthetic identifier")


def evaluation_matches_current_case(
    run: HairEvaluationRun, case: HairCaseRecord
) -> bool:
    """A run is current only for the exact case and target version pair."""
    return (
        run.case_id == case.case_id
        and run.case_version == case.case_version
        and run.target_version == case.target_version
        and run.outcome == "SUCCESS"
    )


def assess_dependency_changes(
    previous: tuple[DependencyRef, ...],
    current: tuple[DependencyRef, ...],
    impact_by_key: dict[str, Literal["EFFECTIVE", "NON_EFFECTIVE", "UNKNOWN"]],
) -> DependencyAssessment:
    """Fail closed unless every changed dependency has an explicit impact."""
    if not isinstance(previous, tuple) or not isinstance(current, tuple):
        raise ValueError("dependency snapshots must be tuples")
    old = {item.key: item.version for item in previous}
    new = {item.key: item.version for item in current}
    if len(old) != len(previous) or len(new) != len(current):
        raise ValueError("dependency keys must be unique")
    changed = tuple(sorted(key for key in set(old) | set(new) if old.get(key) != new.get(key)))
    if not changed:
        return DependencyAssessment("PRESERVE", (), ())
    missing_edges = tuple(key for key in changed if key not in old or key not in new)
    invalidating = tuple(key for key in changed if impact_by_key.get(key) == "EFFECTIVE")
    unresolved = tuple(
        key for key in changed
        if key in missing_edges or impact_by_key.get(key) not in {"EFFECTIVE", "NON_EFFECTIVE"}
    )
    if invalidating:
        return DependencyAssessment("INVALIDATE", changed, unresolved)
    if unresolved:
        return DependencyAssessment("UNRESOLVED", changed, unresolved)
    return DependencyAssessment("PRESERVE", changed, ())


def append_case_event(
    existing_events: tuple[CaseEvent, ...],
    event: CaseEvent,
    workflow_control: WorkflowControl = WorkflowControl(),
    *,
    fresh_evaluation: HairEvaluationRun | None = None,
) -> EventAppendResult:
    """Return a new event tuple; never mutates or persists the supplied history."""
    if not isinstance(existing_events, tuple) or not all(
        isinstance(item, CaseEvent) for item in existing_events
    ):
        raise ValueError("existing_events must be a tuple of CaseEvent values")
    if not isinstance(event, CaseEvent):
        raise TypeError("event must be a CaseEvent")
    if not isinstance(workflow_control, WorkflowControl):
        raise TypeError("workflow_control must be a WorkflowControl")
    if fresh_evaluation is not None and not isinstance(fresh_evaluation, HairEvaluationRun):
        raise TypeError("fresh_evaluation must be a HairEvaluationRun or None")
    if event.event_type != EventType.WORKFLOW_RESTART_AUTHORIZED and fresh_evaluation is not None:
        raise ValueError("fresh_evaluation is accepted only for an authorized restart")
    if existing_events and any(item.case_id != event.case_id for item in existing_events):
        raise ValueError("one in-memory event sequence must belong to one synthetic case")
    if event.event_id in {item.event_id for item in existing_events}:
        raise ValueError("duplicate event_id is not allowed")

    if workflow_control.resume_blocked and event.event_type not in {
        EventType.QUESTION_ASKED,
        EventType.CLIENT_STOP_REQUESTED,
        EventType.WORKFLOW_RESTART_AUTHORIZED,
    }:
        raise ValueError("workflow is stopped; a fresh authorized restart is required")

    restart_events = tuple(
        item for item in existing_events
        if item.event_type == EventType.WORKFLOW_RESTART_AUTHORIZED
    )
    latest_restart = restart_events[-1] if restart_events else None
    if (
        latest_restart is not None
        and event.event_type not in {
            EventType.QUESTION_ASKED,
            EventType.WORKFLOW_RESTART_AUTHORIZED,
        }
        and (
            event.case_version != latest_restart.case_version
            or event.target_version != latest_restart.target_version
        )
    ):
        raise ValueError("event version pair changed; a fresh authorized restart is required")

    client_decisions = {
        EventType.SUGGESTION_REJECTED,
        EventType.SUGGESTION_ACCEPTED,
        EventType.EXECUTION_CONSENT_GIVEN,
        EventType.CLIENT_STOP_REQUESTED,
    }
    if event.event_type in client_decisions and event.actor_kind != "CLIENT":
        raise ValueError("client decision and stop events require a CLIENT actor")
    if event.event_type == EventType.SPECIALIST_REVIEW_RECORDED and event.actor_kind != "SPECIALIST":
        raise ValueError("specialist review events require a SPECIALIST actor")
    if event.event_type in {
        EventType.PERFORMED_STEP_RECORDED,
        EventType.SERVICE_EXECUTION_STARTED,
        EventType.SERVICE_EXECUTION_COMPLETED,
    } and event.actor_kind != "SPECIALIST":
        raise ValueError("service execution events require a SPECIALIST actor")
    if event.event_type == EventType.WORKFLOW_RESTART_AUTHORIZED and event.actor_kind not in {"OPERATOR", "SYSTEM"}:
        raise ValueError("restart authorization requires an OPERATOR or SYSTEM actor")

    payload = dict(event.payload)
    if event.event_type == EventType.QUESTION_ASKED and not payload.get("question_ref"):
        raise ValueError("question events require a synthetic question_ref")
    if event.event_type == EventType.SPECIALIST_REVIEW_RECORDED and not (
        payload.get("review_ref") and payload.get("decision")
    ):
        raise ValueError("specialist review requires review_ref and decision")
    if event.event_type == EventType.TARGET_CHANGED and not payload.get("new_target_version"):
        raise ValueError("target changes require new_target_version")
    if event.event_type == EventType.WORKFLOW_STATE_CHANGED and not (
        payload.get("from_state") and payload.get("to_state")
    ):
        raise ValueError("workflow transitions require from_state and to_state")
    if event.event_type == EventType.PERFORMED_STEP_RECORDED and not payload.get("step_ref"):
        raise ValueError("performed steps require a synthetic step_ref")
    if event.event_type in {
        EventType.SERVICE_EXECUTION_STARTED,
        EventType.SERVICE_EXECUTION_COMPLETED,
    } and not payload.get("service_record_ref"):
        raise ValueError("service execution events require a synthetic service_record_ref")
    if event.event_type == EventType.CASE_DATA_CHANGED and not payload.get("fact_ref"):
        raise ValueError("case data changes require a synthetic fact_ref")
    if event.event_type == EventType.FOLLOW_UP_RECORDED and not payload.get("follow_up_ref"):
        raise ValueError("follow-up events require a synthetic follow_up_ref")
    if event.event_type == EventType.CASE_CLOSED and not payload.get("closure_ref"):
        raise ValueError("case closure requires a synthetic closure_ref")
    if event.event_type == EventType.WORKFLOW_STATE_CHANGED and (
        payload["from_state"] not in WORKFLOW_STATES or payload["to_state"] not in WORKFLOW_STATES
    ):
        raise ValueError("workflow transitions must use the ten approved states")

    active_history = (
        existing_events[existing_events.index(latest_restart) + 1:]
        if latest_restart is not None
        else existing_events
    )
    same_suggestion = tuple(
        item for item in active_history
        if item.suggestion == event.suggestion
        and item.case_version == event.case_version
        and item.target_version == event.target_version
    ) if event.suggestion is not None else ()
    rejected = any(item.event_type == EventType.SUGGESTION_REJECTED for item in same_suggestion)
    accepted = any(item.event_type == EventType.SUGGESTION_ACCEPTED for item in same_suggestion)
    specialist_approved = any(
        item.event_type == EventType.SPECIALIST_REVIEW_RECORDED
        and dict(item.payload).get("decision") == "APPROVED"
        for item in same_suggestion
    )
    consented = any(
        item.event_type == EventType.EXECUTION_CONSENT_GIVEN for item in same_suggestion
    )

    if event.event_type == EventType.SUGGESTION_ACCEPTED and rejected:
        raise ValueError("a rejected suggestion version can never be accepted again")
    if event.event_type == EventType.EXECUTION_CONSENT_GIVEN and (rejected or not accepted):
        raise ValueError("execution consent requires prior acceptance of the exact suggestion version")
    execution_started = any(
        item.event_type == EventType.SERVICE_EXECUTION_STARTED
        for item in same_suggestion
    )
    if event.event_type == EventType.SERVICE_EXECUTION_STARTED and not (
        accepted and consented and specialist_approved and not rejected
    ):
        raise ValueError(
            "execution requires specialist approval, client acceptance, and separate explicit consent"
        )
    if event.event_type in {
        EventType.PERFORMED_STEP_RECORDED,
        EventType.SERVICE_EXECUTION_COMPLETED,
    } and not execution_started:
        raise ValueError("performed steps and completion require a prior execution-start event")
    if event.event_type == EventType.WORKFLOW_RESTART_AUTHORIZED:
        if (
            not workflow_control.resume_blocked
            or not payload.get("fresh_evaluation_ref")
            or not payload.get("authorization_ref")
            or fresh_evaluation is None
        ):
            raise ValueError("restart requires a fresh evaluation and explicit workflow authorization")
        if (
            fresh_evaluation.run_id != payload["fresh_evaluation_ref"]
            or fresh_evaluation.case_id != event.case_id
            or fresh_evaluation.case_version != event.case_version
            or fresh_evaluation.target_version != event.target_version
            or fresh_evaluation.outcome != "SUCCESS"
        ):
            raise ValueError("restart evaluation must be successful and match the exact current case/target versions")

    next_control = workflow_control
    if event.event_type == EventType.CLIENT_STOP_REQUESTED:
        next_control = WorkflowControl(resume_blocked=True, stop_event_id=event.event_id)
    elif event.event_type == EventType.WORKFLOW_RESTART_AUTHORIZED:
        next_control = WorkflowControl(resume_blocked=False, stop_event_id=None)

    return EventAppendResult(
        events=existing_events + (event,),
        workflow_control=next_control,
    )


__all__ = [
    "CaseEvent",
    "DependencyAssessment",
    "DependencyRef",
    "EventAppendResult",
    "EventType",
    "FactRecord",
    "HairCaseRecord",
    "HairEvaluationRun",
    "KnowledgeState",
    "SourceClass",
    "SuggestionVersionRef",
    "WORKFLOW_STATES",
    "WorkflowControl",
    "append_case_event",
    "assess_dependency_changes",
    "evaluation_matches_current_case",
]
