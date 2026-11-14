"""HTTP transition matrix for the synthetic-only hair dialogue contract.

The tests cover state transitions at the API boundary. All identifiers and
states are synthetic; consent recording is not service execution.
"""
import pytest

from app.core.auth import create_access_token
from app.models.user_role import UserRole, ROLE_PO


ENDPOINT = "/api/v1/hair/dialogue/turn"


def _setup(client_db, subject):
    client_db.add(
        UserRole(
            user_role_id=f"UR-HAIR-TRANSITION-{subject}",
            subject_id=subject,
            role=ROLE_PO,
        )
    )
    client_db.flush()
    token = create_access_token({"sub": subject})
    return {"Authorization": f"Bearer {token}"}


def _state(**overrides):
    value = {
        "case_id": "SYNTHETIC-CASE-TRANSITION-01",
        "case_version": "v1",
        "goal_version": "g1",
    }
    value.update(overrides)
    return value


def test_attach_proposal_binds_it_to_current_versions(client, db_session):
    headers = _setup(db_session, "attach")
    response = client.post(
        ENDPOINT,
        headers=headers,
        json={
            "action": "ATTACH_PROPOSAL",
            "state": _state(),
            "proposal_id": "SYNTHETIC-PROPOSAL-01",
        },
    )

    assert response.status_code == 200
    state = response.json()["state"]
    assert state["active_proposal_id"] == "SYNTHETIC-PROPOSAL-01"
    assert state["active_proposal_case_version"] == "v1"
    assert state["active_proposal_goal_version"] == "g1"
    assert state["client_decision"] == "NONE"
    assert state["execution_consent_for_proposal_id"] is None
    assert response.json()["persistence"] == "COMPUTED_ONLY"


def test_rejected_proposal_cannot_be_reactivated_through_http(client, db_session):
    headers = _setup(db_session, "reject")
    rejected_state = _state(
        active_proposal_id="SYNTHETIC-PROPOSAL-REJECTED",
        active_proposal_case_version="v1",
        active_proposal_goal_version="g1",
        client_decision="REJECTED",
        rejected_proposal_ids=["SYNTHETIC-PROPOSAL-REJECTED"],
    )

    response = client.post(
        ENDPOINT,
        headers=headers,
        json={
            "action": "ATTACH_PROPOSAL",
            "state": rejected_state,
            "proposal_id": "SYNTHETIC-PROPOSAL-REJECTED",
        },
    )

    assert response.status_code == 422
    assert "cannot be reactivated" in response.json()["detail"]


def test_goal_change_invalidates_active_proposal_and_prior_decision(client, db_session):
    headers = _setup(db_session, "goal-change")
    response = client.post(
        ENDPOINT,
        headers=headers,
        json={
            "action": "CHANGE_GOAL",
            "state": _state(
                active_proposal_id="SYNTHETIC-PROPOSAL-OLD",
                active_proposal_case_version="v1",
                active_proposal_goal_version="g1",
                client_decision="ACCEPTED",
                execution_consent_for_proposal_id="SYNTHETIC-PROPOSAL-OLD",
            ),
            "new_goal_version": "g2",
        },
    )

    assert response.status_code == 200
    state = response.json()["state"]
    assert state["goal_version"] == "g2"
    assert state["active_proposal_id"] is None
    assert state["client_decision"] == "NONE"
    assert state["execution_consent_for_proposal_id"] is None
    assert response.json()["recommendation"] is None
    assert response.json()["display_allowed"] is False


def test_execution_consent_requires_explicit_consent_flag(client, db_session):
    headers = _setup(db_session, "consent-false")
    payload = {
        "action": "RECORD_EXECUTION_CONSENT",
        "state": _state(
            active_proposal_id="SYNTHETIC-PROPOSAL-ACCEPTED",
            active_proposal_case_version="v1",
            active_proposal_goal_version="g1",
            client_decision="ACCEPTED",
        ),
        "proposal_id": "SYNTHETIC-PROPOSAL-ACCEPTED",
        "explicit_consent": False,
    }

    response = client.post(ENDPOINT, headers=headers, json=payload)

    assert response.status_code == 422
    assert "Explicit execution consent" in response.json()["detail"]


def test_explicit_consent_is_bound_to_accepted_current_proposal_only(client, db_session):
    headers = _setup(db_session, "consent-true")
    payload = {
        "action": "RECORD_EXECUTION_CONSENT",
        "state": _state(
            active_proposal_id="SYNTHETIC-PROPOSAL-ACCEPTED",
            active_proposal_case_version="v1",
            active_proposal_goal_version="g1",
            client_decision="ACCEPTED",
        ),
        "proposal_id": "SYNTHETIC-PROPOSAL-ACCEPTED",
        "explicit_consent": True,
    }

    response = client.post(ENDPOINT, headers=headers, json=payload)

    assert response.status_code == 200
    state = response.json()["state"]
    assert state["execution_consent_for_proposal_id"] == "SYNTHETIC-PROPOSAL-ACCEPTED"
    assert response.json()["recommendation"] is None
    assert response.json()["display_allowed"] is False
    assert response.json()["client_visible"] is False
    assert response.json()["persistence"] == "COMPUTED_ONLY"
