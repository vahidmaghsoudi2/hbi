"""Tests for durable versioned Hair Color case intake storage."""
import pytest

from app.hair_color.case_store import (
    CaseNotFound,
    CaseStoreError,
    HairColorCaseStore,
    StaleCaseVersion,
    StoppedCase,
)


@pytest.fixture
def store(tmp_path):
    return HairColorCaseStore(tmp_path / "hair-color.sqlite3")


def test_create_persists_case_and_audit_event(store):
    created = store.create_case(
        case_ref="CASE-A", event_id="EV-A",
        intake={"goal": "synthetic goal", "history": "synthetic history"},
    )
    assert created.case_version == 1
    assert created.target_version == 1
    assert created.state == "ACTIVE"
    assert store.list_events("CASE-A")[0]["event_type"] == "CASE_CREATED"


def test_case_snapshot_survives_store_reconstruction(tmp_path):
    path = tmp_path / "persistent.sqlite3"
    first = HairColorCaseStore(path)
    first.create_case(case_ref="CASE-P", event_id="EV-P", intake={"goal": "test"})
    reopened = HairColorCaseStore(path)
    assert reopened.get_case("CASE-P").intake == {"goal": "test"}


def test_update_is_versioned_and_records_only_field_names(store):
    store.create_case(case_ref="CASE-U", event_id="EV-1", intake={"goal": "old"})
    updated = store.update_intake(
        case_ref="CASE-U", event_id="EV-2", expected_case_version=1,
        fields={"goal": "new", "history": "added"},
    )
    assert updated.case_version == 2
    assert updated.intake == {"goal": "new", "history": "added"}
    events = store.list_events("CASE-U")
    assert events[-1]["payload"] == {"changed_fields": ["goal", "history"]}
    assert "new" not in str(events[-1]["payload"])


def test_stale_write_rejected_without_mutation(store):
    store.create_case(case_ref="CASE-S", event_id="EV-1", intake={"goal": "a"})
    store.update_intake(case_ref="CASE-S", event_id="EV-2", expected_case_version=1, fields={"goal": "b"})
    with pytest.raises(StaleCaseVersion):
        store.update_intake(case_ref="CASE-S", event_id="EV-3", expected_case_version=1, fields={"goal": "c"})
    assert store.get_case("CASE-S").intake["goal"] == "b"


def test_duplicate_event_id_rejected_and_transaction_rolled_back(store):
    store.create_case(case_ref="CASE-D", event_id="EV-1", intake={"goal": "a"})
    with pytest.raises(CaseStoreError, match="event_id"):
        store.update_intake(case_ref="CASE-D", event_id="EV-1", expected_case_version=1, fields={"goal": "b"})
    snapshot = store.get_case("CASE-D")
    assert snapshot.case_version == 1
    assert snapshot.intake["goal"] == "a"


def test_target_change_increments_both_versions(store):
    store.create_case(case_ref="CASE-T", event_id="EV-1", intake={"goal": "a"})
    changed = store.change_target(case_ref="CASE-T", event_id="EV-2", expected_case_version=1, target_description="revised target")
    assert (changed.case_version, changed.target_version) == (2, 2)
    assert store.list_events("CASE-T")[-1]["event_type"] == "TARGET_CHANGED"


def test_stop_is_a_terminal_record_for_updates_and_no_auto_resume(store):
    store.create_case(case_ref="CASE-STOP", event_id="EV-1", intake={"goal": "a"})
    stopped = store.stop_case(
        case_ref="CASE-STOP", event_id="EV-2", expected_case_version=1,
        performed_step_refs=("step-a", "step-a", " "),
    )
    assert stopped.state == "STOPPED"
    assert stopped.case_version == 2
    assert store.list_events("CASE-STOP")[-1]["case_version"] == 2
    assert store.list_events("CASE-STOP")[-1]["payload"] == {"performed_step_refs": ["step-a"]}
    with pytest.raises(StoppedCase):
        store.update_intake(case_ref="CASE-STOP", event_id="EV-3", expected_case_version=1, fields={"goal": "b"})


def test_fresh_restart_requires_stopped_source_case(store):
    store.create_case(case_ref="CASE-ACTIVE", event_id="EV-A", intake={"goal": "x"})
    with pytest.raises(StoppedCase, match="stopped source"):
        store.fresh_restart(source_case_ref="CASE-ACTIVE", new_case_ref="CASE-B", event_id="EV-B", intake={"goal": "y"})


def test_fresh_restart_creates_new_case_and_links_source(store):
    store.create_case(case_ref="CASE-OLD", event_id="EV-1", intake={"goal": "old"})
    store.stop_case(case_ref="CASE-OLD", event_id="EV-2", expected_case_version=1)
    new = store.fresh_restart(
        source_case_ref="CASE-OLD", new_case_ref="CASE-NEW", event_id="EV-3",
        intake={"goal": "new"},
    )
    assert new.case_ref == "CASE-NEW"
    assert new.case_version == 1
    new_events = store.list_events("CASE-NEW")
    assert [event["event_type"] for event in new_events] == ["CASE_CREATED", "FRESH_RESTART_FROM_STOP"]
    assert new_events[-1]["payload"] == {"source_case_ref": "CASE-OLD"}
    source_events = store.list_events("CASE-OLD")
    assert source_events[-1]["event_type"] == "FRESH_RESTARTED_AS"
    assert source_events[-1]["payload"] == {"new_case_ref": "CASE-NEW"}
    assert store.get_case("CASE-OLD").updated_event_id == source_events[-1]["event_id"]


def test_triage_event_requires_current_versions_and_unique_reasons(store):
    store.create_case(case_ref="CASE-TRIAGE", event_id="EV-1", intake={"goal": "synthetic"})
    store.record_triage(
        case_ref="CASE-TRIAGE", event_id="EV-2", expected_case_version=1,
        expected_target_version=1, request_id="REQ-1", consultation_status="NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW",
        reason_codes=("KNOWLEDGE_GAP",), safe_summary="synthetic safe summary",
    )
    with pytest.raises(CaseStoreError, match="unique"):
        store.record_triage(
            case_ref="CASE-TRIAGE", event_id="EV-3", expected_case_version=1,
            expected_target_version=1, request_id="REQ-2", consultation_status="NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW",
            reason_codes=("DATA_GAP", "DATA_GAP"), safe_summary="summary",
        )
    with pytest.raises(StaleCaseVersion):
        store.record_triage(
            case_ref="CASE-TRIAGE", event_id="EV-4", expected_case_version=2,
            expected_target_version=1, request_id="REQ-3", consultation_status="NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW",
            reason_codes=(), safe_summary="summary",
        )


def test_close_case_records_terminal_state_and_blocks_updates(store):
    store.create_case(case_ref="CASE-CLOSE", event_id="EV-1", intake={"goal": "a"})
    closed = store.close_case(
        case_ref="CASE-CLOSE", event_id="EV-2", expected_case_version=1,
        closure_reason="synthetic completion",
    )
    assert closed.state == "CLOSED"
    assert closed.case_version == 2
    assert store.list_events("CASE-CLOSE")[-1]["event_type"] == "CASE_CLOSED"
    assert store.list_events("CASE-CLOSE")[-1]["case_version"] == 2
    with pytest.raises(StoppedCase):
        store.update_intake(case_ref="CASE-CLOSE", event_id="EV-3", expected_case_version=1, fields={"goal": "b"})


def test_store_creates_parent_directory_and_rejects_memory_database(tmp_path):
    path = tmp_path / "nested" / "case.sqlite"
    store = HairColorCaseStore(path)
    assert path.exists()
    with pytest.raises(CaseStoreError, match="persistent file path"):
        HairColorCaseStore(":memory:")


def test_validation_rejects_duplicate_normalized_keys_and_bool_versions(store):
    with pytest.raises(CaseStoreError, match="unique after normalization"):
        store.create_case(case_ref="CASE-NORM", event_id="EV-NORM", intake={"goal": "x", " goal ": "y"})
    store.create_case(case_ref="CASE-BOOL", event_id="EV-BOOL", intake={"goal": "synthetic"})
    with pytest.raises(CaseStoreError, match="positive integer"):
        store.change_target(case_ref="CASE-BOOL", event_id="EV-BOOL-2", expected_case_version=True)
    with pytest.raises(CaseStoreError, match="positive integer"):
        store.stop_case(case_ref="CASE-BOOL", event_id="EV-BOOL-3", expected_case_version=True)


def test_invalid_intake_and_missing_case_rejected(store):
    with pytest.raises(CaseStoreError):
        store.create_case(case_ref="CASE-X", event_id="EV-X", intake={"goal": 7})
    with pytest.raises(CaseStoreError):
        store.get_case("missing")


def test_create_and_input_normalization_edge_cases(store):
    with pytest.raises(CaseStoreError, match="non-empty string"):
        store.create_case(case_ref=" ", event_id="EV-BLANK", intake={})
    with pytest.raises(CaseStoreError, match="non-empty string"):
        store.create_case(case_ref="CASE-BLANK", event_id="", intake={})
    with pytest.raises(CaseStoreError, match="mapping"):
        store.create_case(case_ref="CASE-NONMAP", event_id="EV-NONMAP", intake=None)
    with pytest.raises(CaseStoreError, match="keys must be non-empty"):
        store.create_case(case_ref="CASE-EMPTYKEY", event_id="EV-EMPTYKEY", intake={" ": "x"})
    store.create_case(case_ref="CASE-DUPCREATE", event_id="EV-DUPCREATE", intake={})
    with pytest.raises(CaseStoreError, match="already exists"):
        store.create_case(case_ref="CASE-DUPCREATE", event_id="EV-OTHER", intake={})


def test_update_and_target_change_edge_guards(store):
    store.create_case(case_ref="CASE-EDGE", event_id="EV-EDGE-1", intake={"goal": "test"})
    with pytest.raises(CaseStoreError, match="at least one"):
        store.update_intake(case_ref="CASE-EDGE", event_id="EV-EDGE-2", expected_case_version=1, fields={})
    with pytest.raises(CaseNotFound):
        store.update_intake(case_ref="CASE-MISSING", event_id="EV-EDGE-3", expected_case_version=1, fields={"goal": "x"})
    with pytest.raises(CaseNotFound):
        store.change_target(case_ref="CASE-MISSING", event_id="EV-EDGE-4", expected_case_version=1, target_description="revised target")
    store.stop_case(case_ref="CASE-EDGE", event_id="EV-EDGE-5", expected_case_version=1)
    with pytest.raises(StoppedCase):
        store.change_target(case_ref="CASE-EDGE", event_id="EV-EDGE-6", expected_case_version=1, target_description="revised target")
    store.create_case(case_ref="CASE-STALE-TARGET", event_id="EV-EDGE-7", intake={})
    store.change_target(case_ref="CASE-STALE-TARGET", event_id="EV-EDGE-8", expected_case_version=1, target_description="revised target")
    with pytest.raises(StaleCaseVersion):
        store.change_target(case_ref="CASE-STALE-TARGET", event_id="EV-EDGE-9", expected_case_version=1, target_description="revised target")


def test_duplicate_target_and_stop_event_ids_roll_back(store):
    store.create_case(case_ref="CASE-DUP-EVENT", event_id="EV-1", intake={"goal": "test"})
    with pytest.raises(CaseStoreError, match="unique within case"):
        store.change_target(case_ref="CASE-DUP-EVENT", event_id="EV-1", expected_case_version=1, target_description="revised target")
    assert store.get_case("CASE-DUP-EVENT").case_version == 1
    with pytest.raises(CaseStoreError, match="unique within case"):
        store.stop_case(case_ref="CASE-DUP-EVENT", event_id="EV-1", expected_case_version=1)
    assert store.get_case("CASE-DUP-EVENT").state == "ACTIVE"
    assert store.get_case("CASE-DUP-EVENT").case_version == 1


def test_stop_guards_and_validation(store):
    store.create_case(case_ref="CASE-STOP-EDGE", event_id="EV-1", intake={"goal": "test"})
    with pytest.raises(CaseStoreError, match="tuple of strings"):
        store.stop_case(case_ref="CASE-STOP-EDGE", event_id="EV-2", expected_case_version=1, performed_step_refs=["x"])
    with pytest.raises(CaseNotFound):
        store.stop_case(case_ref="CASE-MISSING", event_id="EV-3", expected_case_version=1)
    store.stop_case(case_ref="CASE-STOP-EDGE", event_id="EV-4", expected_case_version=1)
    with pytest.raises(StoppedCase, match="already stopped"):
        store.stop_case(case_ref="CASE-STOP-EDGE", event_id="EV-5", expected_case_version=1)
    with pytest.raises(StoppedCase):
        store.stop_case(case_ref="CASE-STOP-EDGE", event_id="EV-6", expected_case_version=2)


def test_triage_guards_and_duplicate_event_rollback(store):
    store.create_case(case_ref="CASE-TRIAGE-EDGE", event_id="EV-1", intake={"goal": "test"})
    valid = dict(
        case_ref="CASE-TRIAGE-EDGE", event_id="EV-2", expected_case_version=1,
        expected_target_version=1, request_id="REQ-2",
        consultation_status="NEEDS_INFORMATION_OR_TEST",
        reason_codes=(), safe_summary="synthetic summary",
    )
    with pytest.raises(CaseStoreError, match="tuple of non-empty"):
        store.record_triage(**{**valid, "reason_codes": ["DATA_GAP"]})
    with pytest.raises(CaseStoreError, match="triage-only status"):
        store.record_triage(**{**valid, "consultation_status": "SUGGESTION"})
    with pytest.raises(CaseNotFound):
        store.record_triage(**{**valid, "case_ref": "CASE-MISSING"})
    store.stop_case(case_ref="CASE-TRIAGE-EDGE", event_id="EV-3", expected_case_version=1)
    with pytest.raises(StoppedCase):
        store.record_triage(**{**valid, "event_id": "EV-4"})
    store.create_case(case_ref="CASE-TRIAGE-DUP", event_id="EV-5", intake={})
    duplicate = {**valid, "case_ref": "CASE-TRIAGE-DUP", "event_id": "EV-5"}
    with pytest.raises(CaseStoreError, match="unique within case"):
        store.record_triage(**duplicate)
    assert store.get_case("CASE-TRIAGE-DUP").state == "ACTIVE"


def test_close_guards_and_duplicate_event_rollback(store):
    store.create_case(case_ref="CASE-CLOSE-EDGE", event_id="EV-1", intake={"goal": "test"})
    with pytest.raises(CaseNotFound):
        store.close_case(case_ref="CASE-MISSING", event_id="EV-2", expected_case_version=1, closure_reason="done")
    with pytest.raises(StaleCaseVersion):
        store.close_case(case_ref="CASE-CLOSE-EDGE", event_id="EV-STALE", expected_case_version=2, closure_reason="stale")
    closed = store.close_case(case_ref="CASE-CLOSE-EDGE", event_id="EV-3", expected_case_version=1, closure_reason="done")
    assert closed.state == "CLOSED"
    with pytest.raises(CaseStoreError, match="already closed"):
        store.close_case(case_ref="CASE-CLOSE-EDGE", event_id="EV-4", expected_case_version=1, closure_reason="again")
    with pytest.raises(CaseStoreError, match="already closed"):
        store.close_case(case_ref="CASE-CLOSE-EDGE", event_id="EV-5", expected_case_version=2, closure_reason="stale")
    store.create_case(case_ref="CASE-CLOSE-DUP", event_id="EV-6", intake={})
    with pytest.raises(CaseStoreError, match="unique within case"):
        store.close_case(case_ref="CASE-CLOSE-DUP", event_id="EV-6", expected_case_version=1, closure_reason="done")
    assert store.get_case("CASE-CLOSE-DUP").state == "ACTIVE"


def test_restart_guards_and_duplicate_restart_rollback(store):
    with pytest.raises(CaseStoreError, match="distinct case_ref"):
        store.fresh_restart(source_case_ref="SAME", new_case_ref="SAME", event_id="EV-1", intake={})
    with pytest.raises(CaseNotFound, match="source case"):
        store.fresh_restart(source_case_ref="MISSING", new_case_ref="NEW", event_id="EV-2", intake={})
    store.create_case(case_ref="CASE-RESTART-SOURCE", event_id="EV-3", intake={})
    store.stop_case(case_ref="CASE-RESTART-SOURCE", event_id="EV-4", expected_case_version=1)
    store.create_case(case_ref="CASE-RESTART-EXISTS", event_id="EV-5", intake={})
    with pytest.raises(CaseStoreError, match="restart case or audit events"):
        store.fresh_restart(source_case_ref="CASE-RESTART-SOURCE", new_case_ref="CASE-RESTART-EXISTS", event_id="EV-5", intake={})
    assert store.get_case("CASE-RESTART-SOURCE").state == "STOPPED"
    assert store.get_case("CASE-RESTART-EXISTS").state == "ACTIVE"



def test_restart_rolls_back_new_case_when_source_backlink_event_id_collides(store):
    store.create_case(case_ref="CASE-BACKLINK-SOURCE", event_id="EV-CREATE", intake={})
    store.stop_case(
        case_ref="CASE-BACKLINK-SOURCE",
        event_id="EV-RESTART:RESTARTED_AS",
        expected_case_version=1,
    )
    with pytest.raises(CaseStoreError, match="restart case or audit events"):
        store.fresh_restart(
            source_case_ref="CASE-BACKLINK-SOURCE",
            new_case_ref="CASE-BACKLINK-NEW",
            event_id="EV-RESTART",
            intake={"goal": "fresh synthetic"},
        )
    with pytest.raises(CaseNotFound):
        store.get_case("CASE-BACKLINK-NEW")
    source_events = store.list_events("CASE-BACKLINK-SOURCE")
    assert [event["event_type"] for event in source_events] == ["CASE_CREATED", "STOP_REQUESTED"]
    assert store.get_case("CASE-BACKLINK-SOURCE").updated_event_id == "EV-RESTART:RESTARTED_AS"
