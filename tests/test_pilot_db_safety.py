"""Safety regression tests for the disposable Playwright fixture builder."""
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "prepare_pilot_browser_db.py"


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


def test_isolated_g8_runner_smoke_starts_and_cleans_its_database() -> None:
    from sqlalchemy.engine import make_url

    env = os.environ.copy()
    env["HBI_ENV"] = "development"
    env.pop("DATABASE_URL", None)
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "run_g8_isolated_pilot.py"), "--smoke-test"],
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
    assert "DATABASE_CLEANUP=PASS" in output

    db_url_line = next(line for line in output.splitlines() if line.startswith("DATABASE_URL="))
    db_path = Path(make_url(db_url_line.split("=", 1)[1]).database)
    assert not db_path.exists()

    log_line = next(line for line in output.splitlines() if line.startswith("API_LOG_RETAINED="))
    assert Path(log_line.split("=", 1)[1]).is_file()
