import os
"""Operational safety tests for synthetic Hair Color SQLite persistence."""
from pathlib import Path
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from fastapi import HTTPException

from app.api.routers.hair_color_cases import get_hair_color_case_service
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


def test_api_storage_dependency_returns_503_when_path_missing(monkeypatch):
    monkeypatch.delenv("HBI_HAIR_COLOR_CASE_DB", raising=False)
    with pytest.raises(HTTPException) as error:
        get_hair_color_case_service()
    assert error.value.status_code == 503


@pytest.mark.skipif(os.name != 'posix', reason='POSIX permission semantics required')
def test_api_storage_dependency_sanitizes_storage_error(monkeypatch, tmp_path):
    unsafe = tmp_path / "unsafe"
    unsafe.mkdir(mode=0o755)
    unsafe.chmod(0o755)
    monkeypatch.setenv("HBI_HAIR_COLOR_CASE_DB", str(unsafe / "case.sqlite"))
    with pytest.raises(HTTPException) as error:
        get_hair_color_case_service()
    assert error.value.status_code == 503
    assert "storage is unavailable" in error.value.detail
    assert str(tmp_path) not in error.value.detail


def test_store_rejects_relative_path(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(CaseStoreError, match="absolute"):
        HairColorCaseStore("relative.sqlite")


def test_store_rejects_symlink_database_path(tmp_path):
    if not hasattr(Path, "symlink_to"):
        pytest.skip("symlinks are not supported")
    real = tmp_path / "real.sqlite"
    HairColorCaseStore(real)
    alias = tmp_path / "alias.sqlite"
    try:
        alias.symlink_to(real)
    except OSError as exc:
        pytest.skip(f"Symlink creation unavailable on this platform: {exc}")
    with pytest.raises(CaseStoreError, match="symlink"):
        HairColorCaseStore(alias)


def test_store_rejects_non_private_directory(tmp_path):
    if __import__("os").name != "posix":
        pytest.skip("POSIX directory permission check")
    unsafe = tmp_path / "unsafe"
    unsafe.mkdir(mode=0o755)
    unsafe.chmod(0o755)
    with pytest.raises(CaseStoreError, match="directory must be private"):
        HairColorCaseStore(unsafe / "case.sqlite")


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
        assert backup.execute("PRAGMA user_version").fetchone()[0] == 2
        assert backup.execute("SELECT COUNT(*) FROM hair_color_case_events").fetchone()[0] == 2

    if hasattr(source_path, "stat"):
        assert source_path.stat().st_size > 0
    if Path(source_path).stat().st_mode & 0o777:
        # On POSIX, service data should not be world/group-readable.
        if __import__("os").name == "posix":
            assert source_path.stat().st_mode & 0o077 == 0


def test_verified_backup_restore_preserves_case_and_history(tmp_path):
    original = HairColorCaseStore(tmp_path / "original.sqlite")
    _create(original)
    original.update_intake(
        case_ref="SYNTHETIC-OPS-CASE",
        event_id="SYNTHETIC-OPS-UPDATE",
        expected_case_version=1,
        fields={"history": "SYNTHETIC: placeholder"},
    )
    backup = original.backup_to(tmp_path / "backups" / "verified.sqlite")
    restored_path = HairColorCaseStore.restore_from_backup(backup, tmp_path / "restore" / "restored.sqlite")
    restored = HairColorCaseStore(restored_path)
    assert restored.integrity_check() == "ok"
    assert restored.get_case("SYNTHETIC-OPS-CASE").case_version == 2
    assert [event["event_type"] for event in restored.list_events("SYNTHETIC-OPS-CASE")] == [
        "CASE_CREATED", "INTAKE_UPDATED",
    ]


def test_backup_destination_must_not_be_source(tmp_path):
    store = HairColorCaseStore(tmp_path / "same.sqlite")
    with pytest.raises(CaseStoreError, match="differ"):
        store.backup_to(tmp_path / "same.sqlite")


def test_backup_refuses_to_overwrite_existing_file(tmp_path):
    store = HairColorCaseStore(tmp_path / "source.sqlite")
    destination = tmp_path / "existing-backup.sqlite"
    destination.write_text("preserve-existing-file", encoding="utf-8")
    with pytest.raises(CaseStoreError, match="already exists"):
        store.backup_to(destination)
    assert destination.read_text(encoding="utf-8") == "preserve-existing-file"


def test_unsupported_schema_version_fails_closed(tmp_path):
    path = tmp_path / "version.sqlite"
    HairColorCaseStore(path)
    with sqlite3.connect(path) as db:
        db.execute("PRAGMA user_version = 99")
    with pytest.raises(CaseStoreError, match="unsupported"):
        HairColorCaseStore(path)


def test_schema_v1_migrates_and_preserves_events_with_legacy_timestamp_marker(tmp_path):
    path = tmp_path / "legacy.sqlite"
    with sqlite3.connect(path) as db:
        db.executescript(
            """
            CREATE TABLE hair_color_cases (
                case_ref TEXT PRIMARY KEY,
                case_version INTEGER NOT NULL,
                target_version INTEGER NOT NULL,
                state TEXT NOT NULL,
                intake_json TEXT NOT NULL,
                created_event_id TEXT NOT NULL,
                updated_event_id TEXT NOT NULL
            );
            CREATE TABLE hair_color_case_events (
                case_ref TEXT NOT NULL,
                event_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                case_version INTEGER NOT NULL,
                target_version INTEGER NOT NULL,
                payload_json TEXT NOT NULL,
                PRIMARY KEY(case_ref,event_id),
                FOREIGN KEY(case_ref) REFERENCES hair_color_cases(case_ref)
            );
            INSERT INTO hair_color_cases VALUES ('SYNTHETIC-LEGACY',1,1,'ACTIVE','{}','SYNTHETIC-CREATE','SYNTHETIC-CREATE');
            INSERT INTO hair_color_case_events VALUES ('SYNTHETIC-LEGACY','SYNTHETIC-CREATE','CASE_CREATED',1,1,'{}');
            PRAGMA user_version = 1;
            """
        )
    migrated = HairColorCaseStore(path)
    events = migrated.list_events("SYNTHETIC-LEGACY")
    assert events[0]["event_type"] == "CASE_CREATED"
    assert events[0]["occurred_at"] == "LEGACY-UNKNOWN"
    assert migrated.integrity_check() == "ok"
    migrated.create_case(case_ref="SYNTHETIC-NEW", event_id="SYNTHETIC-NEW-EVENT", intake={})
    new_event = migrated.list_events("SYNTHETIC-NEW")[0]
    assert new_event["occurred_at"] != "LEGACY-UNKNOWN"


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


def test_two_simultaneous_updates_with_same_version_have_one_winner(tmp_path):
    store = HairColorCaseStore(tmp_path / "concurrent.sqlite")
    _create(store)
    barrier = Barrier(2)

    def update(event_id, value):
        barrier.wait(timeout=5)
        try:
            result = store.update_intake(
                case_ref="SYNTHETIC-OPS-CASE",
                event_id=event_id,
                expected_case_version=1,
                fields={"goal": value},
            )
            return ("success", result.intake["goal"])
        except StaleCaseVersion:
            return ("stale", None)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(
            lambda args: update(*args),
            (("SYNTHETIC-RACE-1", "SYNTHETIC: first"), ("SYNTHETIC-RACE-2", "SYNTHETIC: second")),
        ))
    assert sorted(result[0] for result in results) == ["stale", "success"]
    current = store.get_case("SYNTHETIC-OPS-CASE")
    assert current.case_version == 2
    assert current.intake["goal"] in {"SYNTHETIC: first", "SYNTHETIC: second"}
    assert len(store.list_events(current.case_ref)) == 2
