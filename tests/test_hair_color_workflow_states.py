from app.domain.hair_color_workflow_states import (
    CaseWorkflowState as S, TransitionFacts, allowed_workflow_transitions, transition_case
)

def test_exactly_ten_workflow_states():
    assert len(S)==10

def test_intake_to_evaluation_requires_complete_intake():
    assert not transition_case(S.INCOMPLETE_ACCEPTANCE,S.AWAITING_EVALUATION,TransitionFacts()).allowed
    assert transition_case(S.INCOMPLETE_ACCEPTANCE,S.AWAITING_EVALUATION,TransitionFacts(intake_complete=True)).allowed

def test_evaluation_to_test_requires_test_flag():
    assert transition_case(S.AWAITING_EVALUATION,S.AWAITING_TEST,TransitionFacts(test_required=True)).allowed

def test_evaluation_ready_requires_evidence_and_no_test_or_stop():
    assert transition_case(S.AWAITING_EVALUATION,S.READY_FOR_SPECIALIST_DECISION,TransitionFacts(evaluation_complete=True,evidence_ready=True)).allowed
    assert not transition_case(S.AWAITING_EVALUATION,S.READY_FOR_SPECIALIST_DECISION,TransitionFacts(evaluation_complete=True,evidence_ready=True,safety_stop=True)).allowed

def test_safety_stop_transition_requires_recorded_stop():
    assert not transition_case(S.AWAITING_EVALUATION,S.SAFETY_STOPPED,TransitionFacts()).allowed
    assert transition_case(S.AWAITING_EVALUATION,S.SAFETY_STOPPED,TransitionFacts(safety_stop=True)).allowed

def test_awaiting_client_confirmation_requires_specialist_approval():
    assert not transition_case(S.READY_FOR_SPECIALIST_DECISION,S.AWAITING_CLIENT_CONFIRMATION,TransitionFacts()).allowed
    assert transition_case(S.READY_FOR_SPECIALIST_DECISION,S.AWAITING_CLIENT_CONFIRMATION,TransitionFacts(specialist_approved=True)).allowed

def test_execution_approval_requires_separate_consent():
    facts=TransitionFacts(specialist_approved=True,client_acceptance=True)
    assert not transition_case(S.AWAITING_CLIENT_CONFIRMATION,S.APPROVED_FOR_EXECUTION,facts).allowed
    facts=TransitionFacts(specialist_approved=True,client_acceptance=True,execution_consent=True)
    assert transition_case(S.AWAITING_CLIENT_CONFIRMATION,S.APPROVED_FOR_EXECUTION,facts).allowed

def test_execution_start_requires_authorization():
    assert not transition_case(S.APPROVED_FOR_EXECUTION,S.IN_EXECUTION,TransitionFacts()).allowed
    assert transition_case(S.APPROVED_FOR_EXECUTION,S.IN_EXECUTION,TransitionFacts(execution_authorized=True)).allowed

def test_safety_stop_restart_requires_fresh_evaluation_and_authorization():
    assert not transition_case(S.SAFETY_STOPPED,S.AWAITING_EVALUATION,TransitionFacts()).allowed
    assert transition_case(S.SAFETY_STOPPED,S.AWAITING_EVALUATION,TransitionFacts(fresh_evaluation=True,restart_authorized=True)).allowed

def test_test_completion_and_fresh_evaluation_required():
    assert not transition_case(S.AWAITING_TEST,S.AWAITING_EVALUATION,TransitionFacts(test_completed=True)).allowed
    assert transition_case(S.AWAITING_TEST,S.AWAITING_EVALUATION,TransitionFacts(test_completed=True,fresh_evaluation=True)).allowed

def test_closed_is_terminal():
    assert allowed_workflow_transitions()[S.CLOSED]==()
    assert not transition_case(S.CLOSED,S.AWAITING_EVALUATION,TransitionFacts(fresh_evaluation=True)).allowed

def test_follow_up_requires_flag_and_restart_evaluation():
    assert not transition_case(S.IN_EXECUTION,S.NEEDS_FOLLOW_UP,TransitionFacts()).allowed
    assert transition_case(S.IN_EXECUTION,S.NEEDS_FOLLOW_UP,TransitionFacts(followup_needed=True)).allowed
    assert transition_case(S.NEEDS_FOLLOW_UP,S.AWAITING_EVALUATION,TransitionFacts(fresh_evaluation=True)).allowed

def test_invalid_state_or_facts_fail_closed():
    assert not transition_case("unknown",S.CLOSED,TransitionFacts()).allowed
    assert not transition_case(S.INCOMPLETE_ACCEPTANCE,S.AWAITING_EVALUATION,None).allowed
