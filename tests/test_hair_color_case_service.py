"""Integration tests for synthetic-only Hair Color case service."""
import pytest

from app.hair_color.case_store import HairColorCaseStore, StaleCaseVersion, StoppedCase
from app.hair_color.case_service import HairColorCaseService, HairColorCaseServiceError


@pytest.fixture
def service(tmp_path):
    return HairColorCaseService(HairColorCaseStore(tmp_path / "service.sqlite"))


def test_create_update_consult_persian_and_audit_safe_triage(service):
    case = service.create_case(
        case_ref="SYNTHETIC-CASE-001",
        event_id="SYNTHETIC-EVENT-001",
        intake={
            "current_hair_state": "synthetic state",
            "desired_result": "synthetic goal",
            "service_history": "synthetic history",
            "product_context": "synthetic product metadata",
        },
    )
    assert case.case_version == 1
    result = service.consult_persian(
        case_ref=case.case_ref,
        request_id="SYNTHETIC-REQ-001",
        triage_event_id="SYNTHETIC-EVENT-002",
    )
    assert result["consultation"]["options"] == []
    assert result["presentation"]["options"] == []
    assert result["execution_authorized"] is False
    assert result["publication_gate"]["publication_kind"] == "TRIAGE_ONLY"
    audit = service.store.list_events(case.case_ref)[-1]
    assert audit["event_type"] == "TRIAGE_RECORDED"
    assert audit["payload"]["options_count"] == 0
    assert audit["payload"]["execution_authorized"] is False
    assert "synthetic product metadata" not in str(audit["payload"])


def test_update_and_stale_version_rejected(service):
    service.create_case(case_ref="SYNTHETIC-CASE-002", event_id="SYNTHETIC-EVENT-001", intake={"goal": "old"})
    updated = service.update_intake(
        case_ref="SYNTHETIC-CASE-002", event_id="SYNTHETIC-EVENT-002",
        expected_case_version=1, fields={"goal": "new"},
    )
    assert updated.case_version == 2
    with pytest.raises(StaleCaseVersion):
        service.update_intake(
            case_ref="SYNTHETIC-CASE-002", event_id="SYNTHETIC-EVENT-003",
            expected_case_version=1, fields={"goal": "stale"},
        )


def test_target_change_stop_and_fresh_restart(service):
    service.create_case(case_ref="SYNTHETIC-CASE-003", event_id="SYNTHETIC-EVENT-001", intake={"goal": "first"})
    target = service.change_target(case_ref="SYNTHETIC-CASE-003", event_id="SYNTHETIC-EVENT-002", expected_case_version=1)
    assert (target.case_version, target.target_version) == (2, 2)
    stopped = service.stop_case(
        case_ref="SYNTHETIC-CASE-003", event_id="SYNTHETIC-EVENT-003",
        expected_case_version=2, performed_step_refs=("SYNTHETIC-STEP-01",),
    )
    assert stopped.state == "STOPPED"
    with pytest.raises(StoppedCase):
        service.consult_persian(case_ref="SYNTHETIC-CASE-003", request_id="SYNTHETIC-REQ-02", triage_event_id="SYNTHETIC-EVENT-004")
    restarted = service.fresh_restart(
        source_case_ref="SYNTHETIC-CASE-003", new_case_ref="SYNTHETIC-CASE-004",
        event_id="SYNTHETIC-EVENT-005", intake={"goal": "new fresh intake"},
    )
    assert restarted.case_ref == "SYNTHETIC-CASE-004"
    assert restarted.case_version == 1
    assert restarted.target_version == 1


@pytest.mark.parametrize("identifier", ["CASE-REALISH", "", "synthetic-lowercase"])
def test_service_rejects_non_synthetic_identifiers(service, identifier):
    with pytest.raises(HairColorCaseServiceError):
        service.create_case(case_ref=identifier, event_id="SYNTHETIC-EVENT-1", intake={"goal": "synthetic"})


def test_close_case_is_terminal(service):
    service.create_case(case_ref="SYNTHETIC-CASE-005", event_id="SYNTHETIC-EVENT-001", intake={"goal": "synthetic"})
    closed = service.close_case(
        case_ref="SYNTHETIC-CASE-005", event_id="SYNTHETIC-EVENT-002",
        expected_case_version=1, closure_reason="synthetic closure",
    )
    assert closed.state == "CLOSED"
    with pytest.raises(StoppedCase):
        service.consult_persian(case_ref="SYNTHETIC-CASE-005", request_id="SYNTHETIC-REQ-5", triage_event_id="SYNTHETIC-EVENT-3")
