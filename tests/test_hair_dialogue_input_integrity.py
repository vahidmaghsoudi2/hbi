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


from itertools import product


@pytest.mark.parametrize(
    ("data_complete", "safety_passed", "rule_valid", "evidence_valid"),
    list(product((False, True), repeat=4)),
)
def test_advice_gate_truth_table_never_allows_advice_with_a_failed_precondition(
    client, db_session, data_complete, safety_passed, rule_valid, evidence_valid
):
    headers = _headers(
        db_session,
        f"truth-{int(data_complete)}-{int(safety_passed)}-{int(rule_valid)}-{int(evidence_valid)}",
    )
    response = client.post(
        ENDPOINT,
        headers=headers,
        json={
            "action": "EVALUATE_ADVICE_GATE",
            "state": _state(),
            "data_complete": data_complete,
            "safety_passed": safety_passed,
            "rule_valid": rule_valid,
            "evidence_valid": evidence_valid,
            "engine_ok": True,
        },
    )

    assert response.status_code == 200
    result = response.json()["result"]
    if not safety_passed:
        expected_reasons = ["SAFETY_STOP"]
    else:
        expected_reasons = []
        if not data_complete:
            expected_reasons.append("DATA_GAP")
        if not rule_valid or not evidence_valid:
            expected_reasons.append("KNOWLEDGE_GAP")
    assert result["reason_codes"] == expected_reasons
    assert result["advice_allowed"] is (not expected_reasons)


def test_advice_gate_engine_failure_overrides_otherwise_valid_inputs(client, db_session):
    headers = _headers(db_session, "engine-failure-precedence")
    response = client.post(
        ENDPOINT,
        headers=headers,
        json={
            "action": "EVALUATE_ADVICE_GATE",
            "state": _state(),
            "data_complete": True,
            "safety_passed": True,
            "rule_valid": True,
            "evidence_valid": True,
            "engine_ok": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["result"] == {
        "advice_allowed": False,
        "reason_codes": ["ENGINE_FAIL"],
    }
