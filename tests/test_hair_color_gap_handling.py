from app.domain.hair_color_gap_handling import make_gap, handle_gaps

def dg():
    return make_gap("d1","data_gap","claim-a","required input missing","current base")

def kg():
    return make_gap("k1","knowledge_gap","claim-b","no reliable source")

def eg():
    return make_gap("e1","engine_fail","run","internal error")

def test_data_gap_requests_specific_input():
    a=handle_gaps([dg()])
    assert a.status=="data_gap"
    assert a.request_inputs==("current base",)

def test_knowledge_gap_does_not_request_customer_data():
    a=handle_gaps([kg()])
    assert a.status=="knowledge_gap"
    assert a.request_inputs==()

def test_engine_fail_suppresses_entire_run():
    a=handle_gaps([eg()])
    assert a.status=="engine_fail"
    assert a.output_policy=="suppress_run_output"

def test_mixed_data_and_knowledge_gaps_keep_both():
    a=handle_gaps([dg(),kg()])
    assert a.status=="mixed_gaps"
    assert a.data_gap_ids==("d1",) and a.knowledge_gap_ids==("k1",)
    assert a.request_inputs==("current base",)

def test_engine_fail_overrides_other_gap_handling():
    a=handle_gaps([dg(),kg(),eg()])
    assert a.status=="engine_fail"

def test_no_gaps_has_neutral_gate():
    assert handle_gaps([]).status=="no_gap"

def test_invalid_gap_record_fail_closed():
    assert handle_gaps(["bad"]).status=="invalid_gaps"

def test_duplicate_gap_ids_fail_closed():
    a=handle_gaps([dg(),make_gap("d1","data_gap","claim-c","other missing","history")])
    assert a.status=="duplicate_gap_ids"

def test_data_gap_requires_specific_input():
    assert make_gap("d","data_gap","claim","missing","") is None

def test_knowledge_gap_rejects_required_input_field():
    assert make_gap("k","knowledge_gap","claim","no evidence","customer data") is None

def test_unknown_gap_kind_rejected():
    assert make_gap("x","other","claim","detail") is None
