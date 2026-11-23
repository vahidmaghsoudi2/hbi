import pytest

from app.hair_color.decision_ledger_contract import (
    ConsultationLedger,
    LedgerContractError,
    SuggestionStatus,
    accept_suggestion,
    add_suggestion,
    change_data,
    change_target,
    fresh_restart,
    grant_execution_consent,
    record_question,
    reject_suggestion,
    request_stop,
)


def base():
    return ConsultationLedger(case_ref="CASE-SYN-LEDGER")


def with_suggestion():
    return add_suggestion(base(), suggestion_ref="SUG-SYN-1", dependent_fields=["history", "goal"])


def test_question_before_decision_is_traceable_but_neutral():
    ledger = with_suggestion()
    questioned = record_question(ledger, event_id="EV-SYN-Q1", question_ref="Q-SYN-1")
    assert questioned.suggestions == ledger.suggestions
    assert questioned.events[-1].event_type == "QUESTION"
    assert questioned.suggestions[0].status is SuggestionStatus.REVIEWABLE


def test_acceptance_is_not_execution_consent():
    accepted = accept_suggestion(with_suggestion(), event_id="EV-SYN-A1", suggestion_ref="SUG-SYN-1")
    assert accepted.suggestions[0].status is SuggestionStatus.ACCEPTED
    assert not any(event.event_type == "EXECUTION_CONSENT" for event in accepted.events)


def test_consent_requires_separate_acceptance_event():
    with pytest.raises(LedgerContractError, match="requires a separately accepted"):
        grant_execution_consent(with_suggestion(), event_id="EV-SYN-C1", suggestion_ref="SUG-SYN-1")
    accepted = accept_suggestion(with_suggestion(), event_id="EV-SYN-A2", suggestion_ref="SUG-SYN-1")
    consented = grant_execution_consent(accepted, event_id="EV-SYN-C2", suggestion_ref="SUG-SYN-1")
    assert consented.suggestions[0].status is SuggestionStatus.EXECUTION_CONSENTED
    assert consented.events[-1].event_type == "EXECUTION_CONSENT"


def test_rejected_suggestion_cannot_be_reactivated_by_acceptance():
    rejected = reject_suggestion(with_suggestion(), event_id="EV-SYN-R1", suggestion_ref="SUG-SYN-1")
    assert rejected.suggestions[0].status is SuggestionStatus.REJECTED
    with pytest.raises(LedgerContractError, match="reviewable"):
        accept_suggestion(rejected, event_id="EV-SYN-A3", suggestion_ref="SUG-SYN-1")


def test_target_change_invalidates_every_prior_suggestion_and_decision():
    accepted = accept_suggestion(with_suggestion(), event_id="EV-SYN-A4", suggestion_ref="SUG-SYN-1")
    changed = change_target(accepted, event_id="EV-SYN-T1")
    assert changed.case_version == 2 and changed.target_version == 2
    assert changed.suggestions[0].status is SuggestionStatus.INVALIDATED
    with pytest.raises(LedgerContractError, match="reviewable"):
        accept_suggestion(changed, event_id="EV-SYN-A5", suggestion_ref="SUG-SYN-1")


def test_data_change_invalidates_only_suggestions_dependent_on_changed_field():
    ledger = add_suggestion(base(), suggestion_ref="SUG-SYN-DEP", dependent_fields=["history"])
    ledger = add_suggestion(ledger, suggestion_ref="SUG-SYN-INDEP", dependent_fields=["goal"])
    changed = change_data(ledger, event_id="EV-SYN-D1", changed_fields=["history"])
    assert changed.case_version == 2
    states = {s.suggestion_ref: s.status for s in changed.suggestions}
    assert states["SUG-SYN-DEP"] is SuggestionStatus.INVALIDATED
    assert states["SUG-SYN-INDEP"] is SuggestionStatus.REVIEWABLE
    independent = next(s for s in changed.suggestions if s.suggestion_ref == "SUG-SYN-INDEP")
    assert independent.evaluated_case_version == 2  # unaffected dependency snapshot retained
    accepted_again = accept_suggestion(changed, event_id="EV-SYN-A7", suggestion_ref="SUG-SYN-INDEP")
    assert accepted_again.suggestions[1].status is SuggestionStatus.ACCEPTED


def test_change_data_requires_fields_and_event_id():
    with pytest.raises(LedgerContractError, match="field names"):
        change_data(with_suggestion(), event_id="EV-SYN-D2", changed_fields=[])


def test_stop_records_only_reported_performed_steps_and_blocks_new_suggestions():
    stopped = request_stop(with_suggestion(), event_id="EV-SYN-STOP1", performed_step_refs=["STEP-SYN-DONE"])
    assert stopped.stopped is True
    assert stopped.performed_step_refs == ("STEP-SYN-DONE",)
    with pytest.raises(LedgerContractError, match="stopped"):
        add_suggestion(stopped, suggestion_ref="SUG-SYN-2", dependent_fields=["goal"])


def test_stopped_case_restart_is_fresh_case_without_carryover():
    stopped = request_stop(with_suggestion(), event_id="EV-SYN-STOP2", performed_step_refs=[])
    restarted = fresh_restart(stopped, new_case_ref="CASE-SYN-NEW", event_id="EV-SYN-RESTART1")
    assert restarted.case_ref == "CASE-SYN-NEW"
    assert restarted.case_version == 2 and restarted.target_version == 2
    assert restarted.suggestions == ()
    assert len(restarted.events) == 1
    assert restarted.events[0].event_type == "FRESH_RESTART_FROM_STOP"
    assert restarted.events[0].details == ("CASE-SYN-LEDGER",)
    assert restarted.stopped is False


def test_restart_cannot_resume_same_case_or_nonstopped_case():
    with pytest.raises(LedgerContractError, match="stopped"):
        fresh_restart(base(), new_case_ref="CASE-SYN-NEW", event_id="EV-SYN-RESTART0")
    stopped = request_stop(base(), event_id="EV-SYN-STOP3", performed_step_refs=[])
    with pytest.raises(LedgerContractError, match="distinct"):
        fresh_restart(stopped, new_case_ref="CASE-SYN-LEDGER", event_id="EV-SYN-RESTART3")


def test_stopped_case_blocks_acceptance_and_consent():
    stopped = request_stop(with_suggestion(), event_id="EV-SYN-STOP4", performed_step_refs=[])
    with pytest.raises(LedgerContractError, match="stopped"):
        accept_suggestion(stopped, event_id="EV-SYN-A6", suggestion_ref="SUG-SYN-1")
    with pytest.raises(LedgerContractError, match="stopped"):
        grant_execution_consent(stopped, event_id="EV-SYN-C3", suggestion_ref="SUG-SYN-1")


def test_restart_requires_traceable_event_id():
    stopped = request_stop(base(), event_id="EV-SYN-STOP5", performed_step_refs=[])
    with pytest.raises(LedgerContractError, match="event_id"):
        fresh_restart(stopped, new_case_ref="CASE-SYN-NEW", event_id=" ")


def test_nonstring_dependency_fields_fail_closed():
    with pytest.raises(LedgerContractError, match="strings"):
        add_suggestion(base(), suggestion_ref="SUG-SYN-BAD", dependent_fields=[17])


def test_nonstring_changed_fields_fail_closed():
    with pytest.raises(LedgerContractError, match="strings"):
        change_data(with_suggestion(), event_id="EV-SYN-D3", changed_fields=[17])


def test_unaffected_acceptance_and_consent_reset_after_case_data_version_changes():
    ledger = add_suggestion(base(), suggestion_ref="SUG-SYN-DECISION", dependent_fields=["unrelated"])
    accepted = accept_suggestion(ledger, event_id="EV-SYN-A8", suggestion_ref="SUG-SYN-DECISION")
    consented = grant_execution_consent(accepted, event_id="EV-SYN-C4", suggestion_ref="SUG-SYN-DECISION")
    changed = change_data(consented, event_id="EV-SYN-D4", changed_fields=["different_field"])
    record = changed.suggestions[0]
    assert record.status is SuggestionStatus.REVIEWABLE
    assert record.evaluated_case_version == changed.case_version
    assert not any(event.event_type == "EXECUTION_CONSENT" and event.case_version == changed.case_version for event in changed.events)
    fresh_acceptance = accept_suggestion(changed, event_id="EV-SYN-A9", suggestion_ref="SUG-SYN-DECISION")
    assert fresh_acceptance.suggestions[0].status is SuggestionStatus.ACCEPTED


def test_rejected_suggestion_stays_rejected_after_unrelated_data_change():
    rejected = reject_suggestion(with_suggestion(), event_id="EV-SYN-R2", suggestion_ref="SUG-SYN-1")
    changed = change_data(rejected, event_id="EV-SYN-D5", changed_fields=["unrelated"])
    assert changed.suggestions[0].status is SuggestionStatus.REJECTED
    with pytest.raises(LedgerContractError, match="reviewable"):
        accept_suggestion(changed, event_id="EV-SYN-A10", suggestion_ref="SUG-SYN-1")


def test_event_ids_must_be_unique_within_case():
    questioned = record_question(base(), event_id="EV-SYN-UNIQUE", question_ref="Q-SYN-UNIQUE")
    with pytest.raises(LedgerContractError, match="event_id must be unique"):
        record_question(questioned, event_id="EV-SYN-UNIQUE", question_ref="Q-SYN-DUP")
