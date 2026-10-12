"""WP-INTAKE-CLAIM-INTEGRITY-001 — frozen claim taxonomy (contract v1.1)."""
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
            raise ValueError(
                "claim_type cannot be blank; allowed: "
                + ", ".join(sorted(ALLOWED_CLAIM_TYPES))
            )
        return missing_default
    normalized = text.upper()
    if normalized not in ALLOWED_CLAIM_TYPES:
        raise ValueError(
            f"Unsupported claim_type {value!r}; allowed: "
            + ", ".join(sorted(ALLOWED_CLAIM_TYPES))
        )
    return normalized
