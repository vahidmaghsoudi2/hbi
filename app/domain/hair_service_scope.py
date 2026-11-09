"""Fail-closed service-scope guard for the first HBI Hair release.

This module is intentionally pure: it has no database, API, Skin service,
legacy recommendation, or customer-data dependency. It authorizes only the
CATALOG_READY catalog-identity lookup path defined by PO-66-10.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


HairScopeStop = Literal["DATA_GAP", "OUT_OF_DOMAIN", "UNRESOLVED", "ENGINE_FAIL"]


@dataclass(frozen=True)
class HairServiceScopeDecision:
    """Result of evaluating the requested Hair service kind."""

    allowed: bool
    service_kind: str | None
    stop_class: HairScopeStop | None
    reason_code: str


def evaluate_hair_service_scope(service_kind: object) -> HairServiceScopeDecision:
    """Allow only the exact in-scope CATALOG_READY service kind.

    Missing values are DATA_GAP. The known but excluded COMBINATION_CONSULT
    service is OUT_OF_DOMAIN. Unknown values and invalid input types remain
    UNRESOLVED. No aliases, defaults, or fallback service are inferred.
    """
    if service_kind is None:
        return HairServiceScopeDecision(
            allowed=False,
            service_kind=None,
            stop_class="DATA_GAP",
            reason_code="SERVICE_KIND_MISSING",
        )

    if not isinstance(service_kind, str):
        return HairServiceScopeDecision(
            allowed=False,
            service_kind=None,
            stop_class="UNRESOLVED",
            reason_code="SERVICE_KIND_INVALID_TYPE",
        )

    try:
        normalized = service_kind.strip().upper()
    except Exception:
        return HairServiceScopeDecision(
            allowed=False,
            service_kind=None,
            stop_class="ENGINE_FAIL",
            reason_code="SERVICE_KIND_NORMALIZATION_FAILED",
        )

    if not normalized:
        return HairServiceScopeDecision(
            allowed=False,
            service_kind=None,
            stop_class="DATA_GAP",
            reason_code="SERVICE_KIND_BLANK",
        )

    if normalized == "CATALOG_READY":
        return HairServiceScopeDecision(
            allowed=True,
            service_kind="CATALOG_READY",
            stop_class=None,
            reason_code="SERVICE_KIND_IN_SCOPE",
        )

    if normalized == "COMBINATION_CONSULT":
        return HairServiceScopeDecision(
            allowed=False,
            service_kind="COMBINATION_CONSULT",
            stop_class="OUT_OF_DOMAIN",
            reason_code="SERVICE_KIND_OUT_OF_FIRST_RELEASE_SCOPE",
        )

    return HairServiceScopeDecision(
        allowed=False,
        service_kind=normalized,
        stop_class="UNRESOLVED",
        reason_code="SERVICE_KIND_UNKNOWN",
    )


__all__ = [
    "HairScopeStop",
    "HairServiceScopeDecision",
    "evaluate_hair_service_scope",
]
