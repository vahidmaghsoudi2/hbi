"""Canonical claim taxonomy for the Skin Product Intake evidence contract.

Claim types describe the epistemic status of an evidence row, not recommendation
scores or promotion labels. Keep this module as the single vocabulary source.
"""
from __future__ import annotations

ALLOWED_CLAIM_TYPES = frozenset({
    "FACT",
    "MANUFACTURER_CLAIM",
    "EVIDENCE",
    "INFERENCE",
    "UNKNOWN",
    "CONFLICT",
})


def normalize_claim_type_value(value, *, missing_default: str | None = "UNKNOWN"):
    if value is None:
        return missing_default
    text = str(value).strip()
    if not text:
        if missing_default is None:
            raise ValueError("claim_type cannot be blank; allowed: " + ", ".join(sorted(ALLOWED_CLAIM_TYPES)))
        return missing_default
    normalized = text.upper()
    if normalized not in ALLOWED_CLAIM_TYPES:
        raise ValueError(f"Unsupported claim_type {value!r}; allowed: " + ", ".join(sorted(ALLOWED_CLAIM_TYPES)))
    return normalized


# Compatibility alias retained for PR #360 callers.
CLAIM_TYPES = ALLOWED_CLAIM_TYPES

__all__ = ["ALLOWED_CLAIM_TYPES", "CLAIM_TYPES", "normalize_claim_type_value"]
