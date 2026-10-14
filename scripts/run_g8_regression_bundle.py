"""Run the repeatable G8-related regression bundle and retain traceable local evidence.

This bundle uses the repository's pytest fixtures (currently in-memory SQLite).
It is supporting regression evidence only; it does NOT execute or certify the real
operator G8 pilot, production isolation, or acceptance criteria A1-A9.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

TESTS = (
    "tests/test_wp01_intake_duplicate_gate.py",
    "tests/test_wp02_skin_safety_before_approve.py",
    "tests/test_catalog_intake_engine_ready_path.py",
    "tests/test_claim_taxonomy_contract.py",
    "tests/test_manufacturer_claim_mapping_guard.py",
    "tests/test_evidence_missing_hard_gate.py",
    "tests/test_product_intake_auth.py",
    "tests/test_gap04_recommendation_persistence.py",
)


def _run(command: list[str], cwd: Path) -> tuple[int, str]:
    result = subprocess.run(
        command, cwd=cwd, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, check=False,
    )
    return result.returncode, result.stdout


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    session = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    evidence_root = Path(tempfile.gettempdir()) / "hbi-g8-regression-evidence"
    evidence_root.mkdir(parents=True, exist_ok=True)
    log_path = evidence_root / f"pytest-{session}.log"
    report_path = evidence_root / f"report-{session}.md"

    sha_code, sha_output = _run(["git", "rev-parse", "HEAD"], root)
    sha = sha_output.strip() if sha_code == 0 else "UNAVAILABLE"
    branch_code, branch_output = _run(["git", "branch", "--show-current"], root)
    branch = branch_output.strip() if branch_code == 0 else "UNAVAILABLE"

    missing = [name for name in TESTS if not (root / name).is_file()]
    if missing:
        output = "REFUSED: required regression test files are missing:\n" + "\n".join(missing)
        log_path.write_text(output + "\n", encoding="utf-8")
        print(output)
        print(f"EVIDENCE_LOG={log_path}")
        return 2

    command = [sys.executable, "-m", "pytest", "-q", *TESTS]
    print("G8_REGRESSION_BUNDLE=START", flush=True)
    print(f"CODE_SHA={sha}", flush=True)
    print(f"BRANCH={branch}", flush=True)
    print(f"TEST_COUNT={len(TESTS)}", flush=True)
    print(f"EVIDENCE_DIR={evidence_root}", flush=True)

    try:
        return_code, output = _run(command, root)
    except OSError as exc:
        return_code, output = 127, f"Unable to launch pytest: {exc}"
    log_path.write_text(output, encoding="utf-8")

    status = "PASS" if return_code == 0 else "FAIL"
    report = [
        "# G8 Regression Bundle — Supporting Evidence",
        "",
        f"- Session (UTC): `{session}`",
        f"- Code SHA: `{sha}`",
        f"- Branch: `{branch}`",
        f"- Result: **{status}** (pytest exit code {return_code})",
        f"- Raw pytest output: `{log_path}`",
        "",
        "## Test files",
        *[f"- `{name}`" for name in TESTS],
        "",
        "## Interpretation",
        "",
        "This is automated regression evidence using the repository's pytest fixtures,",
        "which currently use an in-memory SQLite database. It is not a real operator",
        "session and does not prove production isolation or the complete A1–A9 acceptance",
        "criteria. Do not use this report alone to change G8 from BLOCKED / NOT VERIFIED.",
        "",
        "## Pytest output",
        "",
        "```text",
        output.rstrip(),
        "```",
        "",
    ]
    report_path.write_text("\n".join(report), encoding="utf-8")
    print(output, end="" if output.endswith("\n") else "\n")
    print(f"G8_REGRESSION_BUNDLE={status}")
    print(f"PYTEST_EXIT_CODE={return_code}")
    print(f"RAW_LOG={log_path}")
    print(f"REPORT={report_path}")
    print("G8_ACCEPTANCE=A1-A9 NOT CERTIFIED BY THIS BUNDLE")
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
