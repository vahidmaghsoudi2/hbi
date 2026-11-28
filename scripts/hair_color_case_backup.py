#!/usr/bin/env python3
"""Synthetic Hair Color SQLite backup utility.

Run from the repository root with HBI_HAIR_COLOR_CASE_DB configured to an
absolute path and a private backup directory. Does not handle encryption or
off-host replication; those are deployment controls.
"""
from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.hair_color.case_store import HairColorCaseStore, CaseStoreError


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backup-dir", required=True, help="Private directory (POSIX 0700 or stricter)")
    parser.add_argument("--retain", type=int, default=14, help="Keep this many newest backups (default 14)")
    args = parser.parse_args()
    if args.retain < 1:
        parser.error("--retain must be at least 1")
    db_path = os.getenv("HBI_HAIR_COLOR_CASE_DB", "").strip()
    if not db_path:
        parser.error("HBI_HAIR_COLOR_CASE_DB must be configured")
    source = Path(db_path)
    if not source.is_absolute():
        parser.error("HBI_HAIR_COLOR_CASE_DB must be an absolute path")
    backup_dir = Path(args.backup_dir)
    if not backup_dir.is_absolute():
        parser.error("--backup-dir must be an absolute path")
    backup_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    if os.name == "posix" and backup_dir.stat().st_mode & 0o077:
        parser.error("backup directory must be private (mode 0700 or stricter)")
    store = HairColorCaseStore(source)
    if store.integrity_check() != "ok":
        raise SystemExit("Source store failed integrity/foreign-key check; backup aborted.")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = backup_dir / f"hair-color-case-{stamp}.sqlite"
    try:
        created = store.backup_to(target)
    except CaseStoreError as exc:
        raise SystemExit(f"Backup failed: {exc}") from exc
    backups = sorted(backup_dir.glob("hair-color-case-*.sqlite"), key=lambda p: p.stat().st_mtime, reverse=True)
    for stale in backups[args.retain:]:
        if stale.is_symlink():
            continue
        stale.unlink()
    print(f"Verified synthetic case-store backup: {created}")
    print(f"Retained backup files: {min(len(backups), args.retain)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
