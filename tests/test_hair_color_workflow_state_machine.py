import pytest

from app.hair_color.workflow_state_machine import (
    CaseWorkflow,
    WorkflowState,
    WorkflowTransitionError,
    restart_as_fresh_case_after_stop,
    transition,
)


def case(state=WorkflowState.INCOMPLETE_ACCEPTANCE):
    return CaseWorkflow("CASE-SYN-01", 1, 1, state)


def test_workflow_requires_traceable_event_and_current_versions():
    with pytest.raises(WorkflowTransitionError, match="event_id"):
        transition(case(), WorkflowState.AWAITING_EVALUATION, event_id=" ", expected_case_version=1, expected_target_version=1)
    with pytest.raises(WorkflowTransitionError, match="stale"):
        transition(case(), WorkflowState.AWAITING_EVALUATION, event_id="EV-SYN-1", expected_case_version=0, expected_target_version=1)


def test_transition_to_evaluation_is_allowed_and_case_snapshot_is_immutable():
    source = case()
    moved = transition(source, WorkflowState.AWAITING_EVALUATION, event_id="EV-SYN-2", expected_case_version=1, expected_target_version=1)
    assert source.state is WorkflowState.INCOMPLETE_ACCEPTANCE
    assert moved.state is WorkflowState.AWAITING_EVALUATION
    assert moved.last_transition_event == "EV-SYN-2"


def test_client_acceptance_alone_does_not_authorize_execution():
    source = case(WorkflowState.AWAITING_CLIENT_CONFIRMATION)
    with pytest.raises(WorkflowTransitionError, match="separate"):
        transition(source, WorkflowState.APPROVED_FOR_EXECUTION, event_id="EV-SYN-3", expected_case_version=1, expected_target_version=1, client_acceptance=True, execution_consent=False)


def test_execution_approval_requires_both_acceptance_and_explicit_consent():
    source = case(WorkflowState.AWAITING_CLIENT_CONFIRMATION)
    moved = transition(source, WorkflowState.APPROVED_FOR_EXECUTION, event_id="EV-SYN-4", expected_case_version=1, expected_target_version=1, client_acceptance=True, execution_consent=True)
    assert moved.state is WorkflowState.APPROVED_FOR_EXECUTION


def test_safety_stop_has_no_resume_transition():
    stopped = case(WorkflowState.SAFETY_STOPPED)
    with pytest.raises(WorkflowTransitionError, match="not allowed"):
        transition(stopped, WorkflowState.AWAITING_EVALUATION, event_id="EV-SYN-5", expected_case_version=1, expected_target_version=1)


def test_fresh_restart_from_stop_creates_new_case_and_versions():
    stopped = case(WorkflowState.SAFETY_STOPPED)
    fresh = restart_as_fresh_case_after_stop(stopped, new_case_ref="CASE-SYN-02")
    assert fresh.case_ref == "CASE-SYN-02"
    assert (fresh.case_version, fresh.target_version) == (2, 2)
    assert fresh.state is WorkflowState.INCOMPLETE_ACCEPTANCE
    assert stopped.state is WorkflowState.SAFETY_STOPPED


def test_restart_rejected_for_non_stopped_case_and_same_case_reference():
    with pytest.raises(WorkflowTransitionError, match="safety-stopped"):
        restart_as_fresh_case_after_stop(case(), new_case_ref="CASE-SYN-02")
    with pytest.raises(WorkflowTransitionError, match="distinct"):
        restart_as_fresh_case_after_stop(case(WorkflowState.SAFETY_STOPPED), new_case_ref="CASE-SYN-01")


def test_illegal_transition_cannot_skip_specialist_and_client_confirmation_stages():
    with pytest.raises(WorkflowTransitionError, match="not allowed"):
        transition(case(WorkflowState.AWAITING_EVALUATION), WorkflowState.APPROVED_FOR_EXECUTION, event_id="EV-SYN-6", expected_case_version=1, expected_target_version=1, client_acceptance=True, execution_consent=True)
