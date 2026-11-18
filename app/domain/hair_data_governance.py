"""PO-66-09 data governance policy for the first HBI Hair implementation.

This policy deliberately permits synthetic fixtures only. It does not claim
that a legal jurisdiction has been selected or that real-client processing is
authorized. Production personal-data processing remains disabled.
"""
from __future__ import annotations

from dataclasses import dataclass
import re


_SYNTHETIC_IDENTIFIER_RE = re.compile(r"^SYNTHETIC-[A-Za-z0-9][A-Za-z0-9._:-]{0,115}$")
_CASE_VERSION_RE = re.compile(r"^case-v[1-9][0-9]{0,5}$")
_GOAL_VERSION_RE = re.compile(r"^goal-v[1-9][0-9]{0,5}$")
_FIELD_NAME_RE = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
_NUMERIC_VERSION_RE = re.compile(r"^[1-9][0-9]{0,5}(?:\.[0-9]{1,5})?$")


@dataclass(frozen=True)
class HairDataGovernancePolicy:
    policy_id: str = "PO-66-09"
    data_class: str = "SYNTHETIC_ONLY"
    real_client_data_enabled: bool = False
    persistence_enabled: bool = False
    real_client_retention_seconds: int = 0
    exceptions: tuple[str, ...] = ()
    jurisdiction_status: str = "UNAPPROVED_PRODUCTION_BLOCKED"
    jurisdiction_note: str = (
        "No production jurisdiction is approved. Real-client processing is "
        "blocked until the controller, deployment location, data subjects, "
        "and applicable legal review are documented and approved."
    )


HAIR_DATA_GOVERNANCE_POLICY = HairDataGovernancePolicy()

# Existing server-side roles are mapped to narrowly defined capabilities.
# Reviewer/QA is an internal technical-review role, not proof of professional
# hair-color credentials. Admin privileges do not grant domain approval.
HAIR_ROLE_CAPABILITIES = {
    "Editor": frozenset(),
    "Reviewer/QA": frozenset({"READ_SYNTHETIC_SPECIALIST_VIEW"}),
    "PO": frozenset({"READ_SYNTHETIC_SPECIALIST_VIEW", "APPROVE_PRODUCT_SCOPE"}),
    "Admin": frozenset({"READ_SYNTHETIC_SPECIALIST_VIEW", "PLATFORM_ADMIN"}),
}


def is_permitted_synthetic_identifier(value: object) -> bool:
    """Accept only bounded opaque identifiers reserved for synthetic fixtures."""
    return isinstance(value, str) and _SYNTHETIC_IDENTIFIER_RE.fullmatch(value) is not None


def is_permitted_synthetic_version(value: object, *, kind: str) -> bool:
    """Accept only bounded, typed version tokens; arbitrary caller text is rejected."""
    pattern = {"case": _CASE_VERSION_RE, "goal": _GOAL_VERSION_RE}.get(kind)
    return isinstance(value, str) and pattern is not None and pattern.fullmatch(value) is not None


def is_permitted_field_name(value: object) -> bool:
    """Accept bounded schema-style field names, never arbitrary caller text."""
    return isinstance(value, str) and _FIELD_NAME_RE.fullmatch(value) is not None


def is_permitted_numeric_version(value: object) -> bool:
    """Accept the consultation engine's bounded numeric version tokens."""
    return isinstance(value, str) and _NUMERIC_VERSION_RE.fullmatch(value) is not None


def is_permitted_synthetic_case(*, case_id: object, synthetic_data: object) -> bool:
    return (
        HAIR_DATA_GOVERNANCE_POLICY.data_class == "SYNTHETIC_ONLY"
        and HAIR_DATA_GOVERNANCE_POLICY.real_client_data_enabled is False
        and HAIR_DATA_GOVERNANCE_POLICY.persistence_enabled is False
        and synthetic_data is True
        and is_permitted_synthetic_identifier(case_id)
    )


__all__ = [
    "HairDataGovernancePolicy",
    "HAIR_DATA_GOVERNANCE_POLICY",
    "HAIR_ROLE_CAPABILITIES",
    "is_permitted_synthetic_case",
    "is_permitted_synthetic_identifier",
    "is_permitted_synthetic_version",
    "is_permitted_field_name",
    "is_permitted_numeric_version",
]
