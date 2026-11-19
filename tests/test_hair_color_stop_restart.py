from app.domain.hair_color_stop_restart import record_stop_request, assess_restart_after_stop

def test_stop_request_records_only_performed_steps():
    r=record_stop_request("stop1","v1","s1",["step-a"])
    assert r.performed_steps==("step-a",)
    assert r.status=="consultation_stopped_by_client"

def test_stop_never_auto_resumes():
    r=record_stop_request("stop1","v1","s1",[])
    assert r.auto_resume is False
    assert r.prior_decisions_invalidated is True

def test_empty_performed_steps_are_valid_and_not_invented():
    r=record_stop_request("stop1","v1","s1",[])
    assert r.performed_steps==()

def test_invalid_performed_steps_rejected():
    assert record_stop_request("stop1","v1","s1",["",None]) is None

def test_restart_requires_new_version():
    assert not assess_restart_after_stop("v1","v1",True,True,True,True,True,True).allowed

def test_restart_missing_checks_blocked():
    a=assess_restart_after_stop("v1","v2",True,True,True,True,False,True)
    assert not a.allowed
    assert "fresh_evidence" in a.missing_checks

def test_restart_requires_all_fresh_inputs_and_authorization():
    a=assess_restart_after_stop("v1","v2",True,True,True,True,True,True)
    assert a.allowed and a.new_version=="v2"

def test_restart_requires_fresh_hair_state():
    a=assess_restart_after_stop("v1","v2",False,True,True,True,True,True)
    assert not a.allowed and "fresh_hair_state" in a.missing_checks

def test_restart_requires_fresh_safety_check():
    a=assess_restart_after_stop("v1","v2",True,True,False,True,True,True)
    assert not a.allowed and "fresh_safety" in a.missing_checks

def test_restart_requires_explicit_restart_authorization():
    a=assess_restart_after_stop("v1","v2",True,True,True,True,True,False)
    assert not a.allowed and "restart_authorized" in a.missing_checks
