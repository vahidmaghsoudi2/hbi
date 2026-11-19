from app.domain.hair_color_five_response_states import (
    ConsultationResponseState, map_motor_to_response, response_state_labels
)

def test_only_five_response_states():
    assert len(response_state_labels())==5
    assert "conditional_suggestion" not in response_state_labels()

def test_reviewable_motor_maps_to_reviewable_response():
    a=map_motor_to_response("suggestion_reviewable")
    assert a.state==ConsultationResponseState.SUGGESTION_REVIEWABLE_BY_SPECIALIST

def test_request_info_maps_to_info_or_test():
    assert map_motor_to_response("request_more_information").state==ConsultationResponseState.NEEDS_MORE_INFORMATION_OR_TEST

def test_conditional_data_maps_to_information_state():
    assert map_motor_to_response("conditional_suggestion",condition_type="data").state==ConsultationResponseState.NEEDS_MORE_INFORMATION_OR_TEST

def test_conditional_test_maps_to_information_test_state():
    assert map_motor_to_response("conditional_suggestion",condition_type="test").state==ConsultationResponseState.NEEDS_MORE_INFORMATION_OR_TEST

def test_conditional_specialist_condition_maps_to_specialist_review():
    assert map_motor_to_response("conditional_suggestion",condition_type="in_person").state==ConsultationResponseState.NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW

def test_safety_stop_maps_to_safety_response():
    assert map_motor_to_response("stop_or_referral","safety_stop").state==ConsultationResponseState.SAFETY_STOP_NO_EXECUTION_SUGGESTION

def test_scope_stop_maps_to_outside_scope():
    assert map_motor_to_response("stop_or_referral","scope_exclusion").state==ConsultationResponseState.OUTSIDE_FIRST_VERSION_SCOPE

def test_knowledge_gap_maps_to_specialist_review_not_data_gap():
    a=map_motor_to_response("stop_or_referral","knowledge_gap")
    assert a.state==ConsultationResponseState.NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW

def test_engine_fail_maps_to_specialist_review_fail_closed():
    a=map_motor_to_response("stop_or_referral","engine_fail")
    assert a.state==ConsultationResponseState.NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW

def test_invalid_motor_maps_conservatively():
    assert map_motor_to_response("invented").state==ConsultationResponseState.NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW
