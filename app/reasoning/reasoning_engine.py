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
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from .conflict_analyzer import ConflictAnalyzer, ConflictSeverity
from .claim_validator import ClaimValidator


ENGINE_VERSION = "0.1.0-GATE-7-3"


class ReasoningEngine:
    """
    Produces a ReasoningResult that is purely computed.
    Never persists anything to DB (OD-08).
    """

    def __init__(self):
        self.conflict_analyzer = ConflictAnalyzer()
        self.claim_validator = ClaimValidator()

    def run(
        self,
        product_id: str,
        product_knowledge_snapshot: Optional[Dict[str, Any]] = None,
        evidence_list: Optional[List[Dict[str, Any]]] = None,
        existing_conflicts: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Main entry point.

        Returns a complete ReasoningResult (computed only).
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

        # 4. Unknowns (Framework 5) — simple surface for now
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

        # 5. Build human-readable rationale
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

        rationale = " | ".join(rationale_parts)

        # 6. Assemble ReasoningResult — COMPUTED ONLY (OD-08)
        result = {
            "product_id": product_id,
            "product_knowledge_snapshot": product_knowledge_snapshot,
            "evidence_refs": evidence_refs,
            "conflicts": conflicts,
            "unknowns": unknowns,
            "warnings": [],
            "rationale": rationale,
            "claim_boundary_violations": claim_boundary_violations,
            "generated_at": datetime.utcnow().isoformat(),
            "engine_version": ENGINE_VERSION,
            "persistence": "COMPUTED_ONLY",  # explicit OD-08 marker
        }

        # Hard guarantee: we never write this object anywhere.
        return result
