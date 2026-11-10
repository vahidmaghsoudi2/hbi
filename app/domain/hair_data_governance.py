"""PO-66-09 data governance policy for the first HBI Hair implementation.

This policy deliberately permits synthetic fixtures only. It does not claim
that a legal jurisdiction has been selected or that real-client processing is
authorized. Production personal-data processing remains disabled.
"""
from __future__ import annotations

from dataclasses import dataclass


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


def is_permitted_synthetic_case(*, case_id: object, synthetic_data: object) -> bool:
    return (
        HAIR_DATA_GOVERNANCE_POLICY.data_class == "SYNTHETIC_ONLY"
        and HAIR_DATA_GOVERNANCE_POLICY.real_client_data_enabled is False
        and HAIR_DATA_GOVERNANCE_POLICY.persistence_enabled is False
        and synthetic_data is True
        and isinstance(case_id, str)
        and case_id.startswith("SYNTHETIC-")
    )


__all__ = [
    "HairDataGovernancePolicy",
    "HAIR_DATA_GOVERNANCE_POLICY",
    "HAIR_ROLE_CAPABILITIES",
    "is_permitted_synthetic_case",
]
