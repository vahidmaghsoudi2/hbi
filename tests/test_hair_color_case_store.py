"""Tests for durable versioned Hair Color case intake storage."""
import pytest

from app.hair_color.case_store import (
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
    changed = store.change_target(case_ref="CASE-T", event_id="EV-2", expected_case_version=1)
    assert (changed.case_version, changed.target_version) == (2, 2)
    assert store.list_events("CASE-T")[-1]["event_type"] == "TARGET_CHANGED"


def test_stop_is_a_terminal_record_for_updates_and_no_auto_resume(store):
    store.create_case(case_ref="CASE-STOP", event_id="EV-1", intake={"goal": "a"})
    stopped = store.stop_case(
        case_ref="CASE-STOP", event_id="EV-2", expected_case_version=1,
        performed_step_refs=("step-a", "step-a", " "),
    )
    assert stopped.state == "STOPPED"
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
    assert store.list_events("CASE-NEW")[-1]["payload"] == {"source_case_ref": "CASE-OLD"}


def test_close_case_records_terminal_state_and_blocks_updates(store):
    store.create_case(case_ref="CASE-CLOSE", event_id="EV-1", intake={"goal": "a"})
    closed = store.close_case(
        case_ref="CASE-CLOSE", event_id="EV-2", expected_case_version=1,
        closure_reason="synthetic completion",
    )
    assert closed.state == "CLOSED"
    assert store.list_events("CASE-CLOSE")[-1]["event_type"] == "CASE_CLOSED"
    with pytest.raises(StoppedCase):
        store.update_intake(case_ref="CASE-CLOSE", event_id="EV-3", expected_case_version=1, fields={"goal": "b"})


def test_store_creates_parent_directory_and_rejects_memory_database(tmp_path):
    path = tmp_path / "nested" / "case.sqlite"
    store = HairColorCaseStore(path)
    assert path.exists()
    with pytest.raises(CaseStoreError, match="persistent file path"):
        HairColorCaseStore(":memory:")


def test_invalid_intake_and_missing_case_rejected(store):
    with pytest.raises(CaseStoreError):
        store.create_case(case_ref="CASE-X", event_id="EV-X", intake={"goal": 7})
    with pytest.raises(CaseStoreError):
        store.get_case("missing")
