"""Launch a real HBI API session against a fresh, disposable G8 SQLite database.

This runner does not seed fixtures or change product lifecycle state. Use the local
Swagger UI to perform operator-driven Product Intake steps against this isolated DB.
The database is deleted on shutdown; the API log is retained for evidence review.
"""
from __future__ import annotations

import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


HOST = "127.0.0.1"
PORT = 8765
HEALTH_URL = f"http://{HOST}:{PORT}/health"


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


def _remove_disposable_db(session_dir: Path, db_path: Path) -> bool:
    """Remove only the exact session directory created by this process."""
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
    session_dir = pilot_root / f"live-{session_id}"
    evidence_root = temp_root / "hbi-g8-pilot-evidence"
    evidence_root.mkdir(parents=True, exist_ok=True)
    log_path = evidence_root / f"api-{session_id}.log"

    try:
        session_dir.mkdir()
    except FileExistsError:
        print(f"REFUSED: session path already exists: {session_dir}", flush=True)
        return 2

    db_path = session_dir / "pilot.db"
    db_url = "sqlite:///" + db_path.as_posix()
    # SQLAlchemy needs four slashes for an absolute POSIX path and three for a
    # Windows drive path. Construct the URL without ever using the repo DB.
    if os.name != "nt":
        db_url = "sqlite:////" + db_path.as_posix().lstrip("/")
    else:
        db_url = "sqlite:///" + db_path.as_posix()

    env = os.environ.copy()
    env["HBI_ENV"] = "development"
    env["DATABASE_URL"] = db_url
    env["HBI_CORS_ORIGINS"] = f"http://{HOST}:4173,http://localhost:4173"
    env.pop("HBI_ADMIN_USERNAME", None)
    env.pop("HBI_ADMIN_PASSWORD", None)

    command = [
        sys.executable, "-m", "uvicorn", "app.main:app",
        "--host", HOST, "--port", str(PORT), "--no-access-log",
    ]
    print(f"G8_SESSION={session_id}", flush=True)
    print(f"DATABASE_URL={db_url}", flush=True)
    print(f"API_DOCS=http://{HOST}:{PORT}/docs", flush=True)
    print(f"HEALTH={HEALTH_URL}", flush=True)
    print(f"API_LOG={log_path}", flush=True)
    print("MODE=EMPTY_ISOLATED_DATABASE; NO_FIXTURES; NO_AUTO_ACTIVATION", flush=True)

    process = None
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
                    print("PILOT_API_READY=YES", flush=True)
                    print("OPERATOR_ACTION: use /docs and record raw request/response evidence.", flush=True)
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
        cleanup_ok = _remove_disposable_db(session_dir, db_path)
        print(f"DATABASE_CLEANUP={'PASS' if cleanup_ok else 'FAIL'}", flush=True)
        print(f"API_LOG_RETAINED={log_path}", flush=True)

    return 0 if cleanup_ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
