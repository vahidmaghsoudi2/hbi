# Hair Color Synthetic Case Store — Operations (Prototype)

This document applies only to the **synthetic-only** case API in PR #656. It is not deployment, pilot, production-data, or specialist-consultation approval.

## Storage configuration

- Configure `HBI_HAIR_COLOR_CASE_DB` explicitly with an absolute path to a persistent SQLite file.
- If the variable is absent or blank, the API returns HTTP 503. Do not add a default path.
- The parent directory must be provisioned by the operator and restricted to the service account. The store attempts to set the database file mode to `0600` on POSIX systems; filesystem/platform behavior may vary.
- The SQLite store uses WAL mode, a 10-second busy timeout, foreign-key enforcement, and full synchronous durability.
- The schema version is stored in SQLite `user_version` (currently v2). Unknown versions fail closed rather than silently running.
- Audit events include UTC SQLite timestamps. Migrated v1 records are marked `LEGACY-UNKNOWN` rather than assigned invented timestamps.

## Integrity and backup

The store exposes internal operational methods, not public HTTP endpoints:

```python
from app.hair_color.case_store import HairColorCaseStore

store = HairColorCaseStore(database_path)
assert store.integrity_check() == "ok"
backup = store.backup_to("/restricted/backups/hair-color-case-YYYYMMDD-HHMMSS.sqlite")\nrestored = HairColorCaseStore.restore_from_backup(backup, "/restricted/recovery/hair-color-case-rehearsal.sqlite")
```

- Backups are made using SQLite's backup API (consistent snapshot), then integrity-checked.
- Backup filenames must be unique; existing destination files and symlinks are not overwritten. Backup directories must also be private on POSIX.
- Store and backup file permissions are attempted as `0600`.
- A synthetic restore path is implemented and tested: restore only accepts verified schema-v2 backup files, creates a new destination, and re-checks integrity. It has not been rehearsed on a separate host or production-like infrastructure.
- Added a backup/rotation CLI: `python scripts/hair_color_case_backup.py --backup-dir /restricted/backups/hair-color --retain 14`. It verifies source integrity, creates a timestamped backup, validates it through the store, and prunes older files after successful creation. It is not scheduled by the repository; a deployment owner must configure a scheduler.\n- This prototype does **not** encrypt backups, upload them off-host, provide idempotent API retries, or verify restoration on a separate machine. Those controls require approved infrastructure.
- Recovery rehearsal is not yet verified. Restore only to an isolated synthetic test environment and confirm `PRAGMA integrity_check`, event history, and case snapshots before any further use.

## Scheduling example (operator-owned)\n\nExample daily scheduler entry, only after provisioning private directories and explicit DB/backup paths:\n\n```cron\n0 2 * * * HBI_HAIR_COLOR_CASE_DB=/restricted/app/hair-color.sqlite /usr/bin/python /opt/hbi/scripts/hair_color_case_backup.py --backup-dir /restricted/backups/hair-color --retain 14\n```\n\nThis is an example configuration only; no scheduler has been installed or activated.\n\n## Data and access restrictions

- API accepts only `SYNTHETIC-` identifiers and `SYNTHETIC:` placeholder values.
- Role authorization is required (Reviewer QA, PO, or Admin); no user-facing consultation, real customer intake, candidate publication, or execution authorization is enabled.
- Do not put real customer data, photographs, product records, or chemical history in this prototype database.
- Do not expose SQLite files, WAL/SHM files, backups, or logs through static web paths or shared/public storage.

## Current operational boundary

SQLite is a test/prototype persistence adapter. Before any production use, an owner must decide and validate production database hosting, access management, encryption, backup scheduling/retention, restore drills, monitoring/alerting, incident response, migration management, and audit retention. No production or pilot authorization is implied.
