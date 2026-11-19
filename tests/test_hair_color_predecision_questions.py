from app.domain.hair_color_predecision_questions import handle_predecision_question

def q(refs=(),event=None):
    return handle_predecision_question("q1","Question about the suggestion","awaiting_client_confirmation","sug-v1","case-v2",refs,event)

def test_question_without_decision_event_is_informational():
    a=q()
    assert a.decision_event is None
    assert a.case_state_unchanged and a.suggestion_id_unchanged and a.case_version_unchanged

def test_question_with_evidence_reference_can_answer_from_evidence():
    assert q(("doc-1",)).answer_status=="answer_from_recorded_evidence"

def test_no_evidence_does_not_guess():
    a=q()
    assert a.answer_status=="evidence_gap"
    assert "unavailable" in a.message

def test_question_does_not_accept_suggestion():
    a=q()
    assert a.decision_event is None

def test_question_does_not_reject_suggestion():
    a=q()
    assert a.decision_event is None

def test_question_does_not_grant_execution_consent():
    a=q()
    assert a.decision_event is None

def test_explicit_acceptance_is_separate_event_not_question_inference():
    a=q(event="accept_suggestion")
    assert a.decision_event=="accept_suggestion"
    assert a.case_state_unchanged

def test_explicit_rejection_is_separate_event():
    assert q(event="reject_suggestion").decision_event=="reject_suggestion"

def test_explicit_execution_consent_is_distinct_event():
    assert q(event="execution_consent").decision_event=="execution_consent"

def test_invalid_event_fail_closed():
    a=q(event="question means yes")
    assert a.answer_status=="invalid_decision_event"
    assert a.decision_event is None
