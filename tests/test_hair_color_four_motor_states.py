from app.domain.hair_color_four_motor_states import DecisionSignals, MotorState, decide_motor_state

def test_four_states_are_only_motor_states():
    assert {s.value for s in MotorState} == {
        "suggestion_reviewable","conditional_suggestion","request_more_information","stop_or_referral"
    }

def test_valid_candidate_reviewable():
    a=decide_motor_state(DecisionSignals(valid_candidate=True))
    assert a.state==MotorState.SUGGESTION_REVIEWABLE

def test_pending_condition_is_conditional():
    a=decide_motor_state(DecisionSignals(valid_candidate=True,condition_pending=True))
    assert a.state==MotorState.CONDITIONAL_SUGGESTION

def test_data_gap_requests_information():
    a=decide_motor_state(DecisionSignals(data_gap=True,valid_candidate=True))
    assert a.state==MotorState.REQUEST_MORE_INFORMATION

def test_knowledge_gap_stops_instead_of_requesting_customer_data():
    a=decide_motor_state(DecisionSignals(knowledge_gap=True,valid_candidate=True))
    assert a.state==MotorState.STOP_OR_REFERRAL
    assert a.reason_code=="knowledge_gap"

def test_safety_stop_has_precedence_over_data_gap():
    a=decide_motor_state(DecisionSignals(safety_stop=True,data_gap=True))
    assert a.reason_code=="safety_stop"

def test_engine_failure_has_highest_precedence():
    a=decide_motor_state(DecisionSignals(engine_fail=True,safety_stop=True))
    assert a.reason_code=="engine_fail"

def test_scope_exclusion_stops():
    assert decide_motor_state(DecisionSignals(scope_exclusion=True)).state==MotorState.STOP_OR_REFERRAL

def test_no_valid_candidate_stops_without_inventing():
    a=decide_motor_state(DecisionSignals())
    assert a.reason_code=="no_valid_candidate"

def test_invalid_input_fail_closed():
    assert decide_motor_state(None).state==MotorState.STOP_OR_REFERRAL

def test_suggestion_reviewable_is_not_consent():
    a=decide_motor_state(DecisionSignals(valid_candidate=True))
    assert "not client acceptance" in a.message
