"""Ten-scenario synthetic dialogue journey exercised through the public HTTP route.

This is a contract test only: no real client, chemical advice, persistence,
recommendation publication, or service execution is involved.
"""
from app.core.auth import create_access_token
from app.models.user_role import ROLE_REVIEWER_QA, UserRole


def _state(**overrides):
    value = {
        "case_id": "SYNTHETIC-DIALOGUE-HTTP-JOURNEY-001",
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
    token = create_access_token({"sub": "hair-dialogue-http-journey-user"})
    return client.post(
        "/api/v1/hair/dialogue/turn",
        json={"action": action, "state": state, **fields},
        headers={"Authorization": f"Bearer {token}"},
    )


def _assert_envelope(response):
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["recommendation"] is None
    assert body["display_allowed"] is False
    assert body["client_visible"] is False
    assert body["persistence"] == "COMPUTED_ONLY"
    return body


def test_all_ten_dialogue_scenarios_complete_as_one_http_journey(client, db_session):
    db_session.add(
        UserRole(
            user_role_id="HAIR-DIALOGUE-HTTP-JOURNEY-ROLE",
            subject_id="hair-dialogue-http-journey-user",
            role=ROLE_REVIEWER_QA,
        )
    )
    db_session.commit()

    # 1 + 8: sequential and pre-decision questions preserve state and do not decide.
    state = _state()
    attached = _assert_envelope(
        _turn(client, state, "ATTACH_PROPOSAL", proposal_id="SYNTHETIC-JOURNEY-PROPOSAL-1")
    )["state"]
    first_question = _assert_envelope(
        _turn(
            client, attached, "ANSWER_QUESTION",
            question_code="STATUS_REASON", answer_code="STATUS_REASON",
        )
    )["state"]
    assert first_question["client_decision"] == "NONE"
    second_question = _assert_envelope(
        _turn(
            client, first_question, "ANSWER_QUESTION",
            question_code="PROCESS_LIMIT", answer_code="PROCESS_LIMIT",
        )
    )["state"]
    assert second_question["case_version"] == "case-v1"
    assert second_question["goal_version"] == "goal-v1"
    assert second_question["client_decision"] == "NONE"
    assert second_question["execution_consent_for_proposal_id"] is None

    # 2: a reason is returned as an explicit client-safe summary.
    explained = _assert_envelope(
        _turn(client, second_question, "EXPLAIN_REASON", reason_code="DATA_GAP")
    )
    assert explained["result"]["summary_fa"] == (
        "دادهٔ ضروری کافی نیست؛ نتیجهٔ قطعی ارائه نمی‌شود."
    )

    # 3: recorded-field presence is reported without exposing supplied values.
    resolved = _assert_envelope(
        _turn(
            client, second_question, "RESOLVE_REQUIRED_DATA",
            recorded_fields=["brand", "shade_number"],
            required_fields=["brand", "shade_number", "history", "hair_history"],
        )
    )
    assert resolved["result"]["known_fields"] == ["brand", "shade_number"]
    assert resolved["result"]["missing_fields"] == ["history", "hair_history"]
    assert "SYNTHETIC_FIXTURE_VALUE" not in str(resolved["result"])

    # 4: insufficient data withholds advice and reports DATA_GAP.
    data_gap = _assert_envelope(
        _turn(
            client, second_question, "EVALUATE_ADVICE_GATE",
            data_complete=False, safety_passed=True, rule_valid=True,
            evidence_valid=True, engine_ok=True,
        )
    )
    assert data_gap["result"] == {
        "advice_allowed": False, "reason_codes": ["DATA_GAP"]
    }

    # 5: changing the goal creates a new version and clears the dependent proposal.
    changed = _assert_envelope(
        _turn(client, second_question, "CHANGE_GOAL", new_goal_version="goal-v2")
    )["state"]
    assert changed["goal_version"] == "goal-v2"
    assert changed["active_proposal_id"] is None
    assert changed["client_decision"] == "NONE"
    assert changed["execution_consent_for_proposal_id"] is None

    # 6: a rejected proposal is traceable and cannot be reactivated.
    second_proposal = _assert_envelope(
        _turn(client, changed, "ATTACH_PROPOSAL", proposal_id="SYNTHETIC-JOURNEY-PROPOSAL-2")
    )["state"]
    rejected = _assert_envelope(
        _turn(
            client, second_proposal, "REJECT_PROPOSAL",
            proposal_id="SYNTHETIC-JOURNEY-PROPOSAL-2",
        )
    )["state"]
    assert rejected["rejected_proposal_ids"] == ["SYNTHETIC-JOURNEY-PROPOSAL-2"]
    reactivation = _turn(
        client, rejected, "ATTACH_PROPOSAL",
        proposal_id="SYNTHETIC-JOURNEY-PROPOSAL-2",
    )
    assert reactivation.status_code == 422

    # 7: acceptance and explicit execution consent remain separate transitions.
    third_proposal = _assert_envelope(
        _turn(client, rejected, "ATTACH_PROPOSAL", proposal_id="SYNTHETIC-JOURNEY-PROPOSAL-3")
    )["state"]
    accepted = _assert_envelope(
        _turn(
            client, third_proposal, "ACCEPT_PROPOSAL",
            proposal_id="SYNTHETIC-JOURNEY-PROPOSAL-3",
        )
    )["state"]
    assert accepted["client_decision"] == "ACCEPTED"
    assert accepted["execution_consent_for_proposal_id"] is None
    no_consent = _turn(
        client, accepted, "RECORD_EXECUTION_CONSENT",
        proposal_id="SYNTHETIC-JOURNEY-PROPOSAL-3", explicit_consent=False,
    )
    assert no_consent.status_code == 422
    consented = _assert_envelope(
        _turn(
            client, accepted, "RECORD_EXECUTION_CONSENT",
            proposal_id="SYNTHETIC-JOURNEY-PROPOSAL-3", explicit_consent=True,
        )
    )["state"]
    assert consented["execution_consent_for_proposal_id"] == "SYNTHETIC-JOURNEY-PROPOSAL-3"

    # 9: absent evidence returns KNOWLEDGE_GAP and never a recommendation.
    knowledge_gap = _assert_envelope(
        _turn(
            client, consented, "EVALUATE_ADVICE_GATE",
            data_complete=True, safety_passed=True, rule_valid=True,
            evidence_valid=False, engine_ok=True,
        )
    )
    assert knowledge_gap["result"] == {
        "advice_allowed": False, "reason_codes": ["KNOWLEDGE_GAP"]
    }

    # 10: unresolved dependency change clears acceptance and consent (fail closed).
    reassessed = _assert_envelope(
        _turn(
            client, consented, "REASSESS_DEPENDENCIES",
            invalidation_status="UNRESOLVED",
        )
    )
    assert reassessed["result"]["status"] == "REASSESSMENT_REQUIRED"
    assert reassessed["state"]["active_proposal_id"] is None
    assert reassessed["state"]["client_decision"] == "NONE"
    assert reassessed["state"]["execution_consent_for_proposal_id"] is None


def test_http_advice_gate_requires_explicit_engine_health(client, db_session):
    db_session.add(
        UserRole(
            user_role_id="HAIR-DIALOGUE-HTTP-ENGINE-ROLE",
            subject_id="hair-dialogue-http-journey-user",
            role=ROLE_REVIEWER_QA,
        )
    )
    db_session.commit()
    required = {
        "data_complete": True,
        "safety_passed": True,
        "rule_valid": True,
        "evidence_valid": True,
    }

    omitted = _turn(client, _state(), "EVALUATE_ADVICE_GATE", **required)
    assert omitted.status_code == 422

    explicit_null = _turn(
        client, _state(), "EVALUATE_ADVICE_GATE", **required, engine_ok=None
    )
    assert explicit_null.status_code == 422

    engine_failure = _assert_envelope(
        _turn(
            client, _state(), "EVALUATE_ADVICE_GATE",
            **required, engine_ok=False,
        )
    )
    assert engine_failure["result"] == {
        "advice_allowed": False, "reason_codes": ["ENGINE_FAIL"]
    }
