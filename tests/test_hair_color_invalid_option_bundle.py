from app.domain.hair_color_invalid_option_bundle import validate_option_bundle
from app.domain.hair_color_option_selection import make_evaluated_option
from app.domain.hair_color_four_motor_states import DecisionSignals

def c(id,family,rank=1,validity="validated",refs=("e1",),basis="goal fit"):
    return make_evaluated_option(id,family,rank,validity,refs,basis)

def review_gate():
    return DecisionSignals(valid_candidate=True)

def test_valid_single_candidate_bundle():
    a=validate_option_bundle([c("A","بژ")],review_gate())
    assert a.status=="options_ready_for_review" and len(a.options)==1

def test_valid_multiple_candidates_preserve_rank():
    a=validate_option_bundle([c("B","طلایی",2),c("A","بژ",1)],review_gate())
    assert [x.option_id for x in a.options]==["A","B"]

def test_unvalidated_candidate_excluded_from_bundle():
    a=validate_option_bundle([c("A","بژ"),c("B","طلایی",2,"unvalidated")],review_gate())
    assert len(a.options)==1 and a.excluded[0][0]=="B"

def test_missing_evidence_candidate_not_presented():
    a=validate_option_bundle([c("A","بژ",refs=())],review_gate())
    assert a.status=="no_valid_options" and a.options==()

def test_duplicate_rank_conflict_suppresses_bundle():
    a=validate_option_bundle([c("A","بژ",1),c("B","طلایی",1)],review_gate())
    assert a.status=="ranking_conflict" and a.options==()

def test_duplicate_family_conflict_suppresses_bundle():
    a=validate_option_bundle([c("A","بژ",1),c("B","بژ",2)],review_gate())
    assert a.status=="duplicate_families" and a.options==()

def test_four_valid_candidates_fail_not_truncated():
    a=validate_option_bundle([c("A","بژ",1),c("B","طلایی",2),c("C","خاکستری",3),c("D","دودی",4)],review_gate())
    assert a.status=="too_many_valid_options" and a.options==()

def test_data_gap_blocks_option_bundle():
    a=validate_option_bundle([c("A","بژ")],DecisionSignals(data_gap=True))
    assert a.status=="blocked_by_gate" and a.options==()

def test_safety_stop_blocks_option_bundle():
    a=validate_option_bundle([c("A","بژ")],DecisionSignals(safety_stop=True))
    assert a.status=="stopped" and a.options==()

def test_knowledge_gap_stops_bundle():
    assert validate_option_bundle([c("A","بژ")],DecisionSignals(knowledge_gap=True)).status=="stopped"

def test_engine_failure_stops_bundle():
    assert validate_option_bundle([c("A","بژ")],DecisionSignals(engine_fail=True)).status=="stopped"

def test_conditional_state_does_not_emit_unqualified_options():
    a=validate_option_bundle([c("A","بژ")],DecisionSignals(valid_candidate=True,condition_pending=True))
    assert a.status=="blocked_by_gate" and a.options==()

def test_rejected_candidate_excluded():
    a=validate_option_bundle([c("A","بژ",validity="rejected")],review_gate())
    assert a.status=="no_valid_options"

def test_invalid_gate_fail_closed():
    a=validate_option_bundle([c("A","بژ")],None)
    assert a.status=="invalid_gate" and a.options==()
