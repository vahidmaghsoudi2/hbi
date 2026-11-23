"""HTTP integration tests for synthetic-only persistent Hair Color case endpoints."""
from app.api.routers.hair_color_cases import get_hair_color_case_service
from app.core.auth import create_access_token
from app.hair_color.case_service import HairColorCaseService
from app.hair_color.case_store import HairColorCaseStore
from app.models.user_role import ROLE_REVIEWER_QA, UserRole


def _headers(subject="hair-color-cases-api-test"):
    token = create_access_token({"sub": subject})
    return {"Authorization": f"Bearer {token}"}


def _grant_role(db_session, subject="hair-color-cases-api-test"):
    db_session.add(UserRole(
        user_role_id="HAIR-COLOR-CASE-API-REVIEWER",
        subject_id=subject,
        role=ROLE_REVIEWER_QA,
    ))
    db_session.commit()


def test_persistent_synthetic_case_api_create_update_stop_restart_and_history(client, db_session, tmp_path):
    _grant_role(db_session)
    service = HairColorCaseService(HairColorCaseStore(tmp_path / "hair-color-api.sqlite"))
    client.app.dependency_overrides[get_hair_color_case_service] = lambda: service
    try:
        created = client.post(
            "/api/v1/hair/color-consultation/cases",
            headers=_headers(),
            json={
                "case_ref": "SYNTHETIC-API-CASE-01",
                "event_id": "SYNTHETIC-API-EVENT-01",
                "intake": {"current_state": "SYNTHETIC: placeholder state"},
            },
        )
        assert created.status_code == 201
        assert created.json()["case_version"] == 1

        updated = client.patch(
            "/api/v1/hair/color-consultation/cases/SYNTHETIC-API-CASE-01/intake",
            headers=_headers(),
            json={
                "event_id": "SYNTHETIC-API-EVENT-02",
                "expected_case_version": 1,
                "fields": {"goal": "SYNTHETIC: placeholder goal"},
            },
        )
        assert updated.status_code == 200
        assert updated.json()["case_version"] == 2

        triage = client.post(
            "/api/v1/hair/color-consultation/cases/SYNTHETIC-API-CASE-01/triage",
            headers=_headers(),
            json={"request_id": "SYNTHETIC-API-REQUEST-01", "triage_event_id": "SYNTHETIC-API-EVENT-TRIAGE-01"},
        )
        assert triage.status_code == 200
        assert triage.json()["consultation"]["consultation_status"] == "NEEDS_INFORMATION_OR_TEST"
        assert "DATA_GAP" in triage.json()["consultation"]["reason_codes"]
        assert triage.json()["consultation"]["missing_information"]
        assert triage.json()["consultation"]["options"] == []
        assert triage.json()["execution_authorized"] is False

        stale = client.patch(
            "/api/v1/hair/color-consultation/cases/SYNTHETIC-API-CASE-01/intake",
            headers=_headers(),
            json={
                "event_id": "SYNTHETIC-API-EVENT-03",
                "expected_case_version": 1,
                "fields": {"goal": "SYNTHETIC: stale write"},
            },
        )
        assert stale.status_code == 409

        stopped = client.post(
            "/api/v1/hair/color-consultation/cases/SYNTHETIC-API-CASE-01/stop",
            headers=_headers(),
            json={"event_id": "SYNTHETIC-API-EVENT-04", "expected_case_version": 2},
        )
        assert stopped.status_code == 200
        assert stopped.json()["state"] == "STOPPED"

        restarted = client.post(
            "/api/v1/hair/color-consultation/cases/SYNTHETIC-API-CASE-01/restart",
            headers=_headers(),
            json={
                "new_case_ref": "SYNTHETIC-API-CASE-02",
                "event_id": "SYNTHETIC-API-EVENT-05",
                "intake": {"goal": "SYNTHETIC: fresh placeholder goal"},
            },
        )
        assert restarted.status_code == 201
        assert restarted.json()["case_ref"] == "SYNTHETIC-API-CASE-02"
        assert restarted.json()["case_version"] == 1
        assert restarted.json()["target_version"] == 1

        history = client.get(
            "/api/v1/hair/color-consultation/cases/SYNTHETIC-API-CASE-01/history",
            headers=_headers(),
        )
        assert history.status_code == 200
        assert [event["event_type"] for event in history.json()] == [
            "CASE_CREATED", "INTAKE_UPDATED", "TRIAGE_RECORDED", "STOP_REQUESTED",
            "FRESH_RESTARTED_AS",
        ]
        assert history.json()[-1]["payload"] == {"new_case_ref": "SYNTHETIC-API-CASE-02"}
    finally:
        client.app.dependency_overrides.pop(get_hair_color_case_service, None)


def test_persistent_synthetic_case_api_rejects_real_ids_and_unmarked_data(client, db_session, tmp_path):
    _grant_role(db_session)
    service = HairColorCaseService(HairColorCaseStore(tmp_path / "hair-color-api-negative.sqlite"))
    client.app.dependency_overrides[get_hair_color_case_service] = lambda: service
    try:
        realish = client.post(
            "/api/v1/hair/color-consultation/cases",
            headers=_headers(),
            json={"case_ref": "REAL-CASE-01", "event_id": "SYNTHETIC-EVENT-01", "intake": {"goal": "SYNTHETIC: test"}},
        )
        assert realish.status_code == 422

        unmarked = client.post(
            "/api/v1/hair/color-consultation/cases",
            headers=_headers(),
            json={"case_ref": "SYNTHETIC-API-CASE-03", "event_id": "SYNTHETIC-EVENT-03", "intake": {"goal": "real-like data"}},
        )
        assert unmarked.status_code == 422
    finally:
        client.app.dependency_overrides.pop(get_hair_color_case_service, None)


def test_persistent_synthetic_case_api_role_required(client, db_session, tmp_path):
    service = HairColorCaseService(HairColorCaseStore(tmp_path / "hair-color-api-auth.sqlite"))
    client.app.dependency_overrides[get_hair_color_case_service] = lambda: service
    try:
        denied = client.post(
            "/api/v1/hair/color-consultation/cases",
            headers=_headers("hair-color-case-api-no-role"),
            json={"case_ref": "SYNTHETIC-CASE-01", "event_id": "SYNTHETIC-EVENT-01", "intake": {}},
        )
        assert denied.status_code == 403
    finally:
        client.app.dependency_overrides.pop(get_hair_color_case_service, None)


def test_persistent_client_accept_and_reject_are_audited_without_execution_authority(client, db_session, tmp_path):
    _grant_role(db_session)
    service = HairColorCaseService(HairColorCaseStore(tmp_path / "hair-color-decisions.sqlite"))
    client.app.dependency_overrides[get_hair_color_case_service] = lambda: service
    try:
        created = client.post(
            "/api/v1/hair/color-consultation/cases",
            headers=_headers(),
            json={"case_ref": "SYNTHETIC-DECISION-CASE", "event_id": "SYNTHETIC-DECISION-CREATE",
                  "intake": {"goal": "SYNTHETIC: placeholder"}},
        )
        assert created.status_code == 201
        accepted = client.post(
            "/api/v1/hair/color-consultation/cases/SYNTHETIC-DECISION-CASE/decision",
            headers=_headers(),
            json={"event_id": "SYNTHETIC-DECISION-ACCEPT", "expected_case_version": 1,
                  "expected_target_version": 1, "decision": "ACCEPT",
                  "suggestion_ref": "SYNTHETIC-SUGGESTION-1"},
        )
        assert accepted.status_code == 200
        assert accepted.json()["execution_authorized"] is False
        rejected = client.post(
            "/api/v1/hair/color-consultation/cases/SYNTHETIC-DECISION-CASE/decision",
            headers=_headers(),
            json={"event_id": "SYNTHETIC-DECISION-REJECT", "expected_case_version": 1,
                  "expected_target_version": 1, "decision": "REJECT",
                  "suggestion_ref": "SYNTHETIC-SUGGESTION-2",
                  "reason": "SYNTHETIC: placeholder rejection reason"},
        )
        assert rejected.status_code == 200
        history = client.get(
            "/api/v1/hair/color-consultation/cases/SYNTHETIC-DECISION-CASE/history",
            headers=_headers(),
        )
        assert history.status_code == 200
        events = history.json()
        assert [event["event_type"] for event in events] == [
            "CASE_CREATED", "CLIENT_ACCEPTED", "CLIENT_REJECTED",
        ]
        assert events[1]["payload"]["client_acceptance"] is True
        assert events[1]["payload"]["execution_authorized"] is False
        assert events[2]["payload"]["decision"] == "REJECT"

        reactivated = client.post(
            "/api/v1/hair/color-consultation/cases/SYNTHETIC-DECISION-CASE/decision",
            headers=_headers(),
            json={"event_id": "SYNTHETIC-DECISION-REACTIVATE", "expected_case_version": 1,
                  "expected_target_version": 1, "decision": "ACCEPT",
                  "suggestion_ref": "SYNTHETIC-SUGGESTION-2"},
        )
        assert reactivated.status_code == 422
    finally:
        client.app.dependency_overrides.pop(get_hair_color_case_service, None)


def test_client_decision_rejects_stale_version_and_invalid_decision(client, db_session, tmp_path):
    _grant_role(db_session)
    service = HairColorCaseService(HairColorCaseStore(tmp_path / "hair-color-decisions-negative.sqlite"))
    client.app.dependency_overrides[get_hair_color_case_service] = lambda: service
    try:
        client.post(
            "/api/v1/hair/color-consultation/cases",
            headers=_headers(),
            json={"case_ref": "SYNTHETIC-DECISION-STALE", "event_id": "SYNTHETIC-DECISION-STALE-CREATE",
                  "intake": {"goal": "SYNTHETIC: placeholder"}},
        )
        stale = client.post(
            "/api/v1/hair/color-consultation/cases/SYNTHETIC-DECISION-STALE/decision",
            headers=_headers(),
            json={"event_id": "SYNTHETIC-DECISION-STALE-EVENT", "expected_case_version": 2,
                  "expected_target_version": 1, "decision": "ACCEPT",
                  "suggestion_ref": "SYNTHETIC-SUGGESTION-1"},
        )
        assert stale.status_code == 409
        invalid = client.post(
            "/api/v1/hair/color-consultation/cases/SYNTHETIC-DECISION-STALE/decision",
            headers=_headers(),
            json={"event_id": "SYNTHETIC-DECISION-INVALID", "expected_case_version": 1,
                  "expected_target_version": 1, "decision": "EXECUTE",
                  "suggestion_ref": "SYNTHETIC-SUGGESTION-1"},
        )
        assert invalid.status_code == 422
    finally:
        client.app.dependency_overrides.pop(get_hair_color_case_service, None)


def test_target_change_versions_case_and_invalidates_old_decision_context(client, db_session, tmp_path):
    _grant_role(db_session)
    service = HairColorCaseService(HairColorCaseStore(tmp_path / "hair-color-target-change.sqlite"))
    client.app.dependency_overrides[get_hair_color_case_service] = lambda: service
    try:
        created = client.post(
            "/api/v1/hair/color-consultation/cases",
            headers=_headers(),
            json={"case_ref": "SYNTHETIC-TARGET-CASE", "event_id": "SYNTHETIC-TARGET-CREATE",
                  "intake": {"goal": "SYNTHETIC: initial target"}},
        )
        assert created.status_code == 201
        changed = client.post(
            "/api/v1/hair/color-consultation/cases/SYNTHETIC-TARGET-CASE/target-change",
            headers=_headers(),
            json={"event_id": "SYNTHETIC-TARGET-CHANGE", "expected_case_version": 1,
                  "target_description": "SYNTHETIC: revised target placeholder"},
        )
        assert changed.status_code == 200
        assert changed.json()["case_version"] == 2
        assert changed.json()["target_version"] == 2
        assert changed.json()["intake"]["goal"] == "SYNTHETIC: initial target"
        assert changed.json()["intake"]["desired_result"] == "SYNTHETIC: revised target placeholder"
        stale_decision = client.post(
            "/api/v1/hair/color-consultation/cases/SYNTHETIC-TARGET-CASE/decision",
            headers=_headers(),
            json={"event_id": "SYNTHETIC-TARGET-STALE-DECISION", "expected_case_version": 1,
                  "expected_target_version": 1, "decision": "ACCEPT",
                  "suggestion_ref": "SYNTHETIC-OLD-SUGGESTION"},
        )
        assert stale_decision.status_code == 409
        history = client.get(
            "/api/v1/hair/color-consultation/cases/SYNTHETIC-TARGET-CASE/history",
            headers=_headers(),
        )
        assert [event["event_type"] for event in history.json()] == ["CASE_CREATED", "TARGET_CHANGED"]
        assert history.json()[1]["payload"]["previous_target"] is None
        assert history.json()[1]["payload"]["new_target"] == "SYNTHETIC: revised target placeholder"
    finally:
        client.app.dependency_overrides.pop(get_hair_color_case_service, None)


def test_complete_intake_still_fails_closed_without_approved_specialist_knowledge(client, db_session, tmp_path):
    _grant_role(db_session)
    service = HairColorCaseService(HairColorCaseStore(tmp_path / "hair-color-complete-intake.sqlite"))
    client.app.dependency_overrides[get_hair_color_case_service] = lambda: service
    try:
        created = client.post(
            "/api/v1/hair/color-consultation/cases",
            headers=_headers(),
            json={
                "case_ref": "SYNTHETIC-COMPLETE-CASE",
                "event_id": "SYNTHETIC-COMPLETE-CREATE",
                "intake": {
                    "current_hair_state": "SYNTHETIC: placeholder current state",
                    "desired_result": "SYNTHETIC: placeholder desired result",
                    "service_history": "SYNTHETIC: placeholder service history",
                    "product_context": "SYNTHETIC: placeholder product context",
                },
            },
        )
        assert created.status_code == 201
        triage = client.post(
            "/api/v1/hair/color-consultation/cases/SYNTHETIC-COMPLETE-CASE/triage",
            headers=_headers(),
            json={
                "request_id": "SYNTHETIC-COMPLETE-REQUEST",
                "triage_event_id": "SYNTHETIC-COMPLETE-TRIAGE",
            },
        )
        assert triage.status_code == 200
        consultation = triage.json()["consultation"]
        assert consultation["consultation_status"] == "NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW"
        assert "KNOWLEDGE_GAP" in consultation["reason_codes"]
        assert consultation["options"] == []
        assert triage.json()["execution_authorized"] is False
    finally:
        client.app.dependency_overrides.pop(get_hair_color_case_service, None)
