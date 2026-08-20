"""
conflict_analyzer.py — GATE 7-3

Implements:
- OD-04: 4-level conflict severity scale (CRITICAL / HIGH / MEDIUM / LOW)
- OD-05: Manual-only resolution for HIGH and CRITICAL levels
          (no automatic resolution allowed for these severities)

Framework 5 compliant.
Never silently discards conflicting values.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
from enum import Enum


class ConflictSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ResolutionState(str, Enum):
    UNRESOLVED = "UNRESOLVED"
    RESOLVED = "RESOLVED"
    NEEDS_REVIEW = "NEEDS_REVIEW"


# Fields that elevate severity (can be extended later by PO decision on OD-03)
CRITICAL_FIELDS = {
    "brand",
    "product_name",
    "canonical_name",
    "barcode",
    "gtin",
    "barcode_gtin",
    "market_region",
    "inventory_confirmation",
}

HIGH_FIELDS = {
    "variant",
    "size_value",
    "size_unit",
    "country_of_origin",
    "packaging_version",
}


class ConflictAnalyzer:
    """
    Analyzes conflicts scoped by product_id + field.
    Assigns 4-level severity (OD-04).
    Enforces manual-only resolution for HIGH/CRITICAL (OD-05).
    """

    def __init__(self):
        self._register: List[Dict[str, Any]] = []

    def determine_severity(self, field: str) -> ConflictSeverity:
        """OD-04: Map field to 4-level severity."""
        field_lower = (field or "").lower().strip()

        if field_lower in CRITICAL_FIELDS:
            return ConflictSeverity.CRITICAL
        if field_lower in HIGH_FIELDS:
            return ConflictSeverity.HIGH
        if field_lower in ("claim", "general", "notes"):
            return ConflictSeverity.MEDIUM
        return ConflictSeverity.LOW

    def analyze(
        self,
        product_id: str,
        field: str,
        conflicting_values: List[str],
        evidence_refs: Optional[List[Dict]] = None,
        sources: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Build a ConflictResult structure.
        Never drops any conflicting value.
        """
        severity = self.determine_severity(field)

        result = {
            "product_id": product_id,
            "field": field,
            "conflicting_values": list(conflicting_values),  # never silently dropped
            "evidence_refs": evidence_refs or [],
            "sources": sources or [],
            "resolution_state": ResolutionState.UNRESOLVED.value,
            "resolution_rationale": None,
            "severity": severity.value,
            "detected_at": datetime.now(timezone.utc).isoformat(),
            "auto_resolution_allowed": severity in (ConflictSeverity.MEDIUM, ConflictSeverity.LOW),
        }

        self._register.append(result)
        return result

    def can_auto_resolve(self, severity: str) -> bool:
        """
        OD-05: Auto-resolution is FORBIDDEN for HIGH and CRITICAL.
        Only MEDIUM and LOW may be candidates for automatic handling.
        """
        return severity in (ConflictSeverity.MEDIUM.value, ConflictSeverity.LOW.value)

    def attempt_resolution(
        self,
        conflict: Dict[str, Any],
        resolution_rationale: str,
        force_manual: bool = True,
    ) -> Dict[str, Any]:
        """
        Apply a resolution.

        For HIGH / CRITICAL: only explicit manual resolution is accepted.
        Auto-resolution is blocked (OD-05).
        """
        severity = conflict.get("severity")

        if not self.can_auto_resolve(severity) and not force_manual:
            raise ValueError(
                f"Auto-resolution is forbidden for severity={severity}. "
                "Only explicit manual resolution is allowed (OD-05)."
            )

        if not resolution_rationale or not resolution_rationale.strip():
            raise ValueError("resolution_rationale is mandatory for any resolution.")

        conflict["resolution_state"] = ResolutionState.RESOLVED.value
        conflict["resolution_rationale"] = resolution_rationale.strip()
        conflict["resolved_at"] = datetime.now(timezone.utc).isoformat()
        return conflict

    def get_register(self) -> List[Dict[str, Any]]:
        return list(self._register)

    def get_unresolved(self, product_id: Optional[str] = None) -> List[Dict[str, Any]]:
        items = [
            c for c in self._register
            if c["resolution_state"] == ResolutionState.UNRESOLVED.value
        ]
        if product_id:
            items = [c for c in items if c["product_id"] == product_id]
        return items

