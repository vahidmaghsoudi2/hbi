# G8 Historical Pilot Artifact Recovery (Read-Only)

## Purpose

Recover the original 2026-10-18 isolated G8 pilot artifacts, if they still exist on the operator Windows machine. This is recovery only—not a pilot rerun, evidence resolution, verification, approval, activation, or G8 acceptance.

## Source roots scanned

The utility reads these directories under the Windows temporary root:

- `%TEMP%/hbi-g8-pilot-evidence/`
- `%TEMP%/hbi-g8-pilot/`

It matches exactly one evidence-session folder by finding the candidate ID in text/JSON/log files. It archives the source evidence as-is and, if a matching `live-<session-folder>/pilot.db` exists, creates a read-only SQLite backup snapshot in the package. Source files are never moved, deleted, or edited.

## Run on the operator machine

Run recovery only after the pilot API process is confirmed stopped; do not terminate an active process to force recovery. The utility copies the SQLite main file and existing WAL/SHM sidecars to a temporary recovery workspace, opens only that copy read-only, and removes only its own temporary copy after a verified backup.

From the repository checkout containing this utility (after bringing in PR #665's branch or approved version), run this single PowerShell command:

```powershell
./.venv/Scripts/python.exe scripts/recover_g8_pilot_artifacts.py --candidate G8-NUMBUZIN-NO9-20261018 --output "$env:TEMP/hbi-g8-recovered-20261018.zip"
```

The output path must not already exist. On success, the utility prints `RECOVERY=PASS` and a JSON summary. On zero or multiple matches, unsafe roots, integrity failure, or file-size limits, it prints `RECOVERY_REFUSED` and exits without modifying source files.

For files restored from a backup at non-default locations, the utility also accepts explicit `--source-session` and `--database` paths. Use those only for the actual backup evidence directory and DB file; paths are read-only and symlink sources are refused. The output ZIP must still be a new path outside the source session.

## Package contents

- Original evidence files from the matched evidence session folder, including API logs/raw HTTP capture/readback/metadata/manifests if present.
- A read-only SQLite backup snapshot of the associated pilot database, if present and readable.
- `recovery-manifest.json` with candidate/session identity, recovery timestamp, source roots, DB integrity summary, and SHA-256 hashes for included artifacts.

## After recovery

Upload/share the ZIP for independent review. Do not call the live pilot API, resolve the reported evidence conflict, mark evidence VERIFIED/APPROVED, refresh Product Knowledge, activate the product, or delete source data. If the utility reports no match or the original package is absent, do not reconstruct it from Issue #386 narrative. A new pilot may be considered only after the existing preflight boundary and approved contract are satisfied.

## Safety limits

- No outbound/network API calls; it performs a local loopback port check to refuse recovery while the pilot API is active.
- Source SQLite is opened read-only; the backup is written separately and verified.
- Symlinked roots/files are refused or skipped.
- Exactly one matching session is required.
- Per-file and total size limits prevent unexpectedly large packages.
- Existing output files are never overwritten.
- Recovery utility does not clean up any source path.
