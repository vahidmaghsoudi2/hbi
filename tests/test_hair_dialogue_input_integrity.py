"""Input-integrity tests for the synthetic-only hair dialogue HTTP boundary.

These tests pin down validation behavior visible at the API boundary. They use
synthetic identifiers and field-presence markers only; no customer values,
persistence, recommendation generation, or service execution are involved.
"""
import pytest

from app.core.auth import create_access_token
from app.models.user_role import UserRole, ROLE_REVIEWER_QA


ENDPOINT = "/api/v1/hair/dialogue/turn"


def _headers(db, subject):
    db.add(
        UserRole(
            user_role_id=f"UR-HAIR-INPUT-INTEGRITY-{subject}",
            subject_id=subject,
            role=ROLE_REVIEWER_QA,
        )
    )
    db.flush()
    token = create_access_token({"sub": subject})
    return {"Authorization": f"Bearer {token}"}


def _state(**overrides):
    state = {
        "case_id": "SYNTHETIC-CASE-INPUT-01",
        "case_version": "case-v1",
        "goal_version": "goal-v1",
    }
    state.update(overrides)
    return state


@pytest.mark.parametrize("version_field", ["case_version", "goal_version"])
def test_dialogue_rejects_blank_version_identifiers(client, db_session, version_field):
    headers = _headers(db_session, f"blank-{version_field}")
    state = _state(**{version_field: "   "})

    response = client.post(
        ENDPOINT,
        headers=headers,
        json={"action": "ANSWER_QUESTION", "state": state},
    )

    assert response.status_code == 422
    assert "versions must be non-empty" in response.json()["detail"]


def test_required_data_rejects_duplicate_field_presence_markers(client, db_session):
    headers = _headers(db_session, "duplicate-fields")

    response = client.post(
        ENDPOINT,
        headers=headers,
        json={
            "action": "RESOLVE_REQUIRED_DATA",
            "state": _state(),
            "recorded_fields": ["current_level", "current_level"],
            "required_fields": ["current_level"],
        },
    )

    assert response.status_code == 422
    assert "must not contain duplicates" in response.json()["detail"]


def test_required_data_returns_field_names_without_accepting_or_exposing_values(client, db_session):
    headers = _headers(db_session, "presence-only")
    response = client.post(
        ENDPOINT,
        headers=headers,
        json={
            "action": "RESOLVE_REQUIRED_DATA",
            "state": _state(),
            "recorded_fields": ["current_level"],
            "required_fields": ["current_level", "chemical_history"],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["result"] == {
        "known_fields": ["current_level"],
        "missing_fields": ["chemical_history"],
        "complete": False,
    }
    assert "SYNTHETIC_FIXTURE_VALUE" not in response.text
    assert body["recommendation"] is None
    assert body["display_allowed"] is False
    assert body["client_visible"] is False
    assert body["persistence"] == "COMPUTED_ONLY"


def test_advice_gate_requires_every_boolean_input_to_be_explicit(client, db_session):
    headers = _headers(db_session, "gate-inputs")

    response = client.post(
        ENDPOINT,
        headers=headers,
        json={
            "action": "EVALUATE_ADVICE_GATE",
            "state": _state(),
        },
    )

    assert response.status_code == 422
    assert "All advice gate inputs must be explicit" in response.json()["detail"]


def test_advice_gate_rejects_partial_boolean_input_set(client, db_session):
    headers = _headers(db_session, "partial-gate-inputs")

    response = client.post(
        ENDPOINT,
        headers=headers,
        json={
            "action": "EVALUATE_ADVICE_GATE",
            "state": _state(),
            "data_complete": True,
            "safety_passed": True,
            "rule_valid": True,
        },
    )

    assert response.status_code == 422
    assert "All advice gate inputs must be explicit" in response.json()["detail"]
