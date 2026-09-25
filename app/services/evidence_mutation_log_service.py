"""G4 — append-only Evidence mutation audit service."""
from __future__ import annotations
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.evidence_mutation_log import EvidenceMutationLog


def _serialize(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value, default=str, ensure_ascii=False)


class EvidenceMutationLogService:
    def __init__(self, db: Session):
        self.db = db

    def append(
        self,
        *,
        actor_id: str,
        actor_role: Optional[str],
        action: str,
        target_id: str,
        product_id: str,
        before: Any = None,
        after: Any = None,
        diff: Any = None,
        reason: Optional[str] = None,
        resulting_state: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> EvidenceMutationLog:
        row = EvidenceMutationLog(
            log_id=f"EML-{uuid.uuid4().hex}",
            timestamp=datetime.now(timezone.utc),
            actor_id=actor_id,
            actor_role=actor_role,
            action=action,
            target_entity="Evidence",
            target_id=target_id,
            product_id=product_id,
            before_state=_serialize(before),
            after_state=_serialize(after),
            diff=_serialize(diff),
            reason=reason,
            resulting_state=resulting_state,
            correlation_id=correlation_id,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def list_for_evidence(self, evidence_id: str) -> List[EvidenceMutationLog]:
        return (
            self.db.query(EvidenceMutationLog)
            .filter(EvidenceMutationLog.target_id == evidence_id)
            .order_by(EvidenceMutationLog.timestamp.asc())
            .all()
        )

    def list_for_product(self, product_id: str) -> List[EvidenceMutationLog]:
        return (
            self.db.query(EvidenceMutationLog)
            .filter(EvidenceMutationLog.product_id == product_id)
            .order_by(EvidenceMutationLog.timestamp.asc())
            .all()
        )

    @staticmethod
    def snapshot(evidence) -> Dict[str, Any]:
        if evidence is None:
            return {}
        keys = [
            "evidence_id", "product_id", "claim_id", "source_type",
            "source_reference", "claim", "field", "market_region", "notes",
            "claim_type", "evidence_strength", "evidence_status",
            "conflict_status", "source_date", "evidence_date", "qa_status",
        ]
        return {key: getattr(evidence, key) for key in keys if hasattr(evidence, key)}
