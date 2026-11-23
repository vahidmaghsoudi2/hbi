"""In-memory, synthetic consultation decision ledger contract.

This is a software contract fixture, not persistence or a real consultation.
Events track decisions; they do not execute services or provide domain advice.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable


class SuggestionStatus(str, Enum):
    REVIEWABLE = "REVIEWABLE"
    REJECTED = "REJECTED"
    ACCEPTED = "ACCEPTED"
    EXECUTION_CONSENTED = "EXECUTION_CONSENTED"
    INVALIDATED = "INVALIDATED"


@dataclass(frozen=True)
class SuggestionRecord:
    suggestion_ref: str
    evaluated_case_version: int
    evaluated_target_version: int
    dependent_fields: tuple[str, ...]
    status: SuggestionStatus = SuggestionStatus.REVIEWABLE


@dataclass(frozen=True)
class DecisionEvent:
    event_id: str
    event_type: str
    suggestion_ref: str | None
    case_version: int
    target_version: int
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ConsultationLedger:
    case_ref: str
    case_version: int = 1
    target_version: int = 1
    suggestions: tuple[SuggestionRecord, ...] = ()
    events: tuple[DecisionEvent, ...] = ()
    stopped: bool = False
    performed_step_refs: tuple[str, ...] = ()


class LedgerContractError(ValueError):
    """Raised when a decision event violates ledger invariants."""


def add_suggestion(
    ledger: ConsultationLedger,
    *,
    suggestion_ref: str,
    dependent_fields: Iterable[str],
) -> ConsultationLedger:
    if ledger.stopped:
        raise LedgerContractError("stopped case cannot accept suggestions")
    if not isinstance(suggestion_ref, str) or not suggestion_ref.strip():
        raise LedgerContractError("suggestion_ref must be unique and non-empty")
    if any(s.suggestion_ref == suggestion_ref for s in ledger.suggestions):
        raise LedgerContractError("suggestion_ref must be unique and non-empty")
    fields = tuple(dependent_fields)
    if any(not isinstance(field, str) for field in fields):
        raise LedgerContractError("dependent field names must be strings")
    deps = tuple(sorted({field for field in fields if field.strip()}))
    record = SuggestionRecord(suggestion_ref, ledger.case_version, ledger.target_version, deps)
    return replace(ledger, suggestions=ledger.suggestions + (record,))


def record_question(ledger: ConsultationLedger, *, event_id: str, question_ref: str) -> ConsultationLedger:
    if not isinstance(event_id, str) or not event_id.strip() or not isinstance(question_ref, str) or not question_ref.strip():
        raise LedgerContractError("question event requires event_id and question_ref")
    _ensure_unique_event_id(ledger, event_id)
    event = DecisionEvent(event_id, "QUESTION", None, ledger.case_version, ledger.target_version, (question_ref,))
    return replace(ledger, events=ledger.events + (event,))


def _ensure_unique_event_id(ledger: ConsultationLedger, event_id: str) -> None:
    if any(event.event_id == event_id for event in ledger.events):
        raise LedgerContractError("event_id must be unique within a case")


def _get_suggestion(ledger: ConsultationLedger, suggestion_ref: str) -> SuggestionRecord:
    for record in ledger.suggestions:
        if record.suggestion_ref == suggestion_ref:
            return record
    raise LedgerContractError("unknown suggestion_ref")


def _replace_suggestion(ledger: ConsultationLedger, changed: SuggestionRecord) -> ConsultationLedger:
    records = tuple(changed if item.suggestion_ref == changed.suggestion_ref else item for item in ledger.suggestions)
    return replace(ledger, suggestions=records)


def reject_suggestion(ledger: ConsultationLedger, *, event_id: str, suggestion_ref: str) -> ConsultationLedger:
    record = _get_suggestion(ledger, suggestion_ref)
    if ledger.stopped:
        raise LedgerContractError("stopped case cannot accept decision events")
    if not isinstance(event_id, str) or not event_id.strip() or record.status is not SuggestionStatus.REVIEWABLE:
        raise LedgerContractError("only a current reviewable suggestion can be rejected")
    _ensure_unique_event_id(ledger, event_id)
    updated = _replace_suggestion(ledger, replace(record, status=SuggestionStatus.REJECTED))
    event = DecisionEvent(event_id, "REJECT", suggestion_ref, ledger.case_version, ledger.target_version)
    return replace(updated, events=updated.events + (event,))


def accept_suggestion(ledger: ConsultationLedger, *, event_id: str, suggestion_ref: str) -> ConsultationLedger:
    record = _get_suggestion(ledger, suggestion_ref)
    if ledger.stopped:
        raise LedgerContractError("stopped case cannot accept decision events")
    if not isinstance(event_id, str) or not event_id.strip() or record.status is not SuggestionStatus.REVIEWABLE:
        raise LedgerContractError("only a current reviewable suggestion can be accepted")
    if (record.evaluated_case_version, record.evaluated_target_version) != (ledger.case_version, ledger.target_version):
        raise LedgerContractError("stale suggestion; fresh evaluation required")
    _ensure_unique_event_id(ledger, event_id)
    updated = _replace_suggestion(ledger, replace(record, status=SuggestionStatus.ACCEPTED))
    event = DecisionEvent(event_id, "ACCEPT", suggestion_ref, ledger.case_version, ledger.target_version)
    return replace(updated, events=updated.events + (event,))


def grant_execution_consent(
    ledger: ConsultationLedger, *, event_id: str, suggestion_ref: str
) -> ConsultationLedger:
    record = _get_suggestion(ledger, suggestion_ref)
    if ledger.stopped:
        raise LedgerContractError("stopped case cannot accept decision events")
    if not isinstance(event_id, str) or not event_id.strip() or record.status is not SuggestionStatus.ACCEPTED:
        raise LedgerContractError("execution consent requires a separately accepted suggestion")
    if (record.evaluated_case_version, record.evaluated_target_version) != (ledger.case_version, ledger.target_version):
        raise LedgerContractError("stale suggestion; fresh evaluation required")
    _ensure_unique_event_id(ledger, event_id)
    updated = _replace_suggestion(ledger, replace(record, status=SuggestionStatus.EXECUTION_CONSENTED))
    event = DecisionEvent(event_id, "EXECUTION_CONSENT", suggestion_ref, ledger.case_version, ledger.target_version)
    return replace(updated, events=updated.events + (event,))


def change_target(ledger: ConsultationLedger, *, event_id: str) -> ConsultationLedger:
    if not isinstance(event_id, str) or not event_id.strip() or ledger.stopped:
        raise LedgerContractError("target change requires an active case and event ID")
    _ensure_unique_event_id(ledger, event_id)
    next_case, next_target = ledger.case_version + 1, ledger.target_version + 1
    records = tuple(replace(item, status=SuggestionStatus.INVALIDATED) for item in ledger.suggestions)
    event = DecisionEvent(event_id, "TARGET_CHANGED", None, next_case, next_target)
    return replace(ledger, case_version=next_case, target_version=next_target, suggestions=records, events=ledger.events + (event,))


def change_data(ledger: ConsultationLedger, *, event_id: str, changed_fields: Iterable[str]) -> ConsultationLedger:
    supplied_fields = tuple(changed_fields)
    if any(not isinstance(field, str) for field in supplied_fields):
        raise LedgerContractError("changed field names must be strings")
    fields = tuple(sorted({field for field in supplied_fields if field.strip()}))
    if not isinstance(event_id, str) or not event_id.strip() or not fields or ledger.stopped:
        raise LedgerContractError("data change requires active case, event ID, and field names")
    _ensure_unique_event_id(ledger, event_id)
    next_case = ledger.case_version + 1
    changed = set(fields)
    records = tuple(
        replace(item, evaluated_case_version=next_case, status=SuggestionStatus.INVALIDATED)
        if changed.intersection(item.dependent_fields)
        else replace(item, evaluated_case_version=next_case, status=SuggestionStatus.REVIEWABLE)
        if item.status in {SuggestionStatus.REVIEWABLE, SuggestionStatus.ACCEPTED, SuggestionStatus.EXECUTION_CONSENTED}
        else item
        for item in ledger.suggestions
    )
    event = DecisionEvent(event_id, "DATA_CHANGED", None, next_case, ledger.target_version, fields)
    return replace(ledger, case_version=next_case, suggestions=records, events=ledger.events + (event,))


def request_stop(ledger: ConsultationLedger, *, event_id: str, performed_step_refs: Iterable[str]) -> ConsultationLedger:
    if not isinstance(event_id, str) or not event_id.strip() or ledger.stopped:
        raise LedgerContractError("stop event requires active case and event ID")
    _ensure_unique_event_id(ledger, event_id)
    refs = tuple(performed_step_refs)
    if any(not isinstance(ref, str) for ref in refs):
        raise LedgerContractError("performed step references must be strings")
    performed = tuple(dict.fromkeys(ref for ref in refs if ref.strip()))
    event = DecisionEvent(event_id, "STOP_REQUESTED", None, ledger.case_version, ledger.target_version, performed)
    return replace(ledger, stopped=True, performed_step_refs=performed, events=ledger.events + (event,))


def fresh_restart(ledger: ConsultationLedger, *, new_case_ref: str, event_id: str) -> ConsultationLedger:
    if not ledger.stopped:
        raise LedgerContractError("restart requires a stopped source case")
    if not isinstance(event_id, str) or not event_id.strip():
        raise LedgerContractError("restart requires traceable event_id")
    if not isinstance(new_case_ref, str) or not new_case_ref.strip() or new_case_ref == ledger.case_ref:
        raise LedgerContractError("restart must use a distinct case reference")
    _ensure_unique_event_id(ledger, event_id)
    next_case, next_target = ledger.case_version + 1, ledger.target_version + 1
    event = DecisionEvent(event_id, "FRESH_RESTART_FROM_STOP", None, next_case, next_target, (ledger.case_ref,))
    return ConsultationLedger(
        case_ref=new_case_ref,
        case_version=next_case,
        target_version=next_target,
        events=(event,),
    )
