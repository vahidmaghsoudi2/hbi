"""
claim_validator.py — GATE 7-3

Framework 4 Claim Boundary Rules enforcement.
Prevents illegal promotions of claim types.
"""

from typing import List, Dict, Any, Optional


class ClaimValidator:
    """
    Enforces Framework 4 promotion rules.

    Forbidden promotions:
    - UNKNOWN → anything
    - INFERENCE → FACT (automatic)
    - MANUFACTURER_CLAIM → FACT without independent evidence
    - EVIDENCE_SUPPORTED → FACT only with multiple STRONG sources
    """

    FORBIDDEN_PROMOTIONS = {
        ("UNKNOWN", "FACT"),
        ("UNKNOWN", "EVIDENCE_SUPPORTED"),
        ("UNKNOWN", "MANUFACTURER_CLAIM"),
        ("UNKNOWN", "INFERENCE"),
        ("INFERENCE", "FACT"),
        ("MANUFACTURER_CLAIM", "FACT"),
    }

    def validate_promotion(
        self,
        from_type: str,
        to_type: str,
        evidence_strengths: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Returns a validation result.
        Does not raise by default — collects violations for ReasoningResult.
        """
        from_type = (from_type or "UNKNOWN").upper()
        to_type = (to_type or "UNKNOWN").upper()

        violation = {
            "from_type": from_type,
            "to_type": to_type,
            "allowed": True,
            "reason": None,
        }

        if (from_type, to_type) in self.FORBIDDEN_PROMOTIONS:
            violation["allowed"] = False
            violation["reason"] = (
                f"Framework 4 forbids promotion from {from_type} to {to_type}."
            )
            return violation

        if from_type == "EVIDENCE_SUPPORTED" and to_type == "FACT":
            strengths = evidence_strengths or []
            strong_count = sum(1 for s in strengths if (s or "").upper() == "STRONG")
            if strong_count < 2:
                violation["allowed"] = False
                violation["reason"] = (
                    "EVIDENCE_SUPPORTED may become FACT only with multiple STRONG sources "
                    "(Framework 4)."
                )
                return violation

        return violation

    def check_list(
        self,
        claims: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Batch validation. Returns list of violations only.
        """
        violations = []
        for claim in claims:
            result = self.validate_promotion(
                claim.get("claim_type", "UNKNOWN"),
                claim.get("target_type", claim.get("claim_type", "UNKNOWN")),
                claim.get("evidence_strengths"),
            )
            if not result["allowed"]:
                violations.append({**result, "claim": claim})
        return violations
