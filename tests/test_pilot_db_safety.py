"""Regression tests for isolated G8 pilot evidence finalization and DB safety."""
import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "prepare_pilot_browser_db.py"
RUNNER = ROOT / "scripts" / "run_g8_isolated_pilot.py"


def _run_with_env(overrides: dict[str, str]) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.update(overrides)
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
        timeout=20,
    )


def test_browser_fixture_builder_refuses_repository_database() -> None:
    repo_db = (ROOT / "data" / "hbi.db").resolve()
    url = "sqlite:///" + repo_db.as_posix()
    result = _run_with_env({
        "HBI_ENV": "development",
        "HBI_PILOT_FIXTURE_MODE": "browser-fixture",
        "DATABASE_URL": url,
    })

    assert result.returncode != 0
    assert "dedicated temporary pilot directory" in result.stderr


def test_browser_fixture_builder_requires_explicit_fixture_mode() -> None:
    pilot_db = Path(os.getenv("TEMP", "/tmp")) / "hbi-g8-pilot" / "pilot.db"
    url = "sqlite:///" + pilot_db.as_posix()
    env = os.environ.copy()
    env.pop("HBI_PILOT_FIXTURE_MODE", None)
    env.update({
        "HBI_ENV": "development",
        "DATABASE_URL": url,
    })
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
        timeout=20,
    )

    assert result.returncode != 0
    assert "HBI_PILOT_FIXTURE_MODE=browser-fixture" in result.stderr


def _load_runner_module():
    import importlib.util

    spec = importlib.util.spec_from_file_location("g8_pilot_runner", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _make_session(tmp_path: Path):
    session_dir = tmp_path / "isolated-session"
    session_dir.mkdir()
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir()
    (evidence_dir / "raw-http").mkdir()
    db_path = session_dir / "pilot.db"
    with sqlite3.connect(db_path) as connection:
        connection.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, lifecycle TEXT)")
        connection.execute("INSERT INTO products (name, lifecycle) VALUES ('Pilot-only test', 'DRAFT')")
    api_log = evidence_dir / "api.log"
    api_log.write_text("startup log\n", encoding="utf-8")
    return session_dir, evidence_dir, db_path, api_log


def _write_valid_raw_http_artifact(evidence_dir: Path) -> Path:
    raw_http_dir = evidence_dir / "raw-http"
    artifact_path = raw_http_dir / "20261015T000000Z-test-request.json"
    artifact = {
        "schema": "hbi.g8.raw-http.v1",
        "request_id": "test-request-001",
        "started_at_utc": "2026-10-15T00:00:00.000Z",
        "finished_at_utc": "2026-10-15T00:00:00.010Z",
        "request": {
            "method": "GET",
            "path": "/health",
            "headers": {"accept": "application/json"},
            "complete": True,
            "body": {"captured": True, "size_bytes": 0, "sha256_observed_bytes": "e3b0c442"},
        },
        "response": {
            "status": 200,
            "headers": {"content-type": "application/json"},
            "started": True,
            "complete": True,
            "body": {"captured": True, "size_bytes": 11, "sha256_observed_bytes": "a" * 64},
        },
    }
    artifact_path.write_text(json.dumps(artifact), encoding="utf-8")
    return artifact_path


def test_evidence_root_refuses_symlink(tmp_path: Path) -> None:
    runner = _load_runner_module()
    temp_root = tmp_path / "temp"
    temp_root.mkdir()
    redirected = tmp_path / "redirected-evidence"
    redirected.mkdir()
    evidence_root = temp_root / "hbi-g8-pilot-evidence"
    try:
        evidence_root.symlink_to(redirected, target_is_directory=True)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"directory symlinks are unavailable in this environment: {exc}")

    with pytest.raises(RuntimeError, match="must not be a symlink"):
        runner._ensure_safe_evidence_root(temp_root)
    assert list(redirected.iterdir()) == []


def test_evidence_root_is_created_inside_temp_root(tmp_path: Path) -> None:
    runner = _load_runner_module()
    temp_root = tmp_path / "temp"
    temp_root.mkdir()

    evidence_root = runner._ensure_safe_evidence_root(temp_root)

    assert evidence_root.is_dir()
    assert evidence_root.resolve().parent == temp_root.resolve()


def test_successful_finalization_preserves_readback_manifest_then_allows_cleanup(tmp_path: Path) -> None:
    runner = _load_runner_module()
    session_dir, evidence_dir, db_path, api_log = _make_session(tmp_path)
    raw_http_artifact = _write_valid_raw_http_artifact(evidence_dir)

    finalized = runner._finalize_evidence(
        session_id="session-success",
        session_dir=session_dir,
        db_path=db_path,
        evidence_dir=evidence_dir,
        api_log_path=api_log,
        code_sha="a" * 40,
        started_at_utc="2026-10-15T00:00:00Z",
    )

    assert finalized is True
    readback_path = evidence_dir / "database-readback.json"
    manifest_path = evidence_dir / "integrity-manifest.json"
    metadata_path = evidence_dir / "session-metadata.json"
    assert readback_path.is_file() and manifest_path.is_file() and metadata_path.is_file()
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert "raw-http/" + raw_http_artifact.name in metadata["raw_http_files"]
    readback = json.loads(readback_path.read_text(encoding="utf-8"))
    assert readback["tables"]["products"]["rows"][0]["lifecycle"] == "DRAFT"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert any(item["path"] == "database-readback.json" and item["sha256"] for item in manifest["artifacts"])
    assert runner._remove_disposable_db(session_dir, db_path) is True
    assert not db_path.exists()
    assert manifest_path.is_file()


def test_failed_finalization_retains_database_and_writes_marker(tmp_path: Path) -> None:
    runner = _load_runner_module()
    session_dir, evidence_dir, db_path, api_log = _make_session(tmp_path)

    with patch.object(runner, "_export_database_readback", side_effect=RuntimeError("injected export failure")):
        finalized = runner._finalize_evidence(
            session_id="session-failure",
            session_dir=session_dir,
            db_path=db_path,
            evidence_dir=evidence_dir,
            api_log_path=api_log,
            code_sha="b" * 40,
            started_at_utc="2026-10-15T00:00:00Z",
        )

    assert finalized is False
    marker = evidence_dir / "FINALIZATION_FAILED.txt"
    assert marker.is_file()
    assert "injected export failure" in marker.read_text(encoding="utf-8")
    assert db_path.is_file()
    assert session_dir.is_dir()


def test_finalization_refuses_session_without_http_artifacts_and_retains_database(tmp_path: Path) -> None:
    runner = _load_runner_module()
    session_dir, evidence_dir, db_path, api_log = _make_session(tmp_path)

    finalized = runner._finalize_evidence(
        session_id="session-no-http",
        session_dir=session_dir,
        db_path=db_path,
        evidence_dir=evidence_dir,
        api_log_path=api_log,
        code_sha="c" * 40,
        started_at_utc="2026-10-15T00:00:00Z",
    )

    assert finalized is False
    assert db_path.is_file()
    marker = evidence_dir / "FINALIZATION_FAILED.txt"
    assert marker.is_file()
    assert "no raw HTTP request/response artifacts" in marker.read_text(encoding="utf-8")


def test_finalization_refuses_unknown_code_sha_and_retains_database(tmp_path: Path) -> None:
    runner = _load_runner_module()
    session_dir, evidence_dir, db_path, api_log = _make_session(tmp_path)

    finalized = runner._finalize_evidence(
        session_id="session-no-sha",
        session_dir=session_dir,
        db_path=db_path,
        evidence_dir=evidence_dir,
        api_log_path=api_log,
        code_sha="",
        started_at_utc="2026-10-15T00:00:00Z",
    )

    assert finalized is False
    assert (evidence_dir / "FINALIZATION_FAILED.txt").is_file()
    assert db_path.is_file()



def test_finalization_refuses_database_without_application_tables(tmp_path: Path) -> None:
    runner = _load_runner_module()
    session_dir = tmp_path / "isolated-session"
    session_dir.mkdir()
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir()
    (evidence_dir / "raw-http").mkdir()
    db_path = session_dir / "pilot.db"
    sqlite3.connect(db_path).close()
    api_log = evidence_dir / "api.log"
    api_log.write_text("startup log\\n", encoding="utf-8")

    finalized = runner._finalize_evidence(
        session_id="session-empty-db",
        session_dir=session_dir,
        db_path=db_path,
        evidence_dir=evidence_dir,
        api_log_path=api_log,
        code_sha="c" * 40,
        started_at_utc="2026-10-15T00:00:00Z",
    )

    assert finalized is False
    assert (evidence_dir / "FINALIZATION_FAILED.txt").is_file()
    assert db_path.is_file()


def test_isolated_g8_runner_smoke_starts_finalizes_and_cleans_its_database() -> None:
    from sqlalchemy.engine import make_url

    env = os.environ.copy()
    env["HBI_ENV"] = "development"
    env.pop("DATABASE_URL", None)
    result = subprocess.run(
        [sys.executable, str(RUNNER), "--smoke-test"],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
        timeout=60,
    )

    output = result.stdout + "\\n" + result.stderr
    assert result.returncode == 0, output
    assert "PILOT_API_READY=YES" in output
    assert "SMOKE_TEST=PASS" in output
    assert "EVIDENCE_FINALIZATION=PASS" in output
    assert "DATABASE_CLEANUP=PASS" in output

    db_url_line = next(line for line in output.splitlines() if line.startswith("DATABASE_URL="))
    db_path = Path(make_url(db_url_line.split("=", 1)[1]).database)
    assert not db_path.exists()

    manifest_line = next(line for line in output.splitlines() if line.startswith("EVIDENCE_MANIFEST="))
    manifest_path = Path(manifest_line.split("=", 1)[1])
    assert manifest_path.is_file()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["algorithm"] == "sha256"
    assert any(item["path"] == "database-readback.json" for item in manifest["artifacts"])

def test_code_sha_override_does_not_bypass_dirty_worktree_check(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = _load_runner_module()
    monkeypatch.setenv("G8_CODE_SHA", "a" * 40)
    dirty_status = subprocess.CompletedProcess(
        args=["git", "status", "--porcelain"], returncode=0, stdout=" M scripts/example.py\n", stderr=""
    )

    with patch.object(runner.subprocess, "run", return_value=dirty_status) as run:
        assert runner._code_sha() == ""

    run.assert_called_once()


def test_code_sha_override_must_match_actual_head(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = _load_runner_module()
    monkeypatch.setenv("G8_CODE_SHA", "a" * 40)
    clean_status = subprocess.CompletedProcess(
        args=["git", "status", "--porcelain"], returncode=0, stdout="", stderr=""
    )
    actual_head = "b" * 40
    head_result = subprocess.CompletedProcess(
        args=["git", "rev-parse", "HEAD"], returncode=0, stdout=actual_head + "\n", stderr=""
    )

    with patch.object(runner.subprocess, "run", side_effect=[clean_status, head_result]):
        assert runner._code_sha() == ""


def test_code_sha_returns_actual_head_when_matching_override_is_supplied(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner = _load_runner_module()
    actual_head = "a" * 40
    monkeypatch.setenv("G8_CODE_SHA", actual_head.upper())
    clean_status = subprocess.CompletedProcess(
        args=["git", "status", "--porcelain"], returncode=0, stdout="", stderr=""
    )
    head_result = subprocess.CompletedProcess(
        args=["git", "rev-parse", "HEAD"], returncode=0, stdout=actual_head + "\n", stderr=""
    )

    with patch.object(runner.subprocess, "run", side_effect=[clean_status, head_result]):
        assert runner._code_sha() == actual_head

