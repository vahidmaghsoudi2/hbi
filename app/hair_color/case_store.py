"""Durable, versioned case intake and audit storage for Hair Color Consultation.

This service persists user-provided intake snapshots and workflow events only.
It does not calculate or recommend shades, formulas, products, or chemical steps.
SQLite is used as a small deployment-neutral persistence layer; callers may later
replace it behind this API with a production database adapter.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


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
        self.database_path = str(database_path)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=10.0)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as db:
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

    @staticmethod
    def _required_text(value: Any, field: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise CaseStoreError(f"{field} must be a non-empty string")
        return value.strip()

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
            normalized[key.strip()] = value.strip()
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
        if isinstance(expected_case_version, bool) or not isinstance(expected_case_version, int) or expected_case_version < 1:
            raise CaseStoreError("expected_case_version must be a positive integer")
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
    ) -> HairColorCaseSnapshot:
        case_ref = self._required_text(case_ref, "case_ref")
        event_id = self._required_text(event_id, "event_id")
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
            next_case, next_target = row["case_version"] + 1, row["target_version"] + 1
            payload = json.dumps({"target_changed": True}, ensure_ascii=False)
            db.execute(
                "UPDATE hair_color_cases SET case_version=?,target_version=?,updated_event_id=? WHERE case_ref=?",
                (next_case, next_target, event_id, case_ref),
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
            db.execute(
                "UPDATE hair_color_cases SET state='STOPPED',updated_event_id=? WHERE case_ref=?",
                (event_id, case_ref),
            )
            try:
                db.execute(
                    "INSERT INTO hair_color_case_events VALUES(?,?,?,?,?,?)",
                    (case_ref, event_id, "STOP_REQUESTED", row["case_version"], row["target_version"], payload),
                )
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
        if not isinstance(reason_codes, tuple) or any(not isinstance(code, str) for code in reason_codes):
            raise CaseStoreError("reason_codes must be a tuple of strings")
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
            db.execute(
                "UPDATE hair_color_cases SET state='CLOSED',updated_event_id=? WHERE case_ref=?",
                (event_id, case_ref),
            )
            try:
                db.execute(
                    "INSERT INTO hair_color_case_events VALUES(?,?,?,?,?,?)",
                    (case_ref, event_id, "CASE_CLOSED", row["case_version"], row["target_version"], payload),
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
            source = db.execute("SELECT state FROM hair_color_cases WHERE case_ref=?", (source_case_ref,)).fetchone()
            if source is None:
                db.rollback()
                raise CaseNotFound("source case not found")
            if source["state"] != "STOPPED":
                db.rollback()
                raise StoppedCase("fresh restart is permitted only from a stopped source case")
            created_payload = json.dumps({"intake_fields": sorted(normalized)}, ensure_ascii=False)
            source_payload = json.dumps({"source_case_ref": source_case_ref}, ensure_ascii=False)
            try:
                db.execute(
                    "INSERT INTO hair_color_cases VALUES(?,?,?,?,?,?,?)",
                    (new_case_ref, 1, 1, "ACTIVE", json.dumps(normalized, ensure_ascii=False), event_id, event_id),
                )
                db.execute(
                    "INSERT INTO hair_color_case_events VALUES(?,?,?,?,?,?)",
                    (new_case_ref, event_id, "CASE_CREATED", 1, 1, created_payload),
                )
                db.execute(
                    "INSERT INTO hair_color_case_events VALUES(?,?,?,?,?,?)",
                    (new_case_ref, f"{event_id}:SOURCE", "FRESH_RESTART_FROM_STOP", 1, 1, source_payload),
                )
            except sqlite3.IntegrityError as exc:
                db.rollback()
                raise CaseStoreError("restart case or audit events already exist") from exc
            db.commit()
        return self.get_case(new_case_ref)
