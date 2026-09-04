"""P4 P0 — Append-only Product Mutation Log (Audit + History)."""
from __future__ import annotations
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.product_mutation_log import ProductMutationLog


def _serialize(obj: Any) -> Optional[str]:
    if obj is None:
        return None
    if isinstance(obj, str):
        return obj
    try:
        return json.dumps(obj, default=str, ensure_ascii=False)
    except TypeError:
        return str(obj)


class MutationLogService:
    def __init__(self, db: Session):
        self.db = db

    def append(self, *, actor_id: str, actor_role: Optional[str], action: str, target_id: str,
               before: Any = None, after: Any = None, diff: Any = None, reason: Optional[str] = None,
               resulting_state: Optional[str] = None, correlation_id: Optional[str] = None,
               target_entity: str = "Product") -> ProductMutationLog:
        row = ProductMutationLog(
            log_id=f"PML-{uuid.uuid4().hex}",
            timestamp=datetime.now(timezone.utc),
            actor_id=actor_id, actor_role=actor_role, action=action,
            target_entity=target_entity, target_id=target_id,
            before_state=_serialize(before), after_state=_serialize(after),
            diff=_serialize(diff), reason=reason, resulting_state=resulting_state,
            correlation_id=correlation_id,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def list_for_product(self, product_id: str) -> List[ProductMutationLog]:
        return (self.db.query(ProductMutationLog)
                .filter(ProductMutationLog.target_id == product_id)
                .order_by(ProductMutationLog.timestamp.asc()).all())

    def product_snapshot(self, product) -> Dict[str, Any]:
        if product is None:
            return {}
        keys = ["product_id", "brand", "product_name", "variant", "size_value", "size_unit",
                "barcode_gtin", "market_region", "country_of_origin", "packaging_version",
                "identity_status", "identity_confidence", "identity_source_refs",
                "qa_verdict", "qa_reviewed_at", "qa_notes", "status", "category_id"]
        return {k: getattr(product, k) for k in keys if hasattr(product, k)}
