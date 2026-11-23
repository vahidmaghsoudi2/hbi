"""Public intake normalization for the safe Hair Color triage boundary.

Only collects high-level consultation context. It does not infer hair chemistry,
diagnose conditions, or produce color formulas or application instructions.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

INTAKE_FIELDS = {
    "current_hair_state": "شرح وضعیت فعلی مو",
    "desired_result": "هدف و نتیجه موردنظر",
    "service_history": "سابقه خدمات قبلی مو",
    "product_context": "محصولات مرتبط و مشخصات روی بسته‌بندی",
    "reference_context": "توضیح عکس یا نمونه مرجع (در صورت وجود)",
}
_REQUIRED_FIELDS = tuple(field for field in INTAKE_FIELDS if field != "reference_context")


class HairColorIntakeError(ValueError):
    """Raised when intake input is malformed."""


def build_intake_request(
    intake: Mapping[str, Any],
    *,
    request_id: str,
    case_ref: str,
    case_version: int = 1,
    target_version: int = 1,
    safety_concern: bool = False,
    conflicting_fields: tuple[str, ...] = (),
) -> dict[str, Any]:
    """Build a contract request and explicitly identify missing required fields."""
    if not isinstance(intake, Mapping):
        raise HairColorIntakeError("intake must be an object")
    for name, value in (("request_id", request_id), ("case_ref", case_ref)):
        if not isinstance(value, str) or not value.strip():
            raise HairColorIntakeError(f"{name} must be a non-empty string")
    for name, version in (("case_version", case_version), ("target_version", target_version)):
        if isinstance(version, bool) or not isinstance(version, int) or version < 1:
            raise HairColorIntakeError(f"{name} must be a positive integer")
    if not isinstance(safety_concern, bool):
        raise HairColorIntakeError("safety_concern must be boolean")
    if not isinstance(conflicting_fields, tuple) or any(
        not isinstance(field, str) or not field.strip() for field in conflicting_fields
    ):
        raise HairColorIntakeError("conflicting_fields must be a tuple of non-empty strings")

    normalized: dict[str, str] = {}
    missing: list[str] = []
    for field in _REQUIRED_FIELDS:
        value = intake.get(field)
        if not isinstance(value, str) or not value.strip():
            missing.append(field)
        else:
            normalized[field] = value.strip()

    optional_reference = intake.get("reference_context")
    if isinstance(optional_reference, str) and optional_reference.strip():
        normalized["reference_context"] = optional_reference.strip()

    return {
        "contract_version": "0.3-draft",
        "request_id": request_id,
        "operation": "EVALUATE_CASE",
        "case_ref": case_ref,
        "case_version": case_version,
        "target_version": target_version,
        "case_context": {
            "intake": normalized,
            "missing_fields": missing,
            "conflicting_fields": list(conflicting_fields),
            "intake_complete": not missing and not conflicting_fields,
        },
        "evidence_context": [],
        "policy_context": {"safety_concern": safety_concern},
    }


def get_intake_field_labels() -> dict[str, str]:
    """Return a copy of the stable Persian labels used by intake UI."""
    return dict(INTAKE_FIELDS)
