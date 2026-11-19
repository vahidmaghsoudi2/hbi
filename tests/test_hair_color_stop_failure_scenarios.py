from app.domain.hair_color_stop_failure_scenarios import stop_failure_scenarios
from app.domain.hair_color_four_motor_states import DecisionSignals, decide_motor_state, MotorState
from app.domain.hair_color_gap_handling import make_gap, handle_gaps
from app.domain.hair_color_stop_restart import record_stop_request, assess_restart_after_stop
from app.domain.hair_color_workflow_states import CaseWorkflowState as W, TransitionFacts, transition_case
from app.domain.hair_color_five_response_states import map_motor_to_response, ConsultationResponseState
from app.domain.hair_color_invalid_option_bundle import validate_option_bundle
from app.domain.hair_color_option_selection import make_evaluated_option

def c():
    return make_evaluated_option("o1","بژ",1,"validated",("e1",),"goal-fit")

def test_scenario_catalog_has_ten_unique_cases():
    a=stop_failure_scenarios()
    assert len(a)==10 and len({x.scenario_id for x in a})==10

def test_sf01_safety_stop_motor_state_and_response():
    d=decide_motor_state(DecisionSignals(safety_stop=True))
    assert d.state==MotorState.STOP_OR_REFERRAL
    assert map_motor_to_response(d.state,"safety_stop").state==ConsultationResponseState.SAFETY_STOP_NO_EXECUTION_SUGGESTION

def test_sf02_engine_failure_suppresses_run():
    g=handle_gaps([make_gap("e","engine_fail","run","internal error")])
    assert g.output_policy=="suppress_run_output"

def test_sf03_data_gap_requests_specific_input():
    g=handle_gaps([make_gap("d","data_gap","claim","missing","regional map")])
    assert g.status=="data_gap" and g.request_inputs==("regional map",)

def test_sf04_knowledge_gap_not_data_gap():
    g=handle_gaps([make_gap("k","knowledge_gap","claim","no evidence")])
    assert g.status=="knowledge_gap" and not g.request_inputs

def test_sf05_stop_request_no_auto_resume_only_performed_steps():
    r=record_stop_request("stop","v1","s1",["performed"])
    assert not r.auto_resume and r.performed_steps==("performed",)

def test_sf06_restart_incomplete_checks_block():
    r=assess_restart_after_stop("v1","v2",True,True,False,True,True,True)
    assert not r.allowed and "fresh_safety" in r.missing_checks

def test_sf07_fresh_restart_allowed_only_under_new_version():
    r=assess_restart_after_stop("v1","v2",True,True,True,True,True,True)
    assert r.allowed and r.new_version=="v2"

def test_sf08_safety_stop_blocks_workflow_transition_bypass():
    assert not transition_case(W.AWAITING_EVALUATION,W.READY_FOR_SPECIALIST_DECISION,TransitionFacts(evaluation_complete=True,evidence_ready=True,safety_stop=True)).allowed
    assert not transition_case(W.AWAITING_EVALUATION,W.AWAITING_TEST,TransitionFacts(test_required=True,safety_stop=True)).allowed

def test_sf09_conditional_gate_suppresses_unqualified_options():
    a=validate_option_bundle([c()],DecisionSignals(valid_candidate=True,condition_pending=True))
    assert a.options==() and a.status=="blocked_by_gate"

def test_sf10_outside_scope_maps_to_scope_response():
    d=decide_motor_state(DecisionSignals(scope_exclusion=True))
    assert map_motor_to_response(d.state,"scope_exclusion").state==ConsultationResponseState.OUTSIDE_FIRST_VERSION_SCOPE
