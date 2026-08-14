"""
scoring.py - MatchScoringEngine
Architecture Freeze v0.1 (AD-1, AD-2)
"""
from typing import Dict, List, Optional
from .scoring_constants import (
    SCORE_WEIGHT_NEED, SCORE_WEIGHT_EVIDENCE, SCORE_WEIGHT_INVENTORY,
    CONFIDENCE_WEIGHT_NEED, CONFIDENCE_WEIGHT_EVIDENCE,
    THRESHOLD_ELIGIBLE, THRESHOLD_NEEDS_REVIEW,
    ELIGIBILITY_ELIGIBLE, ELIGIBILITY_NEEDS_REVIEW, ELIGIBILITY_INELIGIBLE,
    WARNING_HARD_GATE_ACTIVE, WARNING_EVIDENCE_MISSING,
    WARNING_INVENTORY_UNAVAILABLE,
)


class MatchScoringEngine:
    """Scoring Engine per Architecture Freeze v0.1."""

    def calculate(self, need_match, evidence_score, inventory_score,
                  evidence_refs=None, warnings=None):
        all_warnings = list(warnings or [])
        hard_gate = False
        hg_reasons = []

        if evidence_score <= 0.0:
            hard_gate = True
            hg_reasons.append(WARNING_EVIDENCE_MISSING)
        if inventory_score <= 0.0:
            hard_gate = True
            hg_reasons.append(WARNING_INVENTORY_UNAVAILABLE)

        final = (SCORE_WEIGHT_NEED * need_match
                 + SCORE_WEIGHT_EVIDENCE * evidence_score
                 + SCORE_WEIGHT_INVENTORY * inventory_score)
        final = round(min(1.0, max(0.0, final)), 2)

        conf = (CONFIDENCE_WEIGHT_NEED * need_match
                + CONFIDENCE_WEIGHT_EVIDENCE * evidence_score)
        conf = round(min(1.0, max(0.0, conf)), 2)

        if hard_gate:
            elig = ELIGIBILITY_NEEDS_REVIEW
            all_warnings.append(WARNING_HARD_GATE_ACTIVE)
        elif final >= THRESHOLD_ELIGIBLE:
            elig = ELIGIBILITY_ELIGIBLE
        elif final >= THRESHOLD_NEEDS_REVIEW:
            elig = ELIGIBILITY_NEEDS_REVIEW
        else:
            elig = ELIGIBILITY_INELIGIBLE

        parts = [
            "Need: " + format(need_match, ".2f"),
            "Evidence: " + format(evidence_score, ".2f"),
            "Inventory: " + format(inventory_score, ".2f"),
            "Final: " + format(final, ".2f"),
            "Confidence: " + format(conf, ".2f"),
        ]
        if hard_gate:
            parts.append("Hard Gate: " + ", ".join(hg_reasons))

        return {
            "final_score": final, "confidence": conf,
            "eligibility": elig, "hard_gate_triggered": hard_gate,
            "hard_gate_reasons": hg_reasons,
            "reasoning": " | ".join(parts),
            "evidence_refs": evidence_refs or [],
            "warnings": all_warnings,
        }
