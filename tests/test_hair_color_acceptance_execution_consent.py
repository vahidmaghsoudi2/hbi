from app.domain.hair_color_acceptance_execution_consent import (
    Acceptance, Consent, new_decision_record, record_acceptance, record_execution_consent, evaluate_execution_gate
)

def rec():
    return new_decision_record("v1","suggestion-1")

def test_acceptance_does_not_grant_execution_consent():
    r=record_acceptance(rec(),"accepted","v1","suggestion-1").record
    assert r.acceptance==Acceptance.ACCEPTED
    assert r.execution_consent==Consent.PENDING
    assert not evaluate_execution_gate(r,True,True,False).authorized

def test_rejection_prevents_consent():
    r=record_acceptance(rec(),"rejected","v1","suggestion-1").record
    assert r.acceptance==Acceptance.REJECTED
    assert record_execution_consent(r,"granted","v1","suggestion-1").status=="acceptance_required"

def test_consent_is_separate_after_acceptance():
    r=record_acceptance(rec(),"accepted","v1","suggestion-1").record
    r=record_execution_consent(r,"granted","v1","suggestion-1").record
    assert r.execution_consent==Consent.GRANTED

def test_withheld_consent_blocks_execution():
    r=record_acceptance(rec(),"accepted","v1","suggestion-1").record
    r=record_execution_consent(r,"withheld","v1","suggestion-1").record
    assert not evaluate_execution_gate(r,True,True,False).authorized

def test_all_gates_required_for_execution_authorization():
    r=record_acceptance(rec(),"accepted","v1","suggestion-1").record
    r=record_execution_consent(r,"granted","v1","suggestion-1").record
    assert evaluate_execution_gate(r,True,True,False).authorized

def test_specialist_approval_missing_blocks():
    r=record_acceptance(rec(),"accepted","v1","suggestion-1").record
    r=record_execution_consent(r,"granted","v1","suggestion-1").record
    assert not evaluate_execution_gate(r,False,True,False).authorized

def test_safety_stop_blocks_even_if_all_other_gates_satisfied():
    r=record_acceptance(rec(),"accepted","v1","suggestion-1").record
    r=record_execution_consent(r,"granted","v1","suggestion-1").record
    assert not evaluate_execution_gate(r,True,True,True).authorized

def test_stale_version_rejects_acceptance():
    assert record_acceptance(rec(),"accepted","v2","suggestion-1").status=="stale_version_or_suggestion"

def test_stale_suggestion_rejects_consent():
    r=record_acceptance(rec(),"accepted","v1","suggestion-1").record
    assert record_execution_consent(r,"granted","v1","other").status=="stale_version_or_suggestion"

def test_invalid_acceptance_or_consent_rejected():
    assert record_acceptance(rec(),"maybe","v1","suggestion-1").status=="invalid_acceptance"
    r=record_acceptance(rec(),"accepted","v1","suggestion-1").record
    assert record_execution_consent(r,"maybe","v1","suggestion-1").status=="invalid_consent"

def test_new_record_requires_version_and_suggestion_identity():
    assert new_decision_record("","suggestion-1") is None
