"""Application service joining durable synthetic case storage to triage.

All identifiers must carry the SYNTHETIC- prefix. The service never accepts real
client records, never emits candidates, and records only a safe triage summary.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .case_store import HairColorCaseStore, StoppedCase
from .consultation import run_consultation_from_intake_persian


class HairColorCaseServiceError(ValueError):
    """Invalid application-service request."""


class HairColorCaseService:
    def __init__(self, store: HairColorCaseStore):
        self.store = store

    @staticmethod
    def _synthetic_id(value: str, name: str) -> str:
        if not isinstance(value, str) or not value.startswith("SYNTHETIC-") or not value.strip():
            raise HairColorCaseServiceError(f"{name} must use the SYNTHETIC- prefix")
        return value

    @staticmethod
    def _synthetic_payload(intake: Mapping[str, Any]) -> Mapping[str, Any]:
        if not isinstance(intake, Mapping):
            raise HairColorCaseServiceError("synthetic intake must be a mapping")
        for key, value in intake.items():
            if not isinstance(key, str) or not key.strip() or not isinstance(value, str) or not value.startswith("SYNTHETIC:"):
                raise HairColorCaseServiceError("all intake fields must contain synthetic placeholder values")
        return intake

    def create_case(self, *, case_ref: str, event_id: str, intake: Mapping[str, Any], actor_id: str | None = None):
        self._synthetic_id(case_ref, "case_ref")
        self._synthetic_id(event_id, "event_id")
        self._synthetic_payload(intake)
        return self.store.create_case(case_ref=case_ref, event_id=event_id, intake=intake, actor_id=actor_id)

    def get_case(self, case_ref: str):
        self._synthetic_id(case_ref, "case_ref")
        snapshot = self.store.get_case(case_ref)
        self._synthetic_payload(snapshot.intake)
        return snapshot

    def update_intake(self, *, case_ref: str, event_id: str, expected_case_version: int, fields: Mapping[str, Any], actor_id: str | None = None):
        self._synthetic_id(case_ref, "case_ref")
        self._synthetic_id(event_id, "event_id")
        self._synthetic_payload(fields)
        return self.store.update_intake(
            case_ref=case_ref, event_id=event_id,
            expected_case_version=expected_case_version, fields=fields, actor_id=actor_id,
        )

    def change_target(
        self, *, case_ref: str, event_id: str, expected_case_version: int,
        target_description: str,
        actor_id: str | None = None,
    ):
        self._synthetic_id(case_ref, "case_ref")
        self._synthetic_id(event_id, "event_id")
        if not isinstance(target_description, str) or not target_description.startswith("SYNTHETIC:"):
            raise HairColorCaseServiceError("target_description must be synthetic placeholder text")
        return self.store.change_target(
            case_ref=case_ref, event_id=event_id, expected_case_version=expected_case_version,
            target_description=target_description, actor_id=actor_id,
        )

    def stop_case(self, *, case_ref: str, event_id: str, expected_case_version: int, performed_step_refs: tuple[str, ...] = ()):
        self._synthetic_id(case_ref, "case_ref")
        self._synthetic_id(event_id, "event_id")
        if not isinstance(performed_step_refs, tuple) or any(not isinstance(ref, str) or not ref.startswith("SYNTHETIC-") for ref in performed_step_refs):
            raise HairColorCaseServiceError("performed_step_refs must use SYNTHETIC- identifiers")
        return self.store.stop_case(
            case_ref=case_ref, event_id=event_id, expected_case_version=expected_case_version,
            performed_step_refs=performed_step_refs, actor_id=actor_id,
        )

    def close_case(self, *, case_ref: str, event_id: str, expected_case_version: int, closure_reason: str, actor_id: str | None = None):
        self._synthetic_id(case_ref, "case_ref")
        self._synthetic_id(event_id, "event_id")
        if not isinstance(closure_reason, str) or not closure_reason.startswith("SYNTHETIC:"):
            raise HairColorCaseServiceError("closure_reason must be synthetic placeholder text")
        return self.store.close_case(
            case_ref=case_ref, event_id=event_id, expected_case_version=expected_case_version,
            closure_reason=closure_reason, actor_id=actor_id,
        )

    def fresh_restart(self, *, source_case_ref: str, new_case_ref: str, event_id: str, intake: Mapping[str, Any], actor_id: str | None = None):
        self._synthetic_id(source_case_ref, "source_case_ref")
        self._synthetic_id(new_case_ref, "new_case_ref")
        self._synthetic_id(event_id, "event_id")
        self._synthetic_payload(intake)
        return self.store.fresh_restart(
            source_case_ref=source_case_ref, new_case_ref=new_case_ref, event_id=event_id, intake=intake, actor_id=actor_id,
        )

    def consult_persian(self, *, case_ref: str, request_id: str, triage_event_id: str, actor_id: str | None = None):
        self._synthetic_id(case_ref, "case_ref")
        self._synthetic_id(request_id, "request_id")
        self._synthetic_id(triage_event_id, "triage_event_id")
        snapshot = self.store.get_case(case_ref)
        self._synthetic_payload(snapshot.intake)
        if snapshot.state != "ACTIVE":
            raise StoppedCase("stopped or closed case cannot be consulted")
        result = run_consultation_from_intake_persian(
            snapshot.intake,
            request_id=request_id,
            case_ref=case_ref,
            case_version=snapshot.case_version,
            target_version=snapshot.target_version,
        )
        raw = result["consultation"]
        self.store.record_triage(
            case_ref=case_ref,
            event_id=triage_event_id,
            expected_case_version=snapshot.case_version,
            expected_target_version=snapshot.target_version,
            request_id=request_id,
            consultation_status=raw["consultation_status"],
            reason_codes=tuple(raw["reason_codes"]),
            safe_summary=raw["summary"], actor_id=actor_id,
        )
        return result
