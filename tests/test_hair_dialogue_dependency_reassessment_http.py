"""Dependency reassessment HTTP matrix for the synthetic-only hair dialogue API.

The HTTP caller cannot attest that dependencies are unchanged. Therefore
PRESERVE, unknown values, and missing outcomes are rejected at the boundary.
Only explicit INVALIDATE and UNRESOLVED outcomes are accepted.
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
    payload = {
        "action": "REASSESS_DEPENDENCIES",
        "state": _state(),
    }
    if invalidation_status is not ...:
        payload["invalidation_status"] = invalidation_status
    return client.post(ENDPOINT, headers=headers, json=payload)


@pytest.mark.parametrize(
    "invalidation_status",
    ["PRESERVE", "UNRECOGNIZED_STATUS", "INVALIDATE ", 123, True, []],
)
def test_http_rejects_caller_asserted_or_malformed_dependency_outcomes(
    client, db_session, invalidation_status
):
    headers = _headers(db_session, f"invalid-{str(invalidation_status)!r}"[:40])
    response = _post(client, headers, invalidation_status)
    assert response.status_code == 422


def test_http_requires_explicit_dependency_reassessment_outcome(client, db_session):
    headers = _headers(db_session, "missing-status")
    response = _post(client, headers, ...)
    assert response.status_code == 422


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
