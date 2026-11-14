"""Dependency reassessment HTTP matrix for the synthetic-only hair dialogue API.

The matrix verifies preservation, invalidation, unresolved dependencies, and
unknown-status fail-closed behavior. It never creates recommendations,
customer records, persistence, or service execution.
"""
import pytest

from app.core.auth import create_access_token
from app.models.user_role import UserRole, ROLE_REVIEWER_QA


ENDPOINT = "/api/v1/hair/dialogue/turn"


def _headers(db, subject):
    db.add(
        UserRole(
            user_role_id=f"UR-HAIR-REASSESS-{subject}",
            subject_id=subject,
            role=ROLE_REVIEWER_QA,
        )
    )
    db.flush()
    token = create_access_token({"sub": subject})
    return {"Authorization": f"Bearer {token}"}


def _state():
    return {
        "case_id": "SYNTHETIC-CASE-REASSESS-01",
        "case_version": "case-v3",
        "goal_version": "goal-v2",
        "active_proposal_id": "SYNTHETIC-PROPOSAL-CURRENT",
        "active_proposal_case_version": "case-v3",
        "active_proposal_goal_version": "goal-v2",
        "client_decision": "ACCEPTED",
        "execution_consent_for_proposal_id": "SYNTHETIC-PROPOSAL-CURRENT",
    }


def _post(client, headers, invalidation_status):
    return client.post(
        ENDPOINT,
        headers=headers,
        json={
            "action": "REASSESS_DEPENDENCIES",
            "state": _state(),
            "invalidation_status": invalidation_status,
        },
    )


def test_preserve_reassessment_keeps_current_version_bound_decision_and_consent(client, db_session):
    headers = _headers(db_session, "preserve")
    response = _post(client, headers, "PRESERVE")

    assert response.status_code == 200
    body = response.json()
    assert body["result"]["status"] == "PRESERVED"
    assert body["state"]["active_proposal_id"] == "SYNTHETIC-PROPOSAL-CURRENT"
    assert body["state"]["active_proposal_case_version"] == "case-v3"
    assert body["state"]["active_proposal_goal_version"] == "goal-v2"
    assert body["state"]["client_decision"] == "ACCEPTED"
    assert body["state"]["execution_consent_for_proposal_id"] == "SYNTHETIC-PROPOSAL-CURRENT"


@pytest.mark.parametrize(
    ("invalidation_status", "expected_status"),
    [
        ("INVALIDATE", "INVALIDATED"),
        ("UNRESOLVED", "REASSESSMENT_REQUIRED"),
    ],
)
def test_effective_or_unresolved_dependency_change_clears_dependent_decisions(
    client, db_session, invalidation_status, expected_status
):
    headers = _headers(db_session, f"dependency-{invalidation_status.lower()}")
    response = _post(client, headers, invalidation_status)

    assert response.status_code == 200
    body = response.json()
    assert body["result"]["status"] == expected_status
    assert body["state"]["active_proposal_id"] is None
    assert body["state"]["active_proposal_case_version"] is None
    assert body["state"]["active_proposal_goal_version"] is None
    assert body["state"]["client_decision"] == "NONE"
    assert body["state"]["execution_consent_for_proposal_id"] is None
    assert body["recommendation"] is None
    assert body["display_allowed"] is False
    assert body["client_visible"] is False
    assert body["persistence"] == "COMPUTED_ONLY"


def test_unknown_dependency_status_fails_closed_and_clears_all_dependent_decisions(client, db_session):
    headers = _headers(db_session, "unknown-status")
    response = _post(client, headers, "UNRECOGNIZED_STATUS")

    assert response.status_code == 200
    body = response.json()
    assert body["result"]["status"] == "ENGINE_FAIL_CLOSED"
    assert body["state"]["active_proposal_id"] is None
    assert body["state"]["active_proposal_case_version"] is None
    assert body["state"]["active_proposal_goal_version"] is None
    assert body["state"]["client_decision"] == "NONE"
    assert body["state"]["execution_consent_for_proposal_id"] is None
    assert body["recommendation"] is None
    assert body["display_allowed"] is False
    assert body["client_visible"] is False
    assert body["persistence"] == "COMPUTED_ONLY"


def test_missing_dependency_status_fails_closed_instead_of_preserving_prior_consent(client, db_session):
    headers = _headers(db_session, "missing-status")
    response = _post(client, headers, None)

    assert response.status_code == 200
    body = response.json()
    assert body["result"]["status"] == "ENGINE_FAIL_CLOSED"
    assert body["state"]["active_proposal_id"] is None
    assert body["state"]["client_decision"] == "NONE"
    assert body["state"]["execution_consent_for_proposal_id"] is None
