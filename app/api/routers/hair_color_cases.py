"""Synthetic-only persistent Hair Color case API.

This API exposes the existing case service, not specialist advice. Database path
must be explicitly configured with HBI_HAIR_COLOR_CASE_DB; no default production
storage is created. Only synthetic identifiers and placeholder intake values are
accepted. Explicit synthetic client ACCEPT/REJECT decisions are persisted as audit events; acceptance never grants execution authority.
"""
from __future__ import annotations

import os
import sqlite3
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.core.authorization import require_any_role
from app.hair_color.case_service import HairColorCaseService, HairColorCaseServiceError
from app.hair_color.case_store import (
    CaseNotFound, CaseStoreError, HairColorCaseStore, StaleCaseVersion, StoppedCase,
)
from app.models.user_role import ROLE_ADMIN, ROLE_PO, ROLE_REVIEWER_QA

router = APIRouter()


def get_hair_color_case_service() -> HairColorCaseService:
    database_path = os.getenv("HBI_HAIR_COLOR_CASE_DB", "").strip()
    if not database_path:
        raise HTTPException(status_code=503, detail="Synthetic Hair Color case storage is not configured.")
    try:
        return HairColorCaseService(HairColorCaseStore(database_path))
    except (OSError, sqlite3.Error, CaseStoreError) as exc:
        # Do not leak storage paths or database diagnostics through the API.
        raise HTTPException(status_code=503, detail="Synthetic Hair Color case storage is unavailable.") from exc


class CreateCaseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    case_ref: str
    event_id: str
    intake: dict[str, str] = Field(default_factory=dict)


class UpdateIntakeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event_id: str
    expected_case_version: int = Field(ge=1)
    fields: dict[str, str]


class TriageRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request_id: str
    triage_event_id: str


class TargetChangeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event_id: str
    expected_case_version: int = Field(ge=1)
    target_description: str


class ClientDecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event_id: str
    expected_case_version: int = Field(ge=1)
    expected_target_version: int = Field(ge=1)
    decision: str
    suggestion_ref: str
    reason: str | None = None


class StopCaseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event_id: str
    expected_case_version: int = Field(ge=1)
    performed_step_refs: tuple[str, ...] = ()


class FreshRestartRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    new_case_ref: str
    event_id: str
    intake: dict[str, str] = Field(default_factory=dict)


def _snapshot(snapshot) -> dict[str, Any]:
    return {
        "case_ref": snapshot.case_ref,
        "case_version": snapshot.case_version,
        "target_version": snapshot.target_version,
        "state": snapshot.state,
        "intake": snapshot.intake,
        "created_event_id": snapshot.created_event_id,
        "updated_event_id": snapshot.updated_event_id,
    }


def _translate_error(exc: Exception) -> HTTPException:
    if isinstance(exc, CaseNotFound):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, (StaleCaseVersion, StoppedCase)):
        return HTTPException(status_code=409, detail=str(exc))
    if isinstance(exc, (CaseStoreError, HairColorCaseServiceError)):
        return HTTPException(status_code=422, detail=str(exc))
    return HTTPException(status_code=500, detail="Synthetic Hair Color case operation failed.")


@router.post("/cases", status_code=201)
def create_hair_color_case(
    payload: CreateCaseRequest,
    service: HairColorCaseService = Depends(get_hair_color_case_service),
    _auth=Depends(require_any_role(ROLE_REVIEWER_QA, ROLE_PO, ROLE_ADMIN)),
):
    try:
        return _snapshot(service.create_case(case_ref=payload.case_ref, event_id=payload.event_id, intake=payload.intake, actor_id=_auth[0]))
    except Exception as exc:
        raise _translate_error(exc) from exc


@router.get("/cases/{case_ref}")
def read_hair_color_case(
    case_ref: str,
    service: HairColorCaseService = Depends(get_hair_color_case_service),
    _auth=Depends(require_any_role(ROLE_REVIEWER_QA, ROLE_PO, ROLE_ADMIN)),
):
    try:
        return _snapshot(service.get_case(case_ref))
    except Exception as exc:
        raise _translate_error(exc) from exc


@router.patch("/cases/{case_ref}/intake")
def update_hair_color_intake(
    case_ref: str,
    payload: UpdateIntakeRequest,
    service: HairColorCaseService = Depends(get_hair_color_case_service),
    _auth=Depends(require_any_role(ROLE_REVIEWER_QA, ROLE_PO, ROLE_ADMIN)),
):
    try:
        return _snapshot(service.update_intake(
            case_ref=case_ref, event_id=payload.event_id,
            expected_case_version=payload.expected_case_version, fields=payload.fields, actor_id=_auth[0],
        ))
    except Exception as exc:
        raise _translate_error(exc) from exc



@router.post("/cases/{case_ref}/target-change")
def change_hair_color_target(
    case_ref: str,
    payload: TargetChangeRequest,
    service: HairColorCaseService = Depends(get_hair_color_case_service),
    _auth=Depends(require_any_role(ROLE_REVIEWER_QA, ROLE_PO, ROLE_ADMIN)),
):
    try:
        service._synthetic_id(case_ref, "case_ref")
        service._synthetic_id(payload.event_id, "event_id")
        return _snapshot(service.change_target(
            case_ref=case_ref, event_id=payload.event_id,
            expected_case_version=payload.expected_case_version,
            target_description=payload.target_description, actor_id=_auth[0],
        ))
    except Exception as exc:
        raise _translate_error(exc) from exc


@router.post("/cases/{case_ref}/triage")
def run_synthetic_hair_color_triage(
    case_ref: str,
    payload: TriageRequest,
    service: HairColorCaseService = Depends(get_hair_color_case_service),
    _auth=Depends(require_any_role(ROLE_REVIEWER_QA, ROLE_PO, ROLE_ADMIN)),
):
    try:
        result = service.consult_persian(
            case_ref=case_ref, request_id=payload.request_id, triage_event_id=payload.triage_event_id, actor_id=_auth[0],
        )
        consultation = result.get("consultation", {})
        if consultation.get("options") or result.get("execution_authorized") is not False:
            raise CaseStoreError("synthetic triage output violated non-publishing contract")
        return result
    except Exception as exc:
        raise _translate_error(exc) from exc



@router.post("/cases/{case_ref}/decision")
def record_hair_color_client_decision(
    case_ref: str,
    payload: ClientDecisionRequest,
    service: HairColorCaseService = Depends(get_hair_color_case_service),
    _auth=Depends(require_any_role(ROLE_REVIEWER_QA, ROLE_PO, ROLE_ADMIN)),
):
    try:
        for value, name in ((case_ref, "case_ref"), (payload.event_id, "event_id"),
                            (payload.suggestion_ref, "suggestion_ref")):
            service._synthetic_id(value, name)
        if payload.reason is not None and not payload.reason.startswith("SYNTHETIC:"):
            raise HairColorCaseServiceError("reason must be synthetic placeholder text")
        snapshot = service.store.record_client_decision(
            case_ref=case_ref, event_id=payload.event_id,
            expected_case_version=payload.expected_case_version,
            expected_target_version=payload.expected_target_version,
            decision=payload.decision, suggestion_ref=payload.suggestion_ref,
            reason=payload.reason, actor_id=_auth[0],
        )
        return {**_snapshot(snapshot), "execution_authorized": False}
    except Exception as exc:
        raise _translate_error(exc) from exc


@router.post("/cases/{case_ref}/stop")
def stop_hair_color_case(
    case_ref: str,
    payload: StopCaseRequest,
    service: HairColorCaseService = Depends(get_hair_color_case_service),
    _auth=Depends(require_any_role(ROLE_REVIEWER_QA, ROLE_PO, ROLE_ADMIN)),
):
    try:
        return _snapshot(service.stop_case(
            case_ref=case_ref, event_id=payload.event_id,
            expected_case_version=payload.expected_case_version,
            performed_step_refs=payload.performed_step_refs, actor_id=_auth[0],
        ))
    except Exception as exc:
        raise _translate_error(exc) from exc


@router.post("/cases/{case_ref}/restart", status_code=201)
def fresh_restart_hair_color_case(
    case_ref: str,
    payload: FreshRestartRequest,
    service: HairColorCaseService = Depends(get_hair_color_case_service),
    _auth=Depends(require_any_role(ROLE_REVIEWER_QA, ROLE_PO, ROLE_ADMIN)),
):
    try:
        return _snapshot(service.fresh_restart(
            source_case_ref=case_ref, new_case_ref=payload.new_case_ref,
            event_id=payload.event_id, intake=payload.intake,
        ))
    except Exception as exc:
        raise _translate_error(exc) from exc


@router.get("/cases/{case_ref}/history")
def read_hair_color_case_history(
    case_ref: str,
    service: HairColorCaseService = Depends(get_hair_color_case_service),
    _auth=Depends(require_any_role(ROLE_REVIEWER_QA, ROLE_PO, ROLE_ADMIN)),
):
    try:
        service.get_case(case_ref)
        return service.store.list_events(case_ref)
    except Exception as exc:
        raise _translate_error(exc) from exc
