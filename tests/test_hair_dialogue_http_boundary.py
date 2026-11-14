"""HTTP-boundary regression tests for the synthetic-only hair dialogue endpoint.

These tests exercise the existing stateless API contract only. They do not
introduce persistence, customer data, recommendation logic, or service execution.
"""
import pytest

from app.core.auth import create_access_token
from app.models.user_role import UserRole, ROLE_EDITOR, ROLE_REVIEWER_QA


ENDPOINT = "/api/v1/hair/dialogue/turn"


def _seed_role(db, subject_id, role):
    db.add(
        UserRole(
            user_role_id=f"UR-HAIR-DIALOGUE-{subject_id}",
            subject_id=subject_id,
            role=role,
        )
    )
    db.flush()


def _headers(subject_id):
    token = create_access_token({"sub": subject_id})
    return {"Authorization": f"Bearer {token}"}


def _payload(**overrides):
    value = {
        "action": "ANSWER_QUESTION",
        "state": {
            "case_id": "SYNTHETIC-CASE-HTTP-01",
            "case_version": "1",
            "goal_version": "1",
        },
        "question_code": "STATUS_REASON",
        "answer_code": "STATUS_REASON",
    }
    value.update(overrides)
    return value


def test_dialogue_http_response_is_computed_only_and_never_client_visible(client, db_session):
    _seed_role(db_session, "hair_dialogue_reviewer", ROLE_REVIEWER_QA)

    response = client.post(
        ENDPOINT,
        json=_payload(),
        headers=_headers("hair_dialogue_reviewer"),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["recommendation"] is None
    assert body["display_allowed"] is False
    assert body["client_visible"] is False
    assert body["persistence"] == "COMPUTED_ONLY"
    assert body["result"]["decision_changed"] is False


def test_dialogue_http_rejects_non_synthetic_case_identifier(client, db_session):
    _seed_role(db_session, "hair_dialogue_non_synthetic", ROLE_REVIEWER_QA)
    payload = _payload(
        state={
            "case_id": "CASE-REAL-LOOKING-01",
            "case_version": "1",
            "goal_version": "1",
        }
    )

    response = client.post(
        ENDPOINT,
        json=payload,
        headers=_headers("hair_dialogue_non_synthetic"),
    )

    assert response.status_code == 422
    assert "synthetic case identifiers only" in response.json()["detail"]


def test_dialogue_http_rejects_unapproved_role(client, db_session):
    _seed_role(db_session, "hair_dialogue_editor", ROLE_EDITOR)

    response = client.post(
        ENDPOINT,
        json=_payload(),
        headers=_headers("hair_dialogue_editor"),
    )

    assert response.status_code == 403


def test_dialogue_http_rejects_unknown_request_fields(client, db_session):
    _seed_role(db_session, "hair_dialogue_extra_field", ROLE_REVIEWER_QA)
    payload = _payload(unapproved_customer_value="must-not-enter-contract")

    response = client.post(
        ENDPOINT,
        json=payload,
        headers=_headers("hair_dialogue_extra_field"),
    )

    assert response.status_code == 422


def test_accepting_proposal_does_not_create_execution_consent(client, db_session):
    _seed_role(db_session, "hair_dialogue_acceptance", ROLE_REVIEWER_QA)
    payload = {
        "action": "ACCEPT_PROPOSAL",
        "state": {
            "case_id": "SYNTHETIC-CASE-HTTP-02",
            "case_version": "4",
            "goal_version": "2",
            "active_proposal_id": "PROPOSAL-SYN-02",
            "active_proposal_case_version": "4",
            "active_proposal_goal_version": "2",
        },
        "proposal_id": "PROPOSAL-SYN-02",
    }

    response = client.post(
        ENDPOINT,
        json=payload,
        headers=_headers("hair_dialogue_acceptance"),
    )

    assert response.status_code == 200
    state = response.json()["state"]
    assert state["client_decision"] == "ACCEPTED"
    assert state["execution_consent_for_proposal_id"] is None
    assert response.json()["recommendation"] is None
    assert response.json()["persistence"] == "COMPUTED_ONLY"
