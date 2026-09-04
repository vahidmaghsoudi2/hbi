"""P4 P0 — Evidence readiness (Contract §8 / V1 rule N.8)."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from sqlalchemy.orm import Session
from app.models.evidence import Evidence


@dataclass
class EvidenceReadinessResult:
    ready: bool
    missing_required: List[str] = field(default_factory=list)
    unacceptable_evidence_ids: List[str] = field(default_factory=list)
    blocking_conflicts: List[str] = field(default_factory=list)
    incomplete_qa_evidence_ids: List[str] = field(default_factory=list)
    summary: str = ""


class EvidenceReadinessService:
    ACCEPTABLE_QA = frozenset({"VERIFIED", "APPROVED"})
    UNACCEPTABLE_QA = frozenset({"REJECTED"})

    def __init__(self, db: Session):
        self.db = db

    def evaluate(self, product_id: str) -> EvidenceReadinessResult:
        evidences = self.db.query(Evidence).filter(Evidence.product_id == product_id).all()
        unacceptable, incomplete_qa, conflicts = [], [], []
        acceptable_count = 0
        for e in evidences:
            qa = (getattr(e, "qa_status", None) or "PENDING").upper()
            conflict = (getattr(e, "conflict_status", None) or "NONE").upper()
            eid = getattr(e, "evidence_id", None) or "?"
            if conflict == "CONFLICT":
                conflicts.append(eid)
            if qa in self.UNACCEPTABLE_QA:
                unacceptable.append(eid)
            elif qa in ("PENDING", "NEEDS_REVIEW"):
                incomplete_qa.append(eid)
            elif qa in self.ACCEPTABLE_QA and conflict != "CONFLICT":
                acceptable_count += 1
        missing = ["__no_acceptable_evidence__"] if acceptable_count == 0 else []
        ready = acceptable_count > 0 and not conflicts and not incomplete_qa and not unacceptable
        summary = "PASS" if ready else (
            f"FAIL missing={missing} unacceptable={unacceptable} "
            f"conflicts={conflicts} incomplete_qa={incomplete_qa}"
        )
        return EvidenceReadinessResult(
            ready=ready, missing_required=missing,
            unacceptable_evidence_ids=unacceptable, blocking_conflicts=conflicts,
            incomplete_qa_evidence_ids=incomplete_qa, summary=summary,
        )
