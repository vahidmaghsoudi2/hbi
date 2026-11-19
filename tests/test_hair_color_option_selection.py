from app.domain.hair_color_option_selection import make_evaluated_option, select_reviewable_options

def candidate(id="A",family="بژ",rank=1,validity="validated",refs=("evidence-1",),basis="goal-fit reviewed",reason=""):
    return make_evaluated_option(id,family,rank,validity,refs,basis,(),reason)

def test_single_valid_option_is_only_option_returned():
    a=select_reviewable_options([candidate()])
    assert a.status=="options_ready_for_review"
    assert len(a.selected)==1

def test_multiple_valid_options_preserve_explicit_rank():
    a=select_reviewable_options([candidate("B","طلایی",2),candidate("A","بژ",1)])
    assert [x.option_id for x in a.selected]==["A","B"]

def test_unvalidated_option_is_excluded():
    a=select_reviewable_options([candidate(),candidate("B","طلایی",2,"unvalidated")])
    assert a.status=="options_ready_for_review"
    assert len(a.selected)==1 and a.excluded[0][0]=="B"

def test_validity_without_evidence_is_excluded():
    a=select_reviewable_options([candidate(refs=())])
    assert a.status=="no_valid_options"

def test_validity_without_goal_fit_basis_is_excluded():
    a=select_reviewable_options([candidate(basis="")])
    assert a.status=="no_valid_options"

def test_rejected_candidate_is_not_presented():
    a=select_reviewable_options([candidate(validity="rejected",reason="invalid for scope")])
    assert a.status=="no_valid_options"
    assert a.selected==()

def test_duplicate_rank_fails_closed():
    a=select_reviewable_options([candidate("A","بژ",1),candidate("B","طلایی",1)])
    assert a.status=="ranking_conflict"

def test_duplicate_family_candidates_fail_closed():
    a=select_reviewable_options([candidate("A","بژ",1),candidate("B","بژ",2)])
    assert a.status=="duplicate_families"

def test_invalid_candidate_type_fails_closed():
    assert select_reviewable_options(["invalid"]).status=="invalid_candidates"

def test_more_than_three_valid_options_not_truncated():
    a=select_reviewable_options([candidate("A","بژ",1),candidate("B","طلایی",2),candidate("C","خاکستری",3),candidate("D","دودی",4)])
    assert a.status=="too_many_valid_options"
    assert a.selected==()

def test_duplicate_option_ids_fail_closed():
    a=select_reviewable_options([candidate("same","بژ",1),candidate("same","طلایی",2)])
    assert a.status=="duplicate_option_ids"

def test_empty_candidates_does_not_fabricate():
    assert select_reviewable_options([]).status=="no_candidates"
