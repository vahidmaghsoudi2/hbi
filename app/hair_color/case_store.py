"""Durable, versioned case intake and audit storage for Hair Color Consultation.

This service persists user-provided intake snapshots and workflow events only.
It does not calculate or recommend shades, formulas, products, or chemical steps.
SQLite is used as a small deployment-neutral persistence layer; callers may later
replace it behind this API with a production database adapter.
"""
from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, Mapping


class CaseStoreError(ValueError):
    """Invalid case operation or request."""


class CaseNotFound(CaseStoreError):
    """Case reference does not exist."""


class StaleCaseVersion(CaseStoreError):
    """Caller supplied an outdated version."""


class StoppedCase(CaseStoreError):
    """Case is stopped and cannot be updated or resumed."""


@dataclass(frozen=True)
class HairColorCaseSnapshot:
    case_ref: str
    case_version: int
    target_version: int
    state: str
    intake: dict[str, str]
    created_event_id: str
    updated_event_id: str


class HairColorCaseStore:
    """SQLite-backed case snapshots with optimistic concurrency and audit events."""

    def __init__(self, database_path: str | Path):
        path = Path(database_path)
        if str(path) == ":memory:":
            raise CaseStoreError("SQLite case store requires a persistent file path")
        path.parent.mkdir(parents=True, exist_ok=True)
        self.database_path = str(path)
        self._initialize()
        # Keep local case data private to the service account on POSIX systems.
        try:
            os.chmod(self.database_path, 0o600)
        except OSError:
            # Permission enforcement is platform/filesystem-specific; callers must
            # still provision the parent directory and database securely.
            pass

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path, timeout=10.0)
        try:
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute("PRAGMA busy_timeout = 10000")
            connection.execute("PRAGMA synchronous = FULL")
            yield connection
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connect() as db:
            db.execute("PRAGMA journal_mode = WAL")
            current_version = db.execute("PRAGMA user_version").fetchone()[0]
            if current_version not in (0, 1):
                raise CaseStoreError(f"unsupported case-store schema version: {current_version}")
            db.executescript("""
                CREATE TABLE IF NOT EXISTS hair_color_cases (
                    case_ref TEXT PRIMARY KEY,
                    case_version INTEGER NOT NULL CHECK(case_version >= 1),
                    target_version INTEGER NOT NULL CHECK(target_version >= 1),
                    state TEXT NOT NULL CHECK(state IN ('ACTIVE','STOPPED','CLOSED')),
                    intake_json TEXT NOT NULL,
                    created_event_id TEXT NOT NULL,
                    updated_event_id TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS hair_color_case_events (
                    case_ref TEXT NOT NULL,
                    event_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    case_version INTEGER NOT NULL,
                    target_version INTEGER NOT NULL,
                    payload_json TEXT NOT NULL,
                    PRIMARY KEY(case_ref, event_id),
                    FOREIGN KEY(case_ref) REFERENCES hair_color_cases(case_ref)
                );
            """)
            db.execute("PRAGMA user_version = 1")

    def integrity_check(self) -> str:
        """Return SQLite's integrity-check result; expected value is 'ok'."""
        with self._connect() as db:
            result = db.execute("PRAGMA integrity_check").fetchone()[0]
        return str(result)

    def backup_to(self, destination: str | Path) -> Path:
        """Create a consistent SQLite backup and verify its integrity before returning."""
        target = Path(destination)
        if target.resolve() == Path(self.database_path).resolve():
            raise CaseStoreError("backup destination must differ from source database")
        if target.exists():
            raise CaseStoreError("backup destination already exists; choose a new backup filename")
        target.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as source:
            with sqlite3.connect(str(target)) as backup_db:
                source.backup(backup_db)
                check = backup_db.execute("PRAGMA integrity_check").fetchone()[0]
                if check != "ok":
                    raise CaseStoreError("backup integrity check failed")
        try:
            os.chmod(target, 0o600)
        except OSError:
            pass
        return target

    @staticmethod
    def _required_text(value: Any, field: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise CaseStoreError(f"{field} must be a non-empty string")
        return value.strip()

    @staticmethod
    def _validate_version(value: Any, name: str) -> int:
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise CaseStoreError(f"{name} must be a positive integer")
        return value

    @staticmethod
    def _normalize_intake(intake: Mapping[str, Any]) -> dict[str, str]:
        if not isinstance(intake, Mapping):
            raise CaseStoreError("intake must be a mapping")
        normalized: dict[str, str] = {}
        for key, value in intake.items():
            if not isinstance(key, str) or not key.strip():
                raise CaseStoreError("intake keys must be non-empty strings")
            if not isinstance(value, str):
                raise CaseStoreError("intake values must be strings")
            normalized_key = key.strip()
            if normalized_key in normalized:
                raise CaseStoreError("intake keys must be unique after normalization")
            normalized[normalized_key] = value.strip()
        return normalized

    def create_case(self, *, case_ref: str, event_id: str, intake: Mapping[str, Any]) -> HairColorCaseSnapshot:
        case_ref = self._required_text(case_ref, "case_ref")
        event_id = self._required_text(event_id, "event_id")
        normalized = self._normalize_intake(intake)
        payload = json.dumps({"intake_fields": sorted(normalized)}, ensure_ascii=False)
        with self._connect() as db:
            try:
                db.execute("BEGIN IMMEDIATE")
                db.execute(
                    "INSERT INTO hair_color_cases VALUES(?,?,?,?,?,?,?)",
                    (case_ref, 1, 1, "ACTIVE", json.dumps(normalized, ensure_ascii=False), event_id, event_id),
                )
                db.execute(
                    "INSERT INTO hair_color_case_events VALUES(?,?,?,?,?,?)",
                    (case_ref, event_id, "CASE_CREATED", 1, 1, payload),
                )
                db.commit()
            except sqlite3.IntegrityError as exc:
                db.rollback()
                raise CaseStoreError("case_ref or event_id already exists for this case") from exc
        return self.get_case(case_ref)

    def get_case(self, case_ref: str) -> HairColorCaseSnapshot:
        case_ref = self._required_text(case_ref, "case_ref")
        with self._connect() as db:
            row = db.execute("SELECT * FROM hair_color_cases WHERE case_ref=?", (case_ref,)).fetchone()
        if row is None:
            raise CaseNotFound("case not found")
        return HairColorCaseSnapshot(
            case_ref=row["case_ref"],
            case_version=row["case_version"],
            target_version=row["target_version"],
            state=row["state"],
            intake=json.loads(row["intake_json"]),
            created_event_id=row["created_event_id"],
            updated_event_id=row["updated_event_id"],
        )

    def list_events(self, case_ref: str) -> list[dict[str, Any]]:
        case_ref = self._required_text(case_ref, "case_ref")
        self.get_case(case_ref)
        with self._connect() as db:
            rows = db.execute(
                "SELECT event_id,event_type,case_version,target_version,payload_json "
                "FROM hair_color_case_events WHERE case_ref=? ORDER BY rowid",
                (case_ref,),
            ).fetchall()
        return [
            {
                "event_id": row["event_id"],
                "event_type": row["event_type"],
                "case_version": row["case_version"],
                "target_version": row["target_version"],
                "payload": json.loads(row["payload_json"]),
            }
            for row in rows
        ]

    def update_intake(
        self, *, case_ref: str, event_id: str, expected_case_version: int,
        fields: Mapping[str, Any],
    ) -> HairColorCaseSnapshot:
        case_ref = self._required_text(case_ref, "case_ref")
        event_id = self._required_text(event_id, "event_id")
        updates = self._normalize_intake(fields)
        if not updates:
            raise CaseStoreError("at least one changed intake field is required")
        self._validate_version(expected_case_version, "expected_case_version")
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM hair_color_cases WHERE case_ref=?", (case_ref,)).fetchone()
            if row is None:
                db.rollback()
                raise CaseNotFound("case not found")
            if row["state"] != "ACTIVE":
                db.rollback()
                raise StoppedCase("stopped or closed case requires a fresh case")
            if row["case_version"] != expected_case_version:
                db.rollback()
                raise StaleCaseVersion("case version changed; refresh snapshot before updating")
            old = json.loads(row["intake_json"])
            old.update(updates)
            next_version = row["case_version"] + 1
            payload = json.dumps({"changed_fields": sorted(updates)}, ensure_ascii=False)
            db.execute(
                "UPDATE hair_color_cases SET case_version=?,intake_json=?,updated_event_id=? WHERE case_ref=?",
                (next_version, json.dumps(old, ensure_ascii=False), event_id, case_ref),
            )
            try:
                db.execute(
                    "INSERT INTO hair_color_case_events VALUES(?,?,?,?,?,?)",
                    (case_ref, event_id, "INTAKE_UPDATED", next_version, row["target_version"], payload),
                )
            except sqlite3.IntegrityError as exc:
                db.rollback()
                raise CaseStoreError("event_id must be unique within case") from exc
            db.commit()
        return self.get_case(case_ref)

    def change_target(
        self, *, case_ref: str, event_id: str, expected_case_version: int,
        target_description: str,
    ) -> HairColorCaseSnapshot:
        case_ref = self._required_text(case_ref, "case_ref")
        event_id = self._required_text(event_id, "event_id")
        target_description = self._required_text(target_description, "target_description")
        self._validate_version(expected_case_version, "expected_case_version")
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM hair_color_cases WHERE case_ref=?", (case_ref,)).fetchone()
            if row is None:
                db.rollback()
                raise CaseNotFound("case not found")
            if row["state"] != "ACTIVE":
                db.rollback()
                raise StoppedCase("stopped or closed case requires a fresh case")
            if row["case_version"] != expected_case_version:
                db.rollback()
                raise StaleCaseVersion("case version changed; refresh snapshot before target change")
            intake = json.loads(row["intake_json"])
            previous_target = intake.get("desired_result")
            intake["desired_result"] = target_description
            next_case, next_target = row["case_version"] + 1, row["target_version"] + 1
            payload = json.dumps({
                "target_changed": True,
                "previous_target": previous_target,
                "new_target": target_description,
            }, ensure_ascii=False)
            db.execute(
                "UPDATE hair_color_cases SET case_version=?,target_version=?,intake_json=?,updated_event_id=? WHERE case_ref=?",
                (next_case, next_target, json.dumps(intake, ensure_ascii=False), event_id, case_ref),
            )
            try:
                db.execute(
                    "INSERT INTO hair_color_case_events VALUES(?,?,?,?,?,?)",
                    (case_ref, event_id, "TARGET_CHANGED", next_case, next_target, payload),
                )
            except sqlite3.IntegrityError as exc:
                db.rollback()
                raise CaseStoreError("event_id must be unique within case") from exc
            db.commit()
        return self.get_case(case_ref)

    def stop_case(
        self, *, case_ref: str, event_id: str, expected_case_version: int,
        performed_step_refs: tuple[str, ...] = (),
    ) -> HairColorCaseSnapshot:
        case_ref = self._required_text(case_ref, "case_ref")
        event_id = self._required_text(event_id, "event_id")
        self._validate_version(expected_case_version, "expected_case_version")
        if not isinstance(performed_step_refs, tuple) or any(not isinstance(ref, str) for ref in performed_step_refs):
            raise CaseStoreError("performed_step_refs must be a tuple of strings")
        refs = list(dict.fromkeys(ref.strip() for ref in performed_step_refs if ref.strip()))
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM hair_color_cases WHERE case_ref=?", (case_ref,)).fetchone()
            if row is None:
                db.rollback()
                raise CaseNotFound("case not found")
            if row["state"] != "ACTIVE":
                db.rollback()
                raise StoppedCase("case already stopped or closed")
            if row["case_version"] != expected_case_version:
                db.rollback()
                raise StaleCaseVersion("case version changed; refresh snapshot before stopping")
            payload = json.dumps({"performed_step_refs": refs}, ensure_ascii=False)
            next_version = row["case_version"] + 1
            db.execute(
                "UPDATE hair_color_cases SET case_version=?,state='STOPPED',updated_event_id=? WHERE case_ref=?",
                (next_version, event_id, case_ref),
            )
            try:
                db.execute(
                    "INSERT INTO hair_color_case_events VALUES(?,?,?,?,?,?)",
                    (case_ref, event_id, "STOP_REQUESTED", next_version, row["target_version"], payload),
                )
            except sqlite3.IntegrityError as exc:
                db.rollback()
                raise CaseStoreError("event_id must be unique within case") from exc
            db.commit()
        return self.get_case(case_ref)


    def record_client_decision(
        self, *, case_ref: str, event_id: str, expected_case_version: int,
        expected_target_version: int, decision: str, suggestion_ref: str,
        reason: str | None = None,
    ) -> HairColorCaseSnapshot:
        """Persist an explicit accept/reject decision; acceptance never authorizes execution."""
        case_ref = self._required_text(case_ref, "case_ref")
        event_id = self._required_text(event_id, "event_id")
        suggestion_ref = self._required_text(suggestion_ref, "suggestion_ref")
        if decision not in {"ACCEPT", "REJECT"}:
            raise CaseStoreError("decision must be ACCEPT or REJECT")
        if reason is not None:
            reason = self._required_text(reason, "reason")
        self._validate_version(expected_case_version, "expected_case_version")
        self._validate_version(expected_target_version, "expected_target_version")
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM hair_color_cases WHERE case_ref=?", (case_ref,)).fetchone()
            if row is None:
                db.rollback()
                raise CaseNotFound("case not found")
            if row["state"] != "ACTIVE":
                db.rollback()
                raise StoppedCase("stopped or closed case cannot accept decisions")
            if (row["case_version"], row["target_version"]) != (expected_case_version, expected_target_version):
                db.rollback()
                raise StaleCaseVersion("case or target version changed; decision must be re-evaluated")
            prior_events = db.execute(
                "SELECT event_type,payload_json FROM hair_color_case_events "
                "WHERE case_ref=? AND event_type IN ('CLIENT_ACCEPTED','CLIENT_REJECTED')",
                (case_ref,),
            ).fetchall()
            for prior in prior_events:
                prior_payload = json.loads(prior["payload_json"])
                if prior_payload.get("suggestion_ref") == suggestion_ref:
                    db.rollback()
                    raise CaseStoreError(
                        "a client decision is already recorded for this suggestion; rejected suggestions cannot be reactivated"
                    )
            payload = json.dumps({
                "decision": decision,
                "suggestion_ref": suggestion_ref,
                "reason": reason,
                "client_acceptance": decision == "ACCEPT",
                "execution_authorized": False,
            }, ensure_ascii=False)
            try:
                db.execute(
                    "INSERT INTO hair_color_case_events VALUES(?,?,?,?,?,?)",
                    (case_ref, event_id, f"CLIENT_{decision}ED" if decision == "ACCEPT" else "CLIENT_REJECTED",
                     row["case_version"], row["target_version"], payload),
                )
                db.execute("UPDATE hair_color_cases SET updated_event_id=? WHERE case_ref=?", (event_id, case_ref))
            except sqlite3.IntegrityError as exc:
                db.rollback()
                raise CaseStoreError("event_id must be unique within case") from exc
            db.commit()
        return self.get_case(case_ref)

    def record_triage(
        self, *, case_ref: str, event_id: str, expected_case_version: int,
        expected_target_version: int, request_id: str, consultation_status: str,
        reason_codes: tuple[str, ...], safe_summary: str,
    ) -> HairColorCaseSnapshot:
        case_ref = self._required_text(case_ref, "case_ref")
        event_id = self._required_text(event_id, "event_id")
        request_id = self._required_text(request_id, "request_id")
        consultation_status = self._required_text(consultation_status, "consultation_status")
        safe_summary = self._required_text(safe_summary, "safe_summary")
        if not isinstance(reason_codes, tuple) or any(not isinstance(code, str) or not code.strip() for code in reason_codes):
            raise CaseStoreError("reason_codes must be a tuple of non-empty strings")
        if len(set(reason_codes)) != len(reason_codes):
            raise CaseStoreError("reason_codes must be unique")
        self._validate_version(expected_case_version, "expected_case_version")
        self._validate_version(expected_target_version, "expected_target_version")
        allowed_statuses = {"SAFETY_STOP_NO_EXECUTION_SUGGESTION", "OUT_OF_V1_SCOPE", "NEEDS_INFORMATION_OR_TEST", "NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW"}
        if consultation_status not in allowed_statuses:
            raise CaseStoreError("consultation_status is not a triage-only status")
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM hair_color_cases WHERE case_ref=?", (case_ref,)).fetchone()
            if row is None:
                db.rollback()
                raise CaseNotFound("case not found")
            if row["state"] != "ACTIVE":
                db.rollback()
                raise StoppedCase("stopped or closed case cannot be evaluated")
            if (row["case_version"], row["target_version"]) != (expected_case_version, expected_target_version):
                db.rollback()
                raise StaleCaseVersion("case or target version changed; fresh evaluation required")
            prior_triages = db.execute(
                "SELECT payload_json FROM hair_color_case_events "
                "WHERE case_ref=? AND event_type='TRIAGE_RECORDED'",
                (case_ref,),
            ).fetchall()
            if any(json.loads(event["payload_json"]).get("request_id") == request_id for event in prior_triages):
                db.rollback()
                raise CaseStoreError("request_id has already been evaluated for this case")
            payload = json.dumps({
                "request_id": request_id,
                "consultation_status": consultation_status,
                "reason_codes": list(reason_codes),
                "safe_summary": safe_summary,
                "options_count": 0,
                "execution_authorized": False,
            }, ensure_ascii=False)
            try:
                db.execute(
                    "INSERT INTO hair_color_case_events VALUES(?,?,?,?,?,?)",
                    (case_ref, event_id, "TRIAGE_RECORDED", row["case_version"], row["target_version"], payload),
                )
                db.execute("UPDATE hair_color_cases SET updated_event_id=? WHERE case_ref=?", (event_id, case_ref))
            except sqlite3.IntegrityError as exc:
                db.rollback()
                raise CaseStoreError("event_id must be unique within case") from exc
            db.commit()
        return self.get_case(case_ref)

    def close_case(
        self, *, case_ref: str, event_id: str, expected_case_version: int,
        closure_reason: str,
    ) -> HairColorCaseSnapshot:
        case_ref = self._required_text(case_ref, "case_ref")
        event_id = self._required_text(event_id, "event_id")
        closure_reason = self._required_text(closure_reason, "closure_reason")
        self._validate_version(expected_case_version, "expected_case_version")
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM hair_color_cases WHERE case_ref=?", (case_ref,)).fetchone()
            if row is None:
                db.rollback()
                raise CaseNotFound("case not found")
            if row["state"] == "CLOSED":
                db.rollback()
                raise CaseStoreError("case is already closed")
            if row["case_version"] != expected_case_version:
                db.rollback()
                raise StaleCaseVersion("case version changed; refresh snapshot before closing")
            payload = json.dumps({"closure_reason": closure_reason}, ensure_ascii=False)
            next_version = row["case_version"] + 1
            db.execute(
                "UPDATE hair_color_cases SET case_version=?,state='CLOSED',updated_event_id=? WHERE case_ref=?",
                (next_version, event_id, case_ref),
            )
            try:
                db.execute(
                    "INSERT INTO hair_color_case_events VALUES(?,?,?,?,?,?)",
                    (case_ref, event_id, "CASE_CLOSED", next_version, row["target_version"], payload),
                )
            except sqlite3.IntegrityError as exc:
                db.rollback()
                raise CaseStoreError("event_id must be unique within case") from exc
            db.commit()
        return self.get_case(case_ref)

    def fresh_restart(
        self, *, source_case_ref: str, new_case_ref: str, event_id: str,
        intake: Mapping[str, Any],
    ) -> HairColorCaseSnapshot:
        source_case_ref = self._required_text(source_case_ref, "source_case_ref")
        new_case_ref = self._required_text(new_case_ref, "new_case_ref")
        event_id = self._required_text(event_id, "event_id")
        if source_case_ref == new_case_ref:
            raise CaseStoreError("fresh restart must use a distinct case_ref")
        normalized = self._normalize_intake(intake)
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            source = db.execute("SELECT * FROM hair_color_cases WHERE case_ref=?", (source_case_ref,)).fetchone()
            if source is None:
                db.rollback()
                raise CaseNotFound("source case not found")
            if source["state"] != "STOPPED":
                db.rollback()
                raise StoppedCase("fresh restart is permitted only from a stopped source case")
            created_payload = json.dumps({"intake_fields": sorted(normalized)}, ensure_ascii=False)
            source_payload = json.dumps({"source_case_ref": source_case_ref}, ensure_ascii=False)
            backlink_payload = json.dumps({"new_case_ref": new_case_ref}, ensure_ascii=False)
            source_event_id = f"{event_id}:RESTARTED_AS"
            new_case_source_event_id = f"{event_id}:SOURCE"
            try:
                db.execute(
                    "INSERT INTO hair_color_cases VALUES(?,?,?,?,?,?,?)",
                    (new_case_ref, 1, 1, "ACTIVE", json.dumps(normalized, ensure_ascii=False),
                     event_id, new_case_source_event_id),
                )
                db.execute(
                    "INSERT INTO hair_color_case_events VALUES(?,?,?,?,?,?)",
                    (new_case_ref, event_id, "CASE_CREATED", 1, 1, created_payload),
                )
                db.execute(
                    "INSERT INTO hair_color_case_events VALUES(?,?,?,?,?,?)",
                    (new_case_ref, new_case_source_event_id, "FRESH_RESTART_FROM_STOP", 1, 1, source_payload),
                )
                db.execute(
                    "INSERT INTO hair_color_case_events VALUES(?,?,?,?,?,?)",
                    (source_case_ref, source_event_id, "FRESH_RESTARTED_AS",
                     source["case_version"], source["target_version"], backlink_payload),
                )
                db.execute(
                    "UPDATE hair_color_cases SET updated_event_id=? WHERE case_ref=?",
                    (source_event_id, source_case_ref),
                )
            except sqlite3.IntegrityError as exc:
                db.rollback()
                raise CaseStoreError("restart case or audit events already exist") from exc
            db.commit()
        return self.get_case(new_case_ref)
