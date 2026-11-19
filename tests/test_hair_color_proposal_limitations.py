from app.domain.hair_color_proposal_limitations import make_limitation, assess_proposal_limitations

def lim(id,kind,blocking=True,condition=""):
    return make_limitation(id,kind,"recorded limit","affected claim",blocking,condition)

def test_no_limits_reviewable_not_execution_authority():
    a=assess_proposal_limitations([])
    assert a.status=="reviewable"
    assert a.motor_state=="suggestion_reviewable"
    assert "not execution consent" in a.message

def test_data_gap_requests_information():
    a=assess_proposal_limitations([lim("d","data_gap")])
    assert a.status=="data_gap"
    assert a.motor_state=="request_more_information"

def test_knowledge_gap_is_distinct_from_data_gap():
    a=assess_proposal_limitations([lim("k","knowledge_gap")])
    assert a.status=="knowledge_gap"
    assert a.response_gate=="knowledge_gap"
    assert "do not invent" in a.message

def test_safety_stop_blocks_suggestion():
    a=assess_proposal_limitations([lim("s","safety_stop")])
    assert a.status=="safety_stop"
    assert a.motor_state=="stop_or_referral"

def test_scope_exclusion_stops_out_of_scope_claim():
    a=assess_proposal_limitations([lim("x","scope_exclusion")])
    assert a.status=="scope_excluded"

def test_engine_failure_has_highest_precedence():
    a=assess_proposal_limitations([lim("d","data_gap"),lim("s","safety_stop"),lim("e","engine_fail")])
    assert a.status=="engine_fail"
    assert a.response_gate=="engine_fail"

def test_condition_is_conditional_not_new_response_state():
    a=assess_proposal_limitations([lim("c","condition",False,"confirm prerequisite")])
    assert a.status=="conditional"
    assert a.motor_state=="conditional_suggestion"

def test_nonblocking_data_gap_does_not_block_claim_gate():
    a=assess_proposal_limitations([lim("d","data_gap",False)])
    assert a.status=="reviewable"

def test_condition_requires_condition_text():
    assert make_limitation("c","condition","condition") is None

def test_invalid_limitation_type_fails_closed():
    assert assess_proposal_limitations(["invalid"]).status=="invalid_limitations"

def test_duplicate_ids_fail_closed():
    a=assess_proposal_limitations([lim("same","condition",False,"prereq"),lim("same","data_gap")])
    assert a.status=="duplicate_limitation_ids"

def test_unknown_kind_not_accepted():
    assert make_limitation("u","unknown","description") is None
