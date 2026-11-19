from app.domain.hair_color_rejected_suggestion_control import make_alternative, reject_and_select_alternatives

def alt(id,key,rank=1,valid=True,refs=("e1",),reason=""):
    return make_alternative(id,key,valid,rank,refs,reason)

def test_rejected_current_suggestion_traceable():
    a=reject_and_select_alternatives("s1","fingerprint1",[alt("s2","fingerprint2")])
    assert "s1" in a.rejected_ids and "fingerprint1" in a.rejected_keys

def test_rejected_id_cannot_reappear():
    a=reject_and_select_alternatives("s1","fp1",[alt("s1","fp1",2),alt("s2","fp2")])
    assert [x.suggestion_id for x in a.alternatives]==["s2"]
    assert a.excluded[0][0]=="s1"

def test_rejected_fingerprint_cannot_reappear_under_new_id():
    a=reject_and_select_alternatives("s1","fp1",[alt("new-id","fp1"),alt("s2","fp2",2)])
    assert [x.suggestion_id for x in a.alternatives]==["s2"]

def test_prior_rejection_is_persistent_across_runs():
    a=reject_and_select_alternatives("s9","fp9",[alt("s1","fp1")],rejected_ids=("s1",),rejected_keys=("fp1",))
    assert a.status=="no_valid_alternatives"

def test_invalid_candidate_excluded():
    a=reject_and_select_alternatives("s1","fp1",[alt("s2","fp2",valid=False,reason="invalid")])
    assert a.status=="no_valid_alternatives"

def test_candidate_without_evidence_excluded():
    a=reject_and_select_alternatives("s1","fp1",[alt("s2","fp2",refs=())])
    assert a.status=="no_valid_alternatives"

def test_one_valid_alternative_returns_only_one():
    a=reject_and_select_alternatives("s1","fp1",[alt("s2","fp2")])
    assert len(a.alternatives)==1 and a.status=="alternatives_ready_for_review"

def test_multiple_valid_alternatives_ranked():
    a=reject_and_select_alternatives("s1","fp1",[alt("s3","fp3",3),alt("s2","fp2",2)])
    assert [x.suggestion_id for x in a.alternatives]==["s2","s3"]

def test_more_than_three_alternatives_not_truncated():
    a=reject_and_select_alternatives("s1","fp1",[alt("s2","fp2",1),alt("s3","fp3",2),alt("s4","fp4",3),alt("s5","fp5",4)])
    assert a.status=="too_many_alternatives" and not a.alternatives

def test_duplicate_candidate_identity_fails_closed():
    a=reject_and_select_alternatives("s1","fp1",[alt("s2","fp2"),alt("s2","fp3",2)])
    assert a.status=="duplicate_candidate_identity"

def test_invalid_rejection_identity():
    assert reject_and_select_alternatives("","",[alt("s2","fp2")]).status=="invalid_rejection"
