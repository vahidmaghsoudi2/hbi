"""HTTP-level conformance for the stateless, synthetic Hair dialogue runtime."""
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



def _assert_non_publishing_envelope(body):
    assert body["recommendation"] is None
    assert body["display_allowed"] is False
    assert body["client_visible"] is False
    assert body["persistence"] == "COMPUTED_ONLY"


def test_dialogue_runtime_requires_internal_role(client, db_session):
    response = client.post(
        "/api/v1/hair/dialogue/turn",
        json={"action": "ANSWER_QUESTION", "state": _state(), "question_code": "STATUS_REASON", "answer_code": "STATUS_REASON"},
        headers=_headers(),
    )
    assert response.status_code == 403


def test_sequential_questions_preserve_versions_decisions_and_non_persistence(client, db_session):
    _grant_reviewer_qa(db_session)
    state = _state()
    first = _turn(client, state, "ANSWER_QUESTION", question_code="STATUS_REASON", answer_code="STATUS_REASON")
    assert first.status_code == 200
    second = _turn(client, first.json()["state"], "ANSWER_QUESTION", question_code="MISSING_DATA", answer_code="MISSING_DATA")
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


def test_unavailable_engine_preempts_required_data_gate(client, db_session):
    _grant_reviewer_qa(db_session)
    resolved = _turn(
        client, _state(), "RESOLVE_REQUIRED_DATA",
        recorded_fields=["brand"],
        required_fields=["brand", "history", "hair_history"],
    )
    assert resolved.status_code == 200
    assert resolved.json()["result"]["known_fields"] == ["brand"]
    assert "known_values" not in resolved.json()["result"]
    assert "SYNTHETIC_FIXTURE_VALUE" not in resolved.text
    assert resolved.json()["result"]["missing_fields"] == ["history", "hair_history"]
    gate = _turn(
        client, _state(), "EVALUATE_ADVICE_GATE",
    )
    assert gate.status_code == 200
    assert gate.json()["result"] == {"advice_allowed": False, "reason_codes": ["ENGINE_FAIL"]}


def test_runtime_rejects_real_case_ids_and_unrecognized_request_fields(client, db_session):
    _grant_reviewer_qa(db_session)
    real_case = _turn(client, _state(case_id="REAL-CLIENT-001"), "ANSWER_QUESTION",
                      question_code="STATUS_REASON", answer_code="STATUS_REASON")
    assert real_case.status_code == 422
    malformed = _turn(client, _state(), "ANSWER_QUESTION",
                      question_code="STATUS_REASON", answer_code="STATUS_REASON", customer_id="must-not-be-accepted")
    assert malformed.status_code == 422


def test_engine_failure_has_priority_and_never_allows_advice(client, db_session):
    _grant_reviewer_qa(db_session)
    response = _turn(
        client, _state(), "EVALUATE_ADVICE_GATE",
    )
    assert response.status_code == 200
    assert response.json()["result"] == {"advice_allowed": False, "reason_codes": ["ENGINE_FAIL"]}
    assert response.json()["recommendation"] is None


def test_multiturn_http_flow_keeps_acceptance_consent_and_goal_version_separate(client, db_session):
    _grant_reviewer_qa(db_session)
    state = _state()
    proposal_id = "SYNTHETIC-PROPOSAL-MULTITURN-001"

    attached = _turn(client, state, "ATTACH_PROPOSAL", proposal_id=proposal_id)
    assert attached.status_code == 200
    _assert_non_publishing_envelope(attached.json())
    state = attached.json()["state"]

    question = _turn(
        client, state, "ANSWER_QUESTION",
        question_code="STATUS_REASON", answer_code="STATUS_REASON",
    )
    assert question.status_code == 200
    _assert_non_publishing_envelope(question.json())
    state = question.json()["state"]
    assert state["client_decision"] == "NONE"
    assert state["execution_consent_for_proposal_id"] is None

    accepted = _turn(client, state, "ACCEPT_PROPOSAL", proposal_id=proposal_id)
    assert accepted.status_code == 200
    _assert_non_publishing_envelope(accepted.json())
    state = accepted.json()["state"]
    assert state["client_decision"] == "ACCEPTED"
    assert state["execution_consent_for_proposal_id"] is None

    consent = _turn(
        client, state, "RECORD_EXECUTION_CONSENT",
        proposal_id=proposal_id, explicit_consent=True,
    )
    assert consent.status_code == 200
    _assert_non_publishing_envelope(consent.json())
    state = consent.json()["state"]
    assert state["execution_consent_for_proposal_id"] == proposal_id

    # A later question is informational: it must preserve both independent decisions.
    follow_up = _turn(
        client, state, "ANSWER_QUESTION",
        question_code="PROCESS_LIMIT", answer_code="PROCESS_LIMIT",
    )
    assert follow_up.status_code == 200
    _assert_non_publishing_envelope(follow_up.json())
    state = follow_up.json()["state"]
    assert state["client_decision"] == "ACCEPTED"
    assert state["execution_consent_for_proposal_id"] == proposal_id

    changed = _turn(client, state, "CHANGE_GOAL", new_goal_version="goal-v2")
    assert changed.status_code == 200
    body = changed.json()
    _assert_non_publishing_envelope(body)
    assert body["state"]["goal_version"] == "goal-v2"
    assert body["state"]["active_proposal_id"] is None
    assert body["state"]["client_decision"] == "NONE"
    assert body["state"]["execution_consent_for_proposal_id"] is None


def test_http_rejects_malformed_proposal_references_inside_supplied_state(client, db_session):
    _grant_reviewer_qa(db_session)
    invalid_states = [
        _state(case_id="SYNTHETIC-CASE WITH SPACE"),
        _state(case_id="SYNTHETIC-CASE/REAL"),
        _state(case_version=""),
        _state(case_version=" case-v1"),
        _state(goal_version=""),
        _state(goal_version="goal-v1 "),
        _state(active_proposal_id=""),
        _state(rejected_proposal_ids=["SYNTHETIC-OK", "REAL-PROPOSAL"]),
        _state(rejected_proposal_ids=["SYNTHETIC-"]),
        _state(
            active_proposal_id="SYNTHETIC-PROPOSAL-1",
            active_proposal_case_version="case-v1",
            active_proposal_goal_version="goal-v1",
            client_decision="ACCEPTED",
            execution_consent_for_proposal_id="REAL-PROPOSAL",
        ),
        _state(
            active_proposal_id=None,
            active_proposal_case_version=None,
            active_proposal_goal_version=None,
            client_decision="ACCEPTED",
        ),
        _state(
            active_proposal_id="SYNTHETIC-PROPOSAL-1",
            active_proposal_case_version="stale-case",
        ),
    ]
    for malformed_state in invalid_states:
        response = _turn(
            client, malformed_state, "ANSWER_QUESTION",
            question_code="STATUS_REASON", answer_code="STATUS_REASON",
        )
        assert response.status_code == 422


def test_http_rejects_invalid_request_proposal_id_for_every_lifecycle_action(client, db_session):
    _grant_reviewer_qa(db_session)
    valid_active = _state(
        active_proposal_id="SYNTHETIC-PROPOSAL-1",
        active_proposal_case_version="case-v1",
        active_proposal_goal_version="goal-v1",
        client_decision="ACCEPTED",
    )
    valid_empty = _state()
    cases = [
        ("ATTACH_PROPOSAL", valid_empty),
        ("ACCEPT_PROPOSAL", valid_active),
        ("REJECT_PROPOSAL", valid_active),
        ("RECORD_EXECUTION_CONSENT", valid_active),
    ]
    for action, state in cases:
        for proposal_id in ["", " ", "SYNTHETIC-", " SYNTHETIC-X", "SYNTHETIC-X ", "REAL-X"]:
            response = _turn(
                client, state, action, proposal_id=proposal_id,
                explicit_consent=True,
            )
            assert response.status_code == 422


def test_http_rejects_missing_request_proposal_id_for_lifecycle_actions(client, db_session):
    _grant_reviewer_qa(db_session)
    for action in ["ATTACH_PROPOSAL", "ACCEPT_PROPOSAL", "REJECT_PROPOSAL",
                   "RECORD_EXECUTION_CONSENT"]:
        response = _turn(client, _state(), action, explicit_consent=True)
        assert response.status_code == 422


def test_valid_synthetic_state_preserves_non_publishing_envelope_after_new_guards(client, db_session):
    _grant_reviewer_qa(db_session)
    response = _turn(
        client,
        _state(active_proposal_id="SYNTHETIC-PROPOSAL-VALID",
               active_proposal_case_version="case-v1",
               active_proposal_goal_version="goal-v1"),
        "ANSWER_QUESTION",
        question_code="STATUS_REASON",
        answer_code="STATUS_REASON",
    )
    assert response.status_code == 200
    _assert_non_publishing_envelope(response.json())

def test_http_rejects_padded_or_empty_recorded_field_identifiers(client, db_session):
    _grant_reviewer_qa(db_session)
    for recorded_fields in [[" brand"], ["brand "], [""], [" "]]:
        response = _turn(
            client,
            _state(),
            "RESOLVE_REQUIRED_DATA",
            recorded_fields=recorded_fields,
            required_fields=["brand"],
        )
        assert response.status_code == 422


def test_http_rejects_padded_goal_version_identifiers(client, db_session):
    _grant_reviewer_qa(db_session)
    for new_goal_version in [" goal-v2", "goal-v2 "]:
        response = _turn(
            client,
            _state(),
            "CHANGE_GOAL",
            new_goal_version=new_goal_version,
        )
        assert response.status_code == 422

def test_http_required_data_resolution_rejects_missing_or_empty_required_fields(client, db_session):
    _grant_reviewer_qa(db_session)
    for required_fields in [None, []]:
        response = _turn(
            client,
            _state(),
            "RESOLVE_REQUIRED_DATA",
            recorded_fields=["brand"],
            required_fields=required_fields,
        )
        assert response.status_code == 422



def test_http_rejects_type_coercion_for_boolean_contract_fields(client, db_session):
    _grant_reviewer_qa(db_session)
    malformed_values = ["true", "false", "1", "0", 1, 0]
    for field in [
        "explicit_consent",
        "explicit_consent",
    ]:
        for value in malformed_values:
            response = _turn(
                client,
                _state(),
                "ANSWER_QUESTION",
                question_code="STATUS_REASON",
                answer_code="STATUS_REASON",
                **{field: value},
            )
            assert response.status_code == 422, (field, value, response.text)


def test_http_rejects_non_string_state_identifiers_without_coercion(client, db_session):
    _grant_reviewer_qa(db_session)
    for field in ["case_id", "case_version", "goal_version", "active_proposal_id"]:
        response = _turn(
            client,
            _state(**{field: 123}),
            "ANSWER_QUESTION",
            question_code="STATUS_REASON",
            answer_code="STATUS_REASON",
        )
        assert response.status_code == 422, (field, response.text)


def test_every_successful_http_action_preserves_non_publishing_envelope(client, db_session):
    _grant_reviewer_qa(db_session)
    active = _state(
        active_proposal_id="SYNTHETIC-PROPOSAL-ENVELOPE-1",
        active_proposal_case_version="case-v1",
        active_proposal_goal_version="goal-v1",
    )
    accepted = _state(
        active_proposal_id="SYNTHETIC-PROPOSAL-ENVELOPE-1",
        active_proposal_case_version="case-v1",
        active_proposal_goal_version="goal-v1",
        client_decision="ACCEPTED",
    )
    actions = [
        ("ANSWER_QUESTION", _state(), {
            "question_code": "STATUS_REASON", "answer_code": "STATUS_REASON",
        }),
        ("EXPLAIN_REASON", _state(), {"reason_code": "DATA_GAP"}),
        ("RESOLVE_REQUIRED_DATA", _state(), {
            "recorded_fields": ["brand"], "required_fields": ["brand", "history"],
        }),
        ("EVALUATE_ADVICE_GATE", _state(), {}),
        ("ATTACH_PROPOSAL", _state(), {
            "proposal_id": "SYNTHETIC-PROPOSAL-ENVELOPE-1",
        }),
        ("ACCEPT_PROPOSAL", active, {
            "proposal_id": "SYNTHETIC-PROPOSAL-ENVELOPE-1",
        }),
        ("REJECT_PROPOSAL", active, {
            "proposal_id": "SYNTHETIC-PROPOSAL-ENVELOPE-1",
        }),
        ("RECORD_EXECUTION_CONSENT", accepted, {
            "proposal_id": "SYNTHETIC-PROPOSAL-ENVELOPE-1",
            "explicit_consent": True,
        }),
        ("CHANGE_GOAL", _state(), {"new_goal_version": "goal-v2"}),
        ("REASSESS_DEPENDENCIES", _state(), {"invalidation_status": "INVALIDATE"}),
    ]

    for action, state, fields in actions:
        response = _turn(client, state, action, **fields)
        assert response.status_code == 200, (action, response.text)
        _assert_non_publishing_envelope(response.json())


def test_http_dependency_reassessment_cannot_caller_assert_preservation(client, db_session):
    _grant_reviewer_qa(db_session)
    consented = _state(
        active_proposal_id="SYNTHETIC-PROPOSAL-REASSESS-1",
        active_proposal_case_version="case-v1",
        active_proposal_goal_version="goal-v1",
        client_decision="ACCEPTED",
        execution_consent_for_proposal_id="SYNTHETIC-PROPOSAL-REASSESS-1",
    )

    # PRESERVE is not an HTTP option: the request cannot prove dependencies are unchanged.
    preserved = _turn(
        client, consented, "REASSESS_DEPENDENCIES",
        invalidation_status="PRESERVE",
    )
    assert preserved.status_code == 422

    missing = _turn(client, consented, "REASSESS_DEPENDENCIES")
    assert missing.status_code == 422

    for status, expected in [
        ("INVALIDATE", "INVALIDATED"),
        ("UNRESOLVED", "REASSESSMENT_REQUIRED"),
    ]:
        response = _turn(
            client, consented, "REASSESS_DEPENDENCIES",
            invalidation_status=status,
        )
        assert response.status_code == 200, (status, response.text)
        _assert_non_publishing_envelope(response.json())
        assert response.json()["result"]["status"] == expected
        assert response.json()["state"]["active_proposal_id"] is None
        assert response.json()["state"]["client_decision"] == "NONE"
        assert response.json()["state"]["execution_consent_for_proposal_id"] is None

    for invalid_value in ["PRESERVE", "UNRECOGNIZED_IMPACT", "INVALIDATE ", 123, True, []]:
        malformed = _turn(
            client, consented, "REASSESS_DEPENDENCIES",
            invalidation_status=invalid_value,
        )
        assert malformed.status_code == 422, (invalid_value, malformed.text)

def _headers_for_claims(claims):
    token = create_access_token(claims)
    return {"Authorization": f"Bearer {token}"}


def test_hair_dialogue_rejects_missing_or_noncanonical_actor_identity(client, db_session):
    from app.models.user_role import ROLE_REVIEWER_QA, UserRole

    # Even a mistakenly provisioned blank/whitespace subject must not authorize a caller.
    for index, subject_id in enumerate(["", " ", "  actor  "]):
        db_session.add(UserRole(
            user_role_id=f"HAIR-DIALOGUE-BLANK-ACTOR-{index}",
            subject_id=subject_id,
            role=ROLE_REVIEWER_QA,
        ))
    db_session.commit()

    cases = [
        ({}, 401),
        ({"sub": ""}, 401),
        ({"sub": " "}, 401),
        ({"sub": "  actor  "}, 401),
        ({"sub": 12345}, 401),
    ]
    for claims, expected_status in cases:
        response = client.post(
            "/api/v1/hair/dialogue/turn",
            json={
                "action": "ANSWER_QUESTION",
                "state": _state(),
                "question_code": "STATUS_REASON",
                "answer_code": "STATUS_REASON",
            },
            headers=_headers_for_claims(claims),
        )
        assert response.status_code == expected_status, (claims, response.text)

    unauthenticated = client.post(
        "/api/v1/hair/dialogue/turn",
        json={"action": "ANSWER_QUESTION", "state": _state()},
    )
    assert unauthenticated.status_code == 401


def test_hair_dialogue_accepts_only_exact_internal_role_values(client, db_session):
    from app.models.user_role import ROLE_ADMIN, ROLE_PO, ROLE_REVIEWER_QA, UserRole

    allowed = [ROLE_REVIEWER_QA, ROLE_PO, ROLE_ADMIN]
    for index, role in enumerate(allowed):
        subject_id = f"hair-dialogue-canonical-role-{index}"
        db_session.add(UserRole(
            user_role_id=f"HAIR-DIALOGUE-CANONICAL-ROLE-{index}",
            subject_id=subject_id,
            role=role,
        ))
    db_session.commit()

    for index, role in enumerate(allowed):
        subject_id = f"hair-dialogue-canonical-role-{index}"
        response = client.post(
            "/api/v1/hair/dialogue/turn",
            json={
                "action": "ANSWER_QUESTION",
                "state": _state(),
                "question_code": "STATUS_REASON",
                "answer_code": "STATUS_REASON",
            },
            headers=_headers_for_claims({"sub": subject_id}),
        )
        assert response.status_code == 200, (role, response.text)
        _assert_non_publishing_envelope(response.json())

    denied_roles = ["reviewer/qa", "reviewer_qa", "REVIEWER/QA", "Reviewer/QA ", "Editor"]
    for index, role in enumerate(denied_roles):
        subject_id = f"hair-dialogue-noncanonical-role-{index}"
        db_session.add(UserRole(
            user_role_id=f"HAIR-DIALOGUE-NONCANONICAL-ROLE-{index}",
            subject_id=subject_id,
            role=role,
        ))
    db_session.commit()

    for index, role in enumerate(denied_roles):
        subject_id = f"hair-dialogue-noncanonical-role-{index}"
        response = client.post(
            "/api/v1/hair/dialogue/turn",
            json={
                "action": "ANSWER_QUESTION",
                "state": _state(),
                "question_code": "STATUS_REASON",
                "answer_code": "STATUS_REASON",
            },
            headers=_headers_for_claims({"sub": subject_id}),
        )
        assert response.status_code == 403, (role, response.text)


def test_hair_dialogue_rejects_client_supplied_identity_or_role_claims(client, db_session):
    _grant_reviewer_qa(db_session)
    for field, value in [
        ("role", "Admin"),
        ("roles", ["Admin"]),
        ("actor_id", "another-user"),
        ("subject_id", "another-user"),
        ("is_admin", True),
    ]:
        response = _turn(
            client,
            _state(),
            "ANSWER_QUESTION",
            question_code="STATUS_REASON",
            answer_code="STATUS_REASON",
            **{field: value},
        )
        assert response.status_code == 422, (field, response.text)


def test_hair_dialogue_runtime_has_no_alternate_http_method_entrypoint(client):
    path = "/api/v1/hair/dialogue/turn"
    for method in ["GET", "PUT", "PATCH", "DELETE"]:
        response = client.request(method, path)
        assert response.status_code == 405, (method, response.text)

def test_http_rejects_action_irrelevant_fields_instead_of_silently_ignoring_them(client, db_session):
    _grant_reviewer_qa(db_session)
    cases = [
        ("ANSWER_QUESTION", {"question_code": "STATUS_REASON", "answer_code": "STATUS_REASON", "proposal_id": "SYNTHETIC-UNRELATED"}),
        ("EXPLAIN_REASON", {"reason_code": "DATA_GAP", "explicit_consent": True}),
        ("RESOLVE_REQUIRED_DATA", {"recorded_fields": ["brand"], "required_fields": ["brand"], "new_goal_version": "goal-v2"}),
        ("EVALUATE_ADVICE_GATE", {"data_complete": True, "safety_passed": True, "rule_valid": True, "evidence_valid": True, "invalidation_status": "INVALIDATE"}),
        ("ATTACH_PROPOSAL", {"proposal_id": "SYNTHETIC-UNRELATED", "explicit_consent": True}),
        ("ACCEPT_PROPOSAL", {"proposal_id": "SYNTHETIC-UNRELATED", "question_code": "STATUS_REASON"}),
        ("REJECT_PROPOSAL", {"proposal_id": "SYNTHETIC-UNRELATED", "new_goal_version": "goal-v2"}),
        ("RECORD_EXECUTION_CONSENT", {"proposal_id": "SYNTHETIC-UNRELATED", "explicit_consent": True, "reason_code": "DATA_GAP"}),
        ("CHANGE_GOAL", {"new_goal_version": "goal-v2", "answer_code": "STATUS_REASON"}),
        ("REASSESS_DEPENDENCIES", {"invalidation_status": "INVALIDATE", "proposal_id": "SYNTHETIC-UNRELATED"}),
    ]
    for action, fields in cases:
        response = _turn(client, _state(), action, **fields)
        assert response.status_code == 422, (action, response.text)


def test_http_reason_explanations_are_client_safe_and_explicit(client, db_session):
    _grant_reviewer_qa(db_session)
    expected = {
        "CATALOG_ONLY": "این خروجی فقط زمینهٔ هویت کاتالوگی مصنوعی را پوشش می‌دهد.",
        "DATA_GAP": "دادهٔ ضروری کافی نیست؛ نتیجهٔ قطعی ارائه نمی‌شود.",
        "KNOWLEDGE_GAP": "شاهد یا قاعدهٔ معتبر کافی نیست؛ حدس زده نمی‌شود.",
        "SAFETY_STOP": "شرط ایمنی تأیید نشده است؛ مسیر متوقف می‌ماند.",
    }
    for reason_code, summary in expected.items():
        response = _turn(client, _state(), "EXPLAIN_REASON", reason_code=reason_code)
        assert response.status_code == 200, (reason_code, response.text)
        body = response.json()
        _assert_non_publishing_envelope(body)
        assert body["result"] == {"summary_fa": summary}

    invalid = _turn(client, _state(), "EXPLAIN_REASON", reason_code="ENGINE_FAIL")
    assert invalid.status_code == 422


def test_http_unavailable_engine_preempts_missing_evidence(client, db_session):
    _grant_reviewer_qa(db_session)
    response = _turn(
        client,
        _state(),
        "EVALUATE_ADVICE_GATE",

    )
    assert response.status_code == 200
    body = response.json()
    _assert_non_publishing_envelope(body)
    assert body["result"] == {
        "advice_allowed": False,
        "reason_codes": ["ENGINE_FAIL"],
    }
    assert body["recommendation"] is None
