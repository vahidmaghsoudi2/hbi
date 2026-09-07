"""
scoring.py - MatchScoringEngine
Architecture Freeze v0.1 (AD-1, AD-2)

Also owns *input* score derivation used by ReasoningEngine.run:
need_match, evidence_score, inventory_score — so RecommendationService
stays data-assembly only (PR #36 ownership fix).
"""
from typing import Dict, List, Optional, Any
from .scoring_constants import (
    SCORE_WEIGHT_NEED, SCORE_WEIGHT_EVIDENCE, SCORE_WEIGHT_INVENTORY,
    CONFIDENCE_WEIGHT_NEED, CONFIDENCE_WEIGHT_EVIDENCE,
    THRESHOLD_ELIGIBLE, THRESHOLD_NEEDS_REVIEW,
    ELIGIBILITY_ELIGIBLE, ELIGIBILITY_NEEDS_REVIEW, ELIGIBILITY_INELIGIBLE,
    WARNING_HARD_GATE_ACTIVE, WARNING_EVIDENCE_MISSING,
    WARNING_INVENTORY_UNAVAILABLE,
    EVIDENCE_WEIGHT_INDEPENDENT,
    EVIDENCE_WEIGHT_MANUFACTURER,
    EVIDENCE_WEIGHT_RETAILER,
    EVIDENCE_WEIGHT_SECONDARY,
    EVIDENCE_WEIGHT_NONE,
    INVENTORY_SCORE_AVAILABLE,
    INVENTORY_SCORE_UNAVAILABLE,
)

# Map source_type strings → weights (Framework 1.B / scoring_constants).
_SOURCE_TYPE_WEIGHTS = {
    "PEER_REVIEWED": EVIDENCE_WEIGHT_INDEPENDENT,
    "CLINICAL_TRIAL": EVIDENCE_WEIGHT_INDEPENDENT,
    "REGULATORY": EVIDENCE_WEIGHT_INDEPENDENT,
    "OFFICIAL_MANUFACTURER": EVIDENCE_WEIGHT_MANUFACTURER,
    "MANUFACTURER": EVIDENCE_WEIGHT_MANUFACTURER,
    "REPUTABLE_RETAILER": EVIDENCE_WEIGHT_RETAILER,
    "SECONDARY": EVIDENCE_WEIGHT_SECONDARY,
}


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

    # ── Input scores for ReasoningEngine.run (owned here, not Service) ──

    def score_need_match(
        self,
        concern_list: List[str],
        *,
        product_name: str = "",
        brand: str = "",
        known_use_cases: str = "",
        claimed_benefits: str = "",
        ingredients: str = "",
    ) -> float:
        """Derive need_match input from concern tokens vs product/knowledge text."""
        if not concern_list:
            return 0.5
        corpus = " ".join(
            [
                product_name or "",
                brand or "",
                known_use_cases or "",
                claimed_benefits or "",
                ingredients or "",
            ]
        ).lower()
        if not corpus.strip():
            return 0.3
        hits = sum(1 for c in concern_list if c and c in corpus)
        return round(min(1.0, hits / max(len(concern_list), 1)), 2)

    def score_evidence_from_source_types(self, source_types: List[str]) -> float:
        """Average source-type weights (scoring_constants / Framework 1.B)."""
        if not source_types:
            return EVIDENCE_WEIGHT_NONE
        total = 0.0
        for st in source_types:
            key = (st or "").upper()
            total += _SOURCE_TYPE_WEIGHTS.get(key, 0.1)
        return round(min(1.0, total / len(source_types)), 2)

    def score_inventory(
        self,
        quantity_available: Optional[int] = None,
        stock_status: Optional[str] = None,
    ) -> float:
        """Map inventory row fields to inventory_score input."""
        qty = quantity_available or 0
        status = (stock_status or "").upper()
        if qty <= 0 or status == "OUT_OF_STOCK":
            return INVENTORY_SCORE_UNAVAILABLE
        return INVENTORY_SCORE_AVAILABLE
