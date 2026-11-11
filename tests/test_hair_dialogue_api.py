"""HTTP-level conformance for the stateless, synthetic Hair dialogue runtime."""
from copy import deepcopy

from app.core.auth import create_access_token
from app.models.user_role import ROLE_REVIEWER_QA, UserRole


def _headers():
    token = create_access_token({"sub": "hair-dialogue-api-test-user"})
    return {"Authorization": f"Bearer {token}"}


def _grant_reviewer_qa(db_session):
    db_session.add(UserRole(
        user_role_id="HAIR-DIALOGUE-REVIEWER",
        subject_id="hair-dialogue-api-test-user",
        role=ROLE_REVIEWER_QA,
    ))
    db_session.commit()


def _state(**overrides):
    value = {
        "case_id": "SYNTHETIC-DIALOGUE-API-001",
        "case_version": "case-v1",
        "goal_version": "goal-v1",
        "active_proposal_id": None,
        "active_proposal_case_version": None,
        "active_proposal_goal_version": None,
        "rejected_proposal_ids": [],
        "client_decision": "NONE",
        "execution_consent_for_proposal_id": None,
    }
    value.update(overrides)
    return value


def _turn(client, state, action, **fields):
    return client.post(
        "/api/v1/hair/dialogue/turn",
        json={"action": action, "state": state, **fields},
        headers=_headers(),
    )


def test_dialogue_runtime_requires_internal_role(client, db_session):
    response = client.post(
        "/api/v1/hair/dialogue/turn",
        json={"action": "ANSWER_QUESTION", "state": _state(), "question": "چرا؟", "answer": "توضیح"},
        headers=_headers(),
    )
    assert response.status_code == 403


def test_sequential_questions_preserve_versions_decisions_and_non_persistence(client, db_session):
    _grant_reviewer_qa(db_session)
    state = _state()
    first = _turn(client, state, "ANSWER_QUESTION", question="سؤال اول", answer="پاسخ اول")
    assert first.status_code == 200
    second = _turn(client, first.json()["state"], "ANSWER_QUESTION", question="سؤال دوم", answer="پاسخ دوم")
    assert second.status_code == 200
    body = second.json()
    assert body["state"]["case_version"] == "case-v1"
    assert body["state"]["goal_version"] == "goal-v1"
    assert body["state"]["client_decision"] == "NONE"
    assert body["state"]["execution_consent_for_proposal_id"] is None
    assert body["recommendation"] is None
    assert body["display_allowed"] is False
    assert body["client_visible"] is False
    assert body["persistence"] == "COMPUTED_ONLY"


def test_acceptance_and_execution_consent_are_separate_http_transitions(client, db_session):
    _grant_reviewer_qa(db_session)
    state = _state(
        active_proposal_id="SYNTHETIC-PROPOSAL-API-1",
        active_proposal_case_version="case-v1",
        active_proposal_goal_version="goal-v1",
    )
    accepted = _turn(client, state, "ACCEPT_PROPOSAL", proposal_id="SYNTHETIC-PROPOSAL-API-1")
    assert accepted.status_code == 200
    accepted_state = accepted.json()["state"]
    assert accepted_state["client_decision"] == "ACCEPTED"
    assert accepted_state["execution_consent_for_proposal_id"] is None

    denied = _turn(client, accepted_state, "RECORD_EXECUTION_CONSENT",
                   proposal_id="SYNTHETIC-PROPOSAL-API-1", explicit_consent=False)
    assert denied.status_code == 422

    consented = _turn(client, accepted_state, "RECORD_EXECUTION_CONSENT",
                      proposal_id="SYNTHETIC-PROPOSAL-API-1", explicit_consent=True)
    assert consented.status_code == 200
    assert consented.json()["state"]["execution_consent_for_proposal_id"] == "SYNTHETIC-PROPOSAL-API-1"


def test_goal_change_invalidates_proposal_acceptance_and_consent(client, db_session):
    _grant_reviewer_qa(db_session)
    state = _state(
        active_proposal_id="SYNTHETIC-PROPOSAL-API-2",
        active_proposal_case_version="case-v1",
        active_proposal_goal_version="goal-v1",
        client_decision="ACCEPTED",
        execution_consent_for_proposal_id="SYNTHETIC-PROPOSAL-API-2",
    )
    response = _turn(client, state, "CHANGE_GOAL", new_goal_version="goal-v2")
    assert response.status_code == 200
    result = response.json()["state"]
    assert result["goal_version"] == "goal-v2"
    assert result["active_proposal_id"] is None
    assert result["client_decision"] == "NONE"
    assert result["execution_consent_for_proposal_id"] is None


def test_rejected_proposal_cannot_be_reactivated(client, db_session):
    _grant_reviewer_qa(db_session)
    state = _state(
        active_proposal_id="SYNTHETIC-PROPOSAL-API-3",
        active_proposal_case_version="case-v1",
        active_proposal_goal_version="goal-v1",
    )
    rejected = _turn(client, state, "REJECT_PROPOSAL", proposal_id="SYNTHETIC-PROPOSAL-API-3")
    assert rejected.status_code == 200
    next_state = rejected.json()["state"]
    assert next_state["rejected_proposal_ids"] == ["SYNTHETIC-PROPOSAL-API-3"]
    assert next_state["active_proposal_id"] is None
    reactivated = _turn(client, next_state, "ATTACH_PROPOSAL", proposal_id="SYNTHETIC-PROPOSAL-API-3")
    assert reactivated.status_code == 422


def test_required_data_and_advice_gate_return_explicit_gaps(client, db_session):
    _grant_reviewer_qa(db_session)
    resolved = _turn(
        client, _state(), "RESOLVE_REQUIRED_DATA",
        recorded_data={"brand": "Synthetic Brand", "history": ""},
        required_fields=["brand", "history", "hair_history"],
    )
    assert resolved.status_code == 200
    assert resolved.json()["result"]["missing_fields"] == ["history", "hair_history"]
    gate = _turn(
        client, _state(), "EVALUATE_ADVICE_GATE",
        data_complete=False, safety_passed=True, rule_valid=True, evidence_valid=True,
    )
    assert gate.status_code == 200
    assert gate.json()["result"] == {"advice_allowed": False, "reason_codes": ["DATA_GAP"]}


def test_runtime_rejects_real_case_ids_and_unrecognized_request_fields(client, db_session):
    _grant_reviewer_qa(db_session)
    real_case = _turn(client, _state(case_id="REAL-CLIENT-001"), "ANSWER_QUESTION",
                      question="سؤال", answer="پاسخ")
    assert real_case.status_code == 422
    malformed = _turn(client, _state(), "ANSWER_QUESTION",
                      question="سؤال", answer="پاسخ", customer_id="must-not-be-accepted")
    assert malformed.status_code == 422


def test_engine_failure_has_priority_and_never_allows_advice(client, db_session):
    _grant_reviewer_qa(db_session)
    response = _turn(
        client, _state(), "EVALUATE_ADVICE_GATE",
        data_complete=False, safety_passed=False, rule_valid=False,
        evidence_valid=False, engine_ok=False,
    )
    assert response.status_code == 200
    assert response.json()["result"] == {"advice_allowed": False, "reason_codes": ["ENGINE_FAIL"]}
    assert response.json()["recommendation"] is None
