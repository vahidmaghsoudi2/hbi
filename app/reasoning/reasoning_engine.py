"""
reasoning_engine.py — GATE 7-3

Orchestrator of the Reasoning Engine.

Key guarantees (OD-08):
- ReasoningResult is ALWAYS Computed Only.
- Nothing is written to the database from this engine.
- No persistence of ReasoningResult.

Also integrates:
- OD-04 severity scale via ConflictAnalyzer
- OD-05 manual-only rule for HIGH/CRITICAL
- Framework 4 via ClaimValidator
- Framework 5 Unknown / Conflict protocol
- MatchScoringEngine for final_score / evidence_score (when inputs provided)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from .conflict_analyzer import ConflictAnalyzer, ConflictSeverity
from .claim_validator import ClaimValidator
from .scoring import MatchScoringEngine


ENGINE_VERSION = "0.2.0-GATE-7-3-SCORE"


class ReasoningEngine:
    """
    Produces a ReasoningResult that is purely computed.
    Never persists anything to DB (OD-08).
    """

    def __init__(self):
        self.conflict_analyzer = ConflictAnalyzer()
        self.claim_validator = ClaimValidator()
        self.scoring_engine = MatchScoringEngine()

    def run(
        self,
        product_id: str,
        product_knowledge_snapshot: Optional[Dict[str, Any]] = None,
        evidence_list: Optional[List[Dict[str, Any]]] = None,
        existing_conflicts: Optional[List[Dict[str, Any]]] = None,
        need_match: Optional[float] = None,
        evidence_score: Optional[float] = None,
        inventory_score: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Main entry point.

        Returns a complete ReasoningResult (computed only).
        When need_match / evidence_score / inventory_score are supplied,
        also computes final_score, confidence, eligibility via MatchScoringEngine.
        """
        evidence_list = evidence_list or []
        existing_conflicts = existing_conflicts or []
        product_knowledge_snapshot = product_knowledge_snapshot or {}

        # 1. Build evidence references (provenance)
        evidence_refs = []
        for ev in evidence_list:
            evidence_refs.append({
                "evidence_id": ev.get("evidence_id"),
                "claim_id": ev.get("claim_id"),
                "field": ev.get("field"),
                "claim_type": ev.get("claim_type"),
                "source": ev.get("source_reference") or ev.get("source"),
                "source_type": ev.get("source_type"),
                "evidence_strength": ev.get("evidence_strength"),
                "qa_status": ev.get("qa_status"),
            })

        # 2. Analyze / surface conflicts (OD-04 severity)
        conflicts: List[Dict[str, Any]] = []
        for conf in existing_conflicts:
            analyzed = self.conflict_analyzer.analyze(
                product_id=product_id,
                field=conf.get("field", "general"),
                conflicting_values=conf.get("values") or conf.get("conflicting_values") or [],
                evidence_refs=conf.get("evidence_refs"),
                sources=conf.get("sources"),
            )
            conflicts.append(analyzed)

        # 3. Claim boundary violations (Framework 4)
        claim_boundary_violations = self.claim_validator.check_list(evidence_list)

        # 4. Unknowns (Framework 5)
        unknowns: List[Dict[str, Any]] = []
        for ev in evidence_list:
            if (ev.get("claim_type") or "").upper() == "UNKNOWN":
                field = ev.get("field") or "general"
                severity = self.conflict_analyzer.determine_severity(field).value
                action = "ESCALATE_PO" if severity in ("CRITICAL", "HIGH") else "LOG"
                unknowns.append({
                    "product_id": product_id,
                    "field": field,
                    "severity": severity,
                    "action": action,
                    "notes": ev.get("claim") or ev.get("notes"),
                })

        # 5. Scoring (when inputs provided) — logic lives HERE, not in RecommendationService
        scoring_result: Optional[Dict[str, Any]] = None
        if need_match is not None and evidence_score is not None and inventory_score is not None:
            scoring_result = self.scoring_engine.calculate(
                need_match=need_match,
                evidence_score=evidence_score,
                inventory_score=inventory_score,
                evidence_refs=evidence_refs,
            )

        # 6. Build human-readable rationale
        rationale_parts = [
            f"ReasoningEngine v{ENGINE_VERSION}",
            f"Product: {product_id}",
            f"Evidence items considered: {len(evidence_refs)}",
            f"Conflicts detected: {len(conflicts)}",
            f"Unknowns surfaced: {len(unknowns)}",
            f"Claim-boundary violations: {len(claim_boundary_violations)}",
        ]

        if conflicts:
            high_or_critical = [
                c for c in conflicts
                if c.get("severity") in (ConflictSeverity.CRITICAL.value, ConflictSeverity.HIGH.value)
            ]
            if high_or_critical:
                rationale_parts.append(
                    f"WARNING: {len(high_or_critical)} HIGH/CRITICAL conflict(s) require manual resolution (OD-05)."
                )

        if scoring_result:
            rationale_parts.append(scoring_result.get("reasoning", ""))

        rationale = " | ".join(rationale_parts)

        # 7. Assemble ReasoningResult — COMPUTED ONLY (OD-08)
        result: Dict[str, Any] = {
            "product_id": product_id,
            "product_knowledge_snapshot": product_knowledge_snapshot,
            "evidence_refs": evidence_refs,
            "conflicts": conflicts,
            "unknowns": unknowns,
            "warnings": list(scoring_result.get("warnings", [])) if scoring_result else [],
            "rationale": rationale,
            "claim_boundary_violations": claim_boundary_violations,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "engine_version": ENGINE_VERSION,
            "persistence": "COMPUTED_ONLY",
        }

        if scoring_result:
            result["final_score"] = scoring_result["final_score"]
            result["confidence"] = scoring_result["confidence"]
            result["eligibility"] = scoring_result["eligibility"]
            result["hard_gate_triggered"] = scoring_result["hard_gate_triggered"]
            result["hard_gate_reasons"] = scoring_result["hard_gate_reasons"]
            result["evidence_score"] = evidence_score
            result["need_match"] = need_match
            result["inventory_score"] = inventory_score

        return result
