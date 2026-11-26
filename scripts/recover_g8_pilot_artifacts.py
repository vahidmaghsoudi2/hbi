"""Recover existing G8 pilot artifacts without changing source files or databases.

This utility is read-only against the operator's temporary pilot/evidence directories.
It creates a separate recovery ZIP containing matched evidence, an SQLite backup
snapshot (when the matching DB exists), and a SHA-256 manifest. It never starts
the API, calls the pilot API, resolves evidence, or cleans up source paths.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

DEFAULT_CANDIDATE = "G8-NUMBUZIN-NO9-20261018"
MAX_SEARCH_FILE_BYTES = 2 * 1024 * 1024
MAX_PACKAGE_FILE_BYTES = 100 * 1024 * 1024
MAX_PACKAGE_TOTAL_BYTES = 500 * 1024 * 1024


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _safe_files(root: Path) -> Iterable[Path]:
    if not root.exists() or root.is_symlink() or not root.is_dir():
        return
    for path in root.rglob("*"):
        if path.is_symlink():
            continue
        if path.is_file():
            yield path


def _contains_candidate(folder: Path, candidate: str) -> bool:
    token = candidate.casefold()
    for path in _safe_files(folder):
        if path.suffix.casefold() not in {".json", ".log", ".txt", ".md"}:
            continue
        try:
            if path.stat().st_size > MAX_SEARCH_FILE_BYTES:
                continue
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if token in content.casefold():
            return True
    return False


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sqlite_readonly_backup(source_db: Path, output_db: Path) -> dict[str, object]:
    if source_db.is_symlink() or not source_db.is_file():
        raise RuntimeError(f"unsafe or missing source database: {source_db}")
    uri = source_db.resolve().as_uri() + "?mode=ro"
    source = sqlite3.connect(uri, uri=True, timeout=5)
    destination = sqlite3.connect(str(output_db))
    try:
        integrity = source.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise RuntimeError(f"source SQLite integrity_check failed: {integrity}")
        source.backup(destination)
        destination.commit()
    finally:
        destination.close()
        source.close()
    with sqlite3.connect(str(output_db)) as verify:
        integrity_copy = verify.execute("PRAGMA integrity_check").fetchone()[0]
        tables = [
            row[0] for row in verify.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
        ]
    if integrity_copy != "ok":
        raise RuntimeError(f"recovery SQLite backup integrity check failed: {integrity_copy}")
    return {"integrity_check": "ok", "table_names": tables}


def recover(
    *,
    temp_root: Path,
    candidate: str,
    output_zip: Path,
) -> dict[str, object]:
    temp_root = temp_root.resolve()
    evidence_root = temp_root / "hbi-g8-pilot-evidence"
    pilot_root = temp_root / "hbi-g8-pilot"
    if evidence_root.is_symlink() or pilot_root.is_symlink():
        raise RuntimeError("refusing symlinked G8 temporary roots")
    if not evidence_root.is_dir():
        raise RuntimeError(f"evidence root not found: {evidence_root}")

    matches = [
        folder for folder in evidence_root.iterdir()
        if folder.is_dir() and not folder.is_symlink() and _contains_candidate(folder, candidate)
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"expected exactly one evidence session matching candidate {candidate!r}; found {len(matches)}. "
            "No source files were changed."
        )
    session_folder = matches[0]
    output_zip = output_zip.expanduser().resolve()
    if output_zip == session_folder or session_folder in output_zip.parents:
        raise RuntimeError("recovery output must not be written inside the source evidence session")
    output_zip.parent.mkdir(parents=True, exist_ok=True)

    temp_package = output_zip.with_suffix(output_zip.suffix + ".working")
    if temp_package.exists() or temp_package.is_symlink():
        raise RuntimeError(f"temporary recovery output already exists: {temp_package}")
    try:
        with zipfile.ZipFile(temp_package, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            artifact_manifest: list[dict[str, object]] = []
            total = 0
            for source in sorted(_safe_files(session_folder)):
                size = source.stat().st_size
                if size > MAX_PACKAGE_FILE_BYTES:
                    raise RuntimeError(f"artifact exceeds per-file size limit: {source}")
                total += size
                if total > MAX_PACKAGE_TOTAL_BYTES:
                    raise RuntimeError("source evidence exceeds total package size limit")
                relative = source.relative_to(session_folder).as_posix()
                archive.write(source, f"source-evidence/{relative}")
                artifact_manifest.append({
                    "path": f"source-evidence/{relative}",
                    "size_bytes": size,
                    "sha256": _sha256(source),
                })

            db_source = pilot_root / f"live-{session_folder.name}" / "pilot.db"
            db_info: dict[str, object] | None = None
            if db_source.is_file() and not db_source.is_symlink():
                db_copy = output_zip.parent / (output_zip.stem + ".recovered.sqlite")
                if db_copy.exists() or db_copy.is_symlink():
                    raise RuntimeError(f"recovery DB output already exists: {db_copy}")
                try:
                    db_info = _sqlite_readonly_backup(db_source, db_copy)
                    size = db_copy.stat().st_size
                    total += size
                    if size > MAX_PACKAGE_FILE_BYTES or total > MAX_PACKAGE_TOTAL_BYTES:
                        raise RuntimeError("recovered DB exceeds package size limits")
                    archive.write(db_copy, "recovered-database/pilot-readonly-backup.sqlite")
                    artifact_manifest.append({
                        "path": "recovered-database/pilot-readonly-backup.sqlite",
                        "size_bytes": size,
                        "sha256": _sha256(db_copy),
                    })
                finally:
                    db_copy.unlink(missing_ok=True)

            manifest = {
                "schema": "hbi.g8.recovery-package.v1",
                "candidate": candidate,
                "matched_evidence_session": session_folder.name,
                "recovered_at_utc": _utc_now(),
                "source_roots": {
                    "evidence_root": str(evidence_root),
                    "pilot_root": str(pilot_root),
                },
                "database_backup": db_info,
                "source_files_are_unchanged": True,
                "artifacts": artifact_manifest,
            }
            archive.writestr(
                "recovery-manifest.json",
                json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            )
        os.replace(temp_package, output_zip)
    except Exception:
        temp_package.unlink(missing_ok=True)
        raise
    return {
        "candidate": candidate,
        "matched_session": session_folder.name,
        "package": str(output_zip),
        "artifact_count": len(artifact_manifest),
        "database_backup": db_info is not None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", default=DEFAULT_CANDIDATE)
    parser.add_argument("--temp-root", type=Path, default=Path(tempfile.gettempdir()))
    parser.add_argument("--output", type=Path, required=True, help="Recovery ZIP path; must be outside source session")
    args = parser.parse_args()
    try:
        result = recover(temp_root=args.temp_root, candidate=args.candidate, output_zip=args.output)
    except (OSError, RuntimeError, sqlite3.Error, zipfile.BadZipFile) as exc:
        print(f"RECOVERY_REFUSED: {type(exc).__name__}: {exc}")
        return 2
    print("RECOVERY=PASS")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
