"""Tests for safe recovery of historical G8 pilot artifacts."""
from __future__ import annotations

import hashlib
import json
import sqlite3
import zipfile
from pathlib import Path

import pytest

from scripts.recover_g8_pilot_artifacts import recover


CANDIDATE = "G8-NUMBUZIN-NO9-20261018"


def _roots(tmp_path: Path) -> tuple[Path, Path, Path]:
    evidence = tmp_path / "hbi-g8-pilot-evidence"
    pilot = tmp_path / "hbi-g8-pilot"
    evidence.mkdir()
    pilot.mkdir()
    return evidence, pilot, tmp_path


def _session(evidence_root: Path, pilot_root: Path, session_id: str) -> tuple[Path, Path]:
    evidence = evidence_root / session_id
    evidence.mkdir()
    (evidence / "session-metadata.json").write_text(
        json.dumps({"candidate_id": CANDIDATE, "session_id": session_id}),
        encoding="utf-8",
    )
    raw_http = evidence / "raw-http"
    raw_http.mkdir()
    (raw_http / "capture.json").write_text(
        json.dumps({"request": {"path": "/api/pilot"}, "candidate": CANDIDATE}),
        encoding="utf-8",
    )
    db_dir = pilot_root / f"live-{session_id}"
    db_dir.mkdir()
    db_path = db_dir / "pilot.db"
    with sqlite3.connect(db_path) as connection:
        connection.execute("CREATE TABLE product (product_id TEXT, lifecycle TEXT)")
        connection.execute("INSERT INTO product VALUES (?, ?)", (CANDIDATE, "DRAFT"))
    return evidence, db_path


def test_recovery_archives_evidence_and_readonly_db_backup_without_source_changes(tmp_path: Path) -> None:
    evidence_root, pilot_root, temp_root = _roots(tmp_path)
    evidence_session, source_db = _session(evidence_root, pilot_root, "20261018T123000Z")
    original_hash = hashlib.sha256(source_db.read_bytes()).hexdigest()
    output = tmp_path / "recovery.zip"

    result = recover(temp_root=temp_root, candidate=CANDIDATE, output_zip=output)

    assert result["matched_session"] == evidence_session.name
    assert result["database_backup"] is True
    assert output.is_file()
    assert hashlib.sha256(source_db.read_bytes()).hexdigest() == original_hash
    with zipfile.ZipFile(output) as archive:
        names = archive.namelist()
        assert "source-evidence/session-metadata.json" in names
        assert "source-evidence/raw-http/capture.json" in names
        assert "recovered-database/pilot-readonly-backup.sqlite" in names
        manifest = json.loads(archive.read("recovery-manifest.json"))
        assert manifest["source_files_are_unchanged"] is True
        assert manifest["candidate"] == CANDIDATE
        assert len(manifest["artifacts"]) == 3
        with archive.open("recovered-database/pilot-readonly-backup.sqlite") as db_file:
            backup_path = tmp_path / "verify-backup.sqlite"
            backup_path.write_bytes(db_file.read())
        with sqlite3.connect(backup_path) as connection:
            assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
            assert connection.execute("SELECT lifecycle FROM product WHERE product_id=?", (CANDIDATE,)).fetchone()[0] == "DRAFT"
        backup_path.unlink()


def test_recovery_refuses_zero_matches_without_creating_package(tmp_path: Path) -> None:
    evidence_root, pilot_root, temp_root = _roots(tmp_path)
    (evidence_root / "empty-session").mkdir()
    output = tmp_path / "no-match.zip"

    with pytest.raises(RuntimeError, match="found 0"):
        recover(temp_root=temp_root, candidate=CANDIDATE, output_zip=output)

    assert not output.exists()


def test_recovery_refuses_ambiguous_multiple_sessions(tmp_path: Path) -> None:
    evidence_root, pilot_root, temp_root = _roots(tmp_path)
    _session(evidence_root, pilot_root, "session-a")
    _session(evidence_root, pilot_root, "session-b")
    output = tmp_path / "ambiguous.zip"

    with pytest.raises(RuntimeError, match="found 2"):
        recover(temp_root=temp_root, candidate=CANDIDATE, output_zip=output)

    assert not output.exists()


def test_recovery_refuses_symlinked_evidence_root(tmp_path: Path) -> None:
    redirected = tmp_path / "redirected"
    redirected.mkdir()
    evidence_link = tmp_path / "hbi-g8-pilot-evidence"
    try:
        evidence_link.symlink_to(redirected, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"symlink creation unavailable: {exc}")
    pilot_root = tmp_path / "hbi-g8-pilot"
    pilot_root.mkdir()
    output = tmp_path / "symlink-refused.zip"

    with pytest.raises(RuntimeError, match="symlinked"):
        recover(temp_root=tmp_path, candidate=CANDIDATE, output_zip=output)

    assert list(redirected.iterdir()) == []
    assert not output.exists()


def test_recovery_refuses_to_overwrite_existing_output(tmp_path: Path) -> None:
    evidence_root, pilot_root, temp_root = _roots(tmp_path)
    _session(evidence_root, pilot_root, "session-existing-output")
    output = tmp_path / "existing.zip"
    output.write_bytes(b"preserve-me")

    with pytest.raises(RuntimeError, match="refusing overwrite"):
        recover(temp_root=temp_root, candidate=CANDIDATE, output_zip=output)

    assert output.read_bytes() == b"preserve-me"


def test_candidate_scan_finds_token_after_multiple_chunks(tmp_path: Path) -> None:
    from scripts.recover_g8_pilot_artifacts import _file_contains_token

    file_path = tmp_path / "large-readback.json"
    token = CANDIDATE.casefold().encode("utf-8")
    file_path.write_bytes(b"x" * (1024 * 1024 + 17) + token + b"y")

    assert _file_contains_token(file_path, token)
