from app.domain.hair_color_dialogue_scenarios import dialogue_scenarios, simple_reason
from app.domain.hair_color_predecision_questions import handle_predecision_question
from app.domain.hair_color_gap_handling import make_gap, handle_gaps
from app.domain.hair_color_version_invalidation import invalidate_for_change
from app.domain.hair_color_rejected_suggestion_control import make_alternative, reject_and_select_alternatives
from app.domain.hair_color_acceptance_execution_consent import new_decision_record, record_acceptance, record_execution_consent, evaluate_execution_gate

def test_ten_dialogue_scenarios_are_contracts_not_states():
    scenarios=dialogue_scenarios()
    assert len(scenarios)==10
    assert len({s.scenario_id for s in scenarios})==10

def test_d01_sequential_questions_preserve_state_version_and_suggestion():
    a=handle_predecision_question("q1","why?","awaiting_client_confirmation","s1","v1",("e1",))
    b=handle_predecision_question("q2","what does it mean?","awaiting_client_confirmation","s1","v1",("e1",))
    assert all((x.case_state_unchanged,x.suggestion_id_unchanged,x.case_version_unchanged) for x in (a,b))

def test_d02_reason_explanation_is_plain_language():
    text=simple_reason("engine_fail")
    assert "در بررسی داخلی" in text
    assert "traceback" not in text.lower() and "exception" not in text.lower()

def test_d03_use_evidence_or_disclose_gap():
    a=handle_predecision_question("q1","what?","state","s1","v1",("source-1",))
    b=handle_predecision_question("q2","what?","state","s1","v1",())
    assert a.answer_status=="answer_from_recorded_evidence"
    assert b.answer_status=="evidence_gap"

def test_d04_missing_required_data_blocks_definitive_advice():
    g=make_gap("d1","data_gap","claim","required data absent","regional state")
    a=handle_gaps([g])
    assert a.status=="data_gap" and a.output_policy=="request_missing_inputs"

def test_d05_target_change_fresh_version_and_full_invalidation():
    a=invalidate_for_change("v1","v2",["target_color"])
    assert a.fresh_evaluation_required and a.status=="target_changed_full_invalidation"

def test_d06_rejected_suggestion_not_active_again():
    a=reject_and_select_alternatives("s1","key1",[make_alternative("s1","key1",True,1,("e1",)),make_alternative("s2","key2",True,2,("e2",))])
    assert [x.suggestion_id for x in a.alternatives]==["s2"]

def test_d07_acceptance_not_execution_consent():
    r=record_acceptance(new_decision_record("v1","s1"),"accepted","v1","s1").record
    assert not evaluate_execution_gate(r,True,True,False).authorized
    r=record_execution_consent(r,"granted","v1","s1").record
    assert evaluate_execution_gate(r,True,True,False).authorized

def test_d08_question_not_decision():
    a=handle_predecision_question("q1","should I do it?","awaiting_client_confirmation","s1","v1",("e1",))
    assert a.decision_event is None

def test_d09_absent_evidence_is_explicit():
    a=handle_predecision_question("q1","tell me the exact answer","state","s1","v1",())
    assert a.answer_status=="evidence_gap"
    assert "unavailable" in a.message

def test_d10_changed_data_invalidates_dependents_only():
    a=invalidate_for_change("v1","v2",["current_base"])
    assert "candidate_options" in a.invalidated_outputs
    assert "service_history_assessment" in a.preserved_outputs
