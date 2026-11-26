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
import shutil
import socket
import sqlite3
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

DEFAULT_CANDIDATE = "G8-NUMBUZIN-NO9-20261018"
MAX_SEARCH_SCAN_BYTES = 256 * 1024 * 1024
MAX_PACKAGE_FILE_BYTES = 100 * 1024 * 1024
MAX_PACKAGE_TOTAL_BYTES = 500 * 1024 * 1024
PILOT_HOST = "127.0.0.1"
PILOT_PORT = 8765


def _refuse_if_pilot_api_running() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(0.25)
        try:
            probe.connect((PILOT_HOST, PILOT_PORT))
        except OSError:
            return
        raise RuntimeError(
            f"pilot API appears active at {PILOT_HOST}:{PILOT_PORT}; stop it normally before artifact recovery"
        )


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


def _file_contains_token(path: Path, token: bytes) -> bool:
    try:
        size = path.stat().st_size
        if size > MAX_SEARCH_SCAN_BYTES:
            return False
        overlap = max(0, len(token) - 1)
        tail = b""
        with path.open("rb") as stream:
            while True:
                chunk = stream.read(1024 * 1024)
                if not chunk:
                    return False
                combined = tail + chunk
                if token in combined.lower():
                    return True
                tail = combined[-overlap:] if overlap else b""
    except OSError:
        return False


def _contains_candidate(folder: Path, candidate: str) -> bool:
    token = candidate.casefold().encode("utf-8")
    for path in _safe_files(folder):
        if path.suffix.casefold() not in {".json", ".log", ".txt", ".md"}:
            continue
        if _file_contains_token(path, token):
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
    # Work on byte-copies so SQLite cannot create/change source WAL/SHM files
    # while opening a read-only source connection.
    source_copy = output_db.with_name(output_db.name + ".source-copy")
    source_sidecars = [Path(str(source_db) + suffix) for suffix in ("-wal", "-shm")]
    copied_sidecars: list[Path] = []
    try:
        if source_copy.exists() or source_copy.is_symlink():
            raise RuntimeError(f"temporary source copy already exists: {source_copy}")
        shutil.copy2(source_db, source_copy)
        for sidecar in source_sidecars:
            if sidecar.is_symlink():
                raise RuntimeError(f"refusing source sidecar symlink: {sidecar}")
            if sidecar.is_file():
                suffix = sidecar.name[len(source_db.name):]
                copied = Path(str(source_copy) + suffix)
                shutil.copy2(sidecar, copied)
                copied_sidecars.append(copied)
        uri = source_copy.resolve().as_uri() + "?mode=ro"
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
    finally:
        source_copy.unlink(missing_ok=True)
        for copied in copied_sidecars:
            copied.unlink(missing_ok=True)


def recover(
    *,
    temp_root: Path,
    candidate: str,
    output_zip: Path,
    source_session: Path | None = None,
    database_path: Path | None = None,
) -> dict[str, object]:
    _refuse_if_pilot_api_running()
    temp_root = temp_root.resolve()
    evidence_root = temp_root / "hbi-g8-pilot-evidence"
    pilot_root = temp_root / "hbi-g8-pilot"
    if evidence_root.is_symlink() or pilot_root.is_symlink():
        raise RuntimeError("refusing symlinked G8 temporary roots")
    if source_session is not None:
        if source_session.is_symlink():
            raise RuntimeError("explicit source session must not be a symlink")
        source_folder = source_session.expanduser().resolve()
        if not source_folder.is_dir() or not _contains_candidate(source_folder, candidate):
            raise RuntimeError(f"explicit source session is missing or candidate not found: {source_folder}")
        matches = [source_folder]
    else:
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
    output_requested = output_zip.expanduser()
    if output_requested.exists() or output_requested.is_symlink():
        raise RuntimeError(f"recovery output already exists or is a symlink; refusing overwrite: {output_requested}")
    output_zip = output_requested.resolve()
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

            if database_path is not None and database_path.is_symlink():
                raise RuntimeError("explicit database source must not be a symlink")
            db_source = (
                database_path.expanduser().resolve()
                if database_path is not None
                else pilot_root / f"live-{session_folder.name}" / "pilot.db"
            )
            if db_source.is_symlink():
                raise RuntimeError(f"database source must not be a symlink: {db_source}")
            if db_source.exists() and not db_source.is_file():
                raise RuntimeError(f"database source is not a regular file: {db_source}")
            if database_path is not None and not db_source.is_file():
                raise RuntimeError(f"explicit database source is missing: {db_source}")
            if database_path is None and db_source.parent.is_symlink():
                raise RuntimeError(f"pilot session database directory must not be a symlink: {db_source.parent}")
            if database_path is None:
                try:
                    db_source.resolve().relative_to(pilot_root.resolve())
                except ValueError as exc:
                    raise RuntimeError(f"pilot database path escapes its isolated root: {db_source}") from exc
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
                "source_session_directory": str(session_folder.resolve()),
                "database_source_path": str(db_source.resolve()) if db_info is not None else None,
                "database_backup": db_info,
                "source_files_are_unchanged": True,
                "artifacts": artifact_manifest,
            }
            archive.writestr(
                "recovery-manifest.json",
                json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            )
        # Re-open and verify every archived artifact before publishing the ZIP.
        with zipfile.ZipFile(temp_package, "r") as verification:
            for item in artifact_manifest:
                archived_path = str(item["path"])
                digest = hashlib.sha256()
                size = 0
                with verification.open(archived_path) as stream:
                    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                        digest.update(chunk)
                        size += len(chunk)
                if digest.hexdigest() != item["sha256"] or size != item["size_bytes"]:
                    raise RuntimeError(f"recovery ZIP integrity verification failed: {archived_path}")
            parsed_manifest = json.loads(verification.read("recovery-manifest.json"))
            if parsed_manifest.get("candidate") != candidate or len(parsed_manifest.get("artifacts", [])) != len(artifact_manifest):
                raise RuntimeError("recovery ZIP manifest verification failed")
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
    parser.add_argument("--source-session", type=Path, help="Optional explicit evidence folder (for a backup/export)")
    parser.add_argument("--database", type=Path, help="Optional explicit SQLite DB path (opened read-only via a copied working set)")
    parser.add_argument("--output", type=Path, required=True, help="Recovery ZIP path; must be outside source session")
    args = parser.parse_args()
    try:
        result = recover(
            temp_root=args.temp_root,
            candidate=args.candidate,
            output_zip=args.output,
            source_session=args.source_session,
            database_path=args.database,
        )
    except (OSError, RuntimeError, sqlite3.Error, zipfile.BadZipFile) as exc:
        print(f"RECOVERY_REFUSED: {type(exc).__name__}: {exc}")
        return 2
    print("RECOVERY=PASS")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
