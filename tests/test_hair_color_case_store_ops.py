"""Operational safety tests for synthetic Hair Color SQLite persistence."""
from pathlib import Path
import sqlite3

import pytest

from app.hair_color.case_store import (
    CaseStoreError,
    HairColorCaseStore,
    StaleCaseVersion,
)


def _create(store):
    return store.create_case(
        case_ref="SYNTHETIC-OPS-CASE",
        event_id="SYNTHETIC-OPS-CREATE",
        intake={"goal": "SYNTHETIC: sample"},
    )


def test_store_integrity_backup_and_private_file_permissions(tmp_path):
    source_path = tmp_path / "store.sqlite"
    store = HairColorCaseStore(source_path)
    _create(store)
    store.update_intake(
        case_ref="SYNTHETIC-OPS-CASE",
        event_id="SYNTHETIC-OPS-UPDATE",
        expected_case_version=1,
        fields={"history": "SYNTHETIC: placeholder"},
    )
    assert store.integrity_check() == "ok"

    backup_path = store.backup_to(tmp_path / "backups" / "store-backup.sqlite")
    assert backup_path.exists()
    with sqlite3.connect(backup_path) as backup:
        assert backup.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert backup.execute("PRAGMA user_version").fetchone()[0] == 1
        assert backup.execute("SELECT COUNT(*) FROM hair_color_case_events").fetchone()[0] == 2

    if hasattr(source_path, "stat"):
        assert source_path.stat().st_size > 0
    if Path(source_path).stat().st_mode & 0o777:
        # On POSIX, service data should not be world/group-readable.
        if __import__("os").name == "posix":
            assert source_path.stat().st_mode & 0o077 == 0


def test_backup_destination_must_not_be_source(tmp_path):
    store = HairColorCaseStore(tmp_path / "same.sqlite")
    with pytest.raises(CaseStoreError, match="differ"):
        store.backup_to(tmp_path / "same.sqlite")


def test_unsupported_schema_version_fails_closed(tmp_path):
    path = tmp_path / "version.sqlite"
    HairColorCaseStore(path)
    with sqlite3.connect(path) as db:
        db.execute("PRAGMA user_version = 99")
    with pytest.raises(CaseStoreError, match="unsupported"):
        HairColorCaseStore(path)


def test_duplicate_event_rolls_back_snapshot_mutation(tmp_path):
    store = HairColorCaseStore(tmp_path / "rollback.sqlite")
    _create(store)
    with pytest.raises(CaseStoreError, match="unique"):
        store.update_intake(
            case_ref="SYNTHETIC-OPS-CASE",
            event_id="SYNTHETIC-OPS-CREATE",
            expected_case_version=1,
            fields={"goal": "SYNTHETIC: should rollback"},
        )
    snapshot = store.get_case("SYNTHETIC-OPS-CASE")
    assert snapshot.case_version == 1
    assert snapshot.intake == {"goal": "SYNTHETIC: sample"}
    assert [event["event_type"] for event in store.list_events(snapshot.case_ref)] == ["CASE_CREATED"]


def test_stale_concurrent_update_rejected_and_no_overwrite(tmp_path):
    store = HairColorCaseStore(tmp_path / "stale.sqlite")
    _create(store)
    store.update_intake(
        case_ref="SYNTHETIC-OPS-CASE",
        event_id="SYNTHETIC-OPS-UPDATE-1",
        expected_case_version=1,
        fields={"goal": "SYNTHETIC: winner"},
    )
    with pytest.raises(StaleCaseVersion):
        store.update_intake(
            case_ref="SYNTHETIC-OPS-CASE",
            event_id="SYNTHETIC-OPS-UPDATE-2",
            expected_case_version=1,
            fields={"goal": "SYNTHETIC: stale loser"},
        )
    current = store.get_case("SYNTHETIC-OPS-CASE")
    assert current.case_version == 2
    assert current.intake["goal"] == "SYNTHETIC: winner"
    assert store.integrity_check() == "ok"
