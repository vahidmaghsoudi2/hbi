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
