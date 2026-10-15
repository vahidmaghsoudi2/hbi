"""Run an isolated G8 API session and finalize auditable evidence before cleanup.

The disposable SQLite database is never removed unless a readback export and an
integrity manifest have both been written successfully. If finalization fails, the
database stays in its session-specific temporary directory with a failure marker.
"""
from __future__ import annotations

import base64
import getpass
import hashlib
import json
import os
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


HOST = "127.0.0.1"
PORT = 8765
HEALTH_URL = f"http://{HOST}:{PORT}/health"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _port_is_free() -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind((HOST, PORT))
        except OSError:
            return False
        return True


def _health_ok() -> bool:
    try:
        with urllib.request.urlopen(HEALTH_URL, timeout=1) as response:
            return response.status == 200
    except (OSError, urllib.error.URLError):
        return False


def _code_sha() -> str:
    configured = os.getenv("G8_CODE_SHA", "").strip()
    if configured:
        return configured
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
        check=False,
        timeout=5,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def _json_value(value: Any) -> Any:
    if isinstance(value, bytes):
        return {"encoding": "base64", "value": base64.b64encode(value).decode("ascii")}
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _export_database_readback(db_path: Path, output_path: Path) -> dict[str, int]:
    if db_path.is_symlink() or not db_path.is_file():
        raise RuntimeError(f"isolated database is missing or unsafe: {db_path}")
    uri = db_path.resolve().as_uri() + "?mode=ro"
    with sqlite3.connect(uri, uri=True, timeout=5) as connection:
        connection.row_factory = sqlite3.Row
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise RuntimeError(f"SQLite integrity_check failed: {integrity}")
        table_names = [
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
        ]
        tables: dict[str, Any] = {}
        counts: dict[str, int] = {}
        for table_name in table_names:
            # Table names come from sqlite_master and are quoted as identifiers.
            quoted = '"' + table_name.replace('"', '""') + '"'
            columns = [
                row[1] for row in connection.execute(f"PRAGMA table_info({quoted})")
            ]
            rows = [
                {key: _json_value(value) for key, value in dict(row).items()}
                for row in connection.execute(f"SELECT * FROM {quoted}")
            ]
            tables[table_name] = {"columns": columns, "rows": rows}
            counts[table_name] = len(rows)
    payload = {
        "exported_at_utc": _utc_now(),
        "database_integrity_check": "ok",
        "table_count": len(tables),
        "tables": tables,
    }
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return counts


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_failure_marker(evidence_dir: Path, message: str) -> None:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    marker = evidence_dir / "FINALIZATION_FAILED.txt"
    marker.write_text(
        f"status=FAILED\nfailed_at_utc={_utc_now()}\nreason={message}\n",
        encoding="utf-8",
    )


def _finalize_evidence(
    *,
    session_id: str,
    session_dir: Path,
    db_path: Path,
    evidence_dir: Path,
    api_log_path: Path,
    code_sha: str,
    started_at_utc: str,
) -> bool:
    """Export persisted state and write hashes; false means retain the database."""
    try:
        if not code_sha or code_sha == "unknown":
            raise RuntimeError("exact code SHA is unavailable; set G8_CODE_SHA or run from a Git checkout")
        if session_dir.is_symlink() or not session_dir.is_dir():
            raise RuntimeError(f"isolated session directory is missing or unsafe: {session_dir}")
        if evidence_dir.is_symlink() or not evidence_dir.is_dir():
            raise RuntimeError(f"evidence directory is missing or unsafe: {evidence_dir}")
        if api_log_path.is_file():
            pass
        else:
            raise RuntimeError("API log is missing; cannot finalize an auditable session")

        counts = _export_database_readback(db_path, evidence_dir / "database-readback.json")
        raw_http_dir = evidence_dir / "raw-http"
        raw_http_files = []
        if raw_http_dir.exists():
            if raw_http_dir.is_symlink() or not raw_http_dir.is_dir():
                raise RuntimeError("raw-http evidence path is unsafe")
            raw_http_files = sorted(
                str(path.relative_to(evidence_dir).as_posix())
                for path in raw_http_dir.rglob("*")
                if path.is_file() and not path.is_symlink()
            )

        metadata = {
            "status": "FINALIZED",
            "session_id": session_id,
            "code_sha": code_sha,
            "started_at_utc": started_at_utc,
            "finalized_at_utc": _utc_now(),
            "environment": {
                "HBI_ENV": os.getenv("HBI_ENV", "development"),
                "database_path": str(db_path.resolve()),
                "session_directory": str(session_dir.resolve()),
            },
            "database_readback": "database-readback.json",
            "table_row_counts": counts,
            "api_log": api_log_path.name,
            "raw_http_files": raw_http_files,
            "note": (
                "Database readback is a persisted-state snapshot, not proof that A1-A9 passed. "
                "Operator-supplied raw HTTP artifacts are listed when present."
            ),
        }
        (evidence_dir / "session-metadata.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        artifacts = []
        for path in sorted(evidence_dir.rglob("*")):
            if path.is_symlink():
                raise RuntimeError(f"refusing to hash symlink evidence artifact: {path}")
            if path.is_file() and path.name != "integrity-manifest.json":
                artifacts.append({
                    "path": path.relative_to(evidence_dir).as_posix(),
                    "size_bytes": path.stat().st_size,
                    "sha256": _sha256(path),
                })
        manifest = {
            "session_id": session_id,
            "code_sha": code_sha,
            "created_at_utc": _utc_now(),
            "algorithm": "sha256",
            "artifacts": artifacts,
        }
        (evidence_dir / "integrity-manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        # Re-read required outputs so a failed/partial write cannot authorize cleanup.
        readback = json.loads((evidence_dir / "database-readback.json").read_text(encoding="utf-8"))
        parsed_manifest = json.loads((evidence_dir / "integrity-manifest.json").read_text(encoding="utf-8"))
        if readback.get("database_integrity_check") != "ok" or parsed_manifest.get("session_id") != session_id:
            raise RuntimeError("evidence readback verification failed")
        if not any(item["path"] == "database-readback.json" for item in parsed_manifest["artifacts"]):
            raise RuntimeError("integrity manifest does not cover database readback")
        (evidence_dir / "FINALIZATION_FAILED.txt").unlink(missing_ok=True)
        print(f"EVIDENCE_FINALIZATION=PASS", flush=True)
        print(f"EVIDENCE_DIR={evidence_dir}", flush=True)
        print(f"EVIDENCE_MANIFEST={evidence_dir / 'integrity-manifest.json'}", flush=True)
        return True
    except Exception as exc:
        _write_failure_marker(evidence_dir, f"{type(exc).__name__}: {exc}")
        print(f"EVIDENCE_FINALIZATION=FAIL ({type(exc).__name__}: {exc})", flush=True)
        print(f"DISPOSABLE_DATABASE_RETAINED={db_path}", flush=True)
        print(f"FINALIZATION_FAILURE_MARKER={evidence_dir / 'FINALIZATION_FAILED.txt'}", flush=True)
        return False


def _remove_disposable_db(session_dir: Path, db_path: Path) -> bool:
    """Remove only the exact session database and sidecars after evidence is finalized."""
    for suffix in ("", "-wal", "-shm", "-journal"):
        candidate = Path(str(db_path) + suffix)
        try:
            if candidate.is_symlink() or (candidate.exists() and not candidate.is_file()):
                print(f"REFUSING CLEANUP OF UNEXPECTED PATH: {candidate}", flush=True)
                return False
            if candidate.exists():
                candidate.unlink()
        except OSError as exc:
            print(f"CLEANUP ERROR for {candidate}: {exc}", flush=True)
            return False
    try:
        session_dir.rmdir()
    except OSError as exc:
        print(f"CLEANUP ERROR for session directory {session_dir}: {exc}", flush=True)
        return False
    return not db_path.exists()


def main() -> int:
    smoke_test = "--smoke-test" in sys.argv[1:]
    runtime_ok = False
    if os.getenv("HBI_ENV", "").lower() == "production":
        print("REFUSED: HBI_ENV=production.", flush=True)
        return 2
    if not _port_is_free():
        print(
            f"REFUSED: {HOST}:{PORT} is already occupied. Stop the other service first; "
            "the runner will not attach to an unknown database.",
            flush=True,
        )
        return 2

    temp_root = Path(tempfile.gettempdir()).resolve()
    pilot_root = temp_root / "hbi-g8-pilot"
    if pilot_root.is_symlink():
        print(f"REFUSED: pilot root must not be a symlink: {pilot_root}", flush=True)
        return 2
    pilot_root.mkdir(parents=True, exist_ok=True)

    session_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    started_at_utc = _utc_now()
    session_dir = pilot_root / f"live-{session_id}"
    evidence_root = temp_root / "hbi-g8-pilot-evidence"
    evidence_root.mkdir(parents=True, exist_ok=True)
    evidence_dir = evidence_root / session_id
    log_path = evidence_dir / "api.log"

    try:
        session_dir.mkdir()
        evidence_dir.mkdir()
        (evidence_dir / "raw-http").mkdir()
    except FileExistsError:
        print(f"REFUSED: session/evidence path already exists for {session_id}.", flush=True)
        return 2

    db_path = session_dir / "pilot.db"
    if os.name != "nt":
        db_url = "sqlite:////" + db_path.as_posix().lstrip("/")
    else:
        db_url = "sqlite:///" + db_path.as_posix()

    env = os.environ.copy()
    env["HBI_ENV"] = "development"
    env["DATABASE_URL"] = db_url
    env["HBI_CORS_ORIGINS"] = f"http://{HOST}:4173,http://localhost:4173"

    if not smoke_test:
        username = input("HBI login username for this isolated pilot: ").strip()
        password = getpass.getpass("HBI login password (input hidden): ")
        if not username or not password:
            print("REFUSED: username and password are required for standard login.", flush=True)
            _write_failure_marker(evidence_dir, "operator credentials were not supplied")
            return 2
        env["HBI_ADMIN_USERNAME"] = username
        env["HBI_ADMIN_PASSWORD"] = password

    command = [
        sys.executable, "-m", "uvicorn", "app.main:app",
        "--host", HOST, "--port", str(PORT),
    ]
    print(f"G8_SESSION={session_id}", flush=True)
    print(f"DATABASE_URL={db_url}", flush=True)
    print(f"API_DOCS=http://{HOST}:{PORT}/docs", flush=True)
    print(f"HEALTH={HEALTH_URL}", flush=True)
    print(f"API_LOG={log_path}", flush=True)
    print(f"RAW_HTTP_EVIDENCE_DIR={evidence_dir / 'raw-http'}", flush=True)
    print("MODE=EMPTY_ISOLATED_DATABASE; STANDARD_LOGIN; NO_FIXTURES; NO_AUTO_ACTIVATION", flush=True)
    print("BEFORE STOP: save available raw request/response artifacts under RAW_HTTP_EVIDENCE_DIR.", flush=True)

    process = None
    finalized = False
    cleanup_ok = False
    try:
        with log_path.open("w", encoding="utf-8") as log:
            process = subprocess.Popen(
                command, cwd=Path(__file__).resolve().parents[1],
                env=env, stdout=log, stderr=subprocess.STDOUT,
            )
            deadline = time.monotonic() + 45
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    print(f"REFUSED: API exited during startup (code={process.returncode}).", flush=True)
                    break
                if _health_ok():
                    runtime_ok = True
                    print("PILOT_API_READY=YES", flush=True)
                    if smoke_test:
                        print("SMOKE_TEST=PASS", flush=True)
                        break
                    print("OPERATOR_ACTION: use /docs and preserve raw request/response artifacts.", flush=True)
                    print("STOP: press Ctrl+C here after the pilot session.", flush=True)
                    while process.poll() is None:
                        time.sleep(0.5)
                    break
                time.sleep(0.5)
            else:
                print("REFUSED: API health check timed out. Inspect API_LOG.", flush=True)
    except KeyboardInterrupt:
        print("STOP_REQUESTED=YES", flush=True)
    finally:
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)

        code_sha = _code_sha()
        finalized = _finalize_evidence(
            session_id=session_id,
            session_dir=session_dir,
            db_path=db_path,
            evidence_dir=evidence_dir,
            api_log_path=log_path,
            code_sha=code_sha,
            started_at_utc=started_at_utc,
        )
        if finalized:
            cleanup_ok = _remove_disposable_db(session_dir, db_path)
            print(f"DATABASE_CLEANUP={'PASS' if cleanup_ok else 'FAIL'}", flush=True)
            if not cleanup_ok:
                _write_failure_marker(evidence_dir, "evidence finalized, but disposable database cleanup failed")
        else:
            print("DATABASE_CLEANUP=SKIPPED_EVIDENCE_FINALIZATION_FAILED", flush=True)
        print(f"API_LOG_RETAINED={log_path}", flush=True)

    return 0 if cleanup_ok and finalized and runtime_ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
