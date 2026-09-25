"""Governed Product duplicate/naming check service.

Business rules are deliberately deterministic: exact Product ID and exact GTIN can
identify an existing Product; size/variant differences define distinct Products;
packaging-only changes remain the same Product; name similarity is presented for
operator review rather than computed with fuzzy scoring.
"""
from __future__ import annotations

import json
import re
import uuid
from typing import Any, Dict, List, Optional, Set

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationError
from app.models.duplicate_check_audit import DuplicateCheckAudit
from app.models.product import Product
from app.models.user_role import ROLE_ADMIN, ROLE_EDITOR, ROLE_PO, ROLE_REVIEWER_QA


_ROLE_ORDER = (ROLE_PO, ROLE_REVIEWER_QA, ROLE_EDITOR, ROLE_ADMIN)


def _norm(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\\s+", " ", str(value).strip()).casefold()


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, default=str, sort_keys=True)


class DuplicateCheckService:
    def __init__(self, db: Session):
        self.db = db

    def check(self, payload: Dict[str, Any], *, actor_id: str, roles: Set[str]) -> Dict[str, Any]:
        if not actor_id:
            raise ValidationError("Actor is required for duplicate check")

        data = {
            "product_id": payload.get("product_id"),
            "barcode_gtin": payload.get("barcode_gtin"),
            "brand": payload.get("brand"),
            "product_name": payload.get("product_name"),
            "variant": payload.get("variant"),
            "size_value": payload.get("size_value"),
            "size_unit": payload.get("size_unit"),
            "market_region": payload.get("market_region"),
            "packaging_version": payload.get("packaging_version"),
        }

        names = [
            {"product_id": p.product_id, "brand": p.brand, "product_name": p.product_name}
            for p in self.db.query(Product).order_by(Product.product_name.asc(), Product.product_id.asc()).all()
        ]

        result = "NEW"
        candidates: List[Dict[str, Any]] = []
        reason = "NO_CREDIBLE_MATCH"

        explicit_id = _norm(data["product_id"])
        if explicit_id:
            product = self.db.query(Product).filter(Product.product_id == data["product_id"]).first()
            if product:
                conflicts = self._conflicts(product, data)
                result = "EXISTING"
                reason = "EXACT_PRODUCT_ID"
                candidates.append(self._candidate(product, "EXISTING", "PRODUCT_ID", conflicts))

        if result == "NEW" and data["barcode_gtin"]:
            barcode = _norm(data["barcode_gtin"])
            product = self.db.query(Product).filter(Product.barcode_gtin == data["barcode_gtin"]).first()
            if not product:
                product = next((p for p in self.db.query(Product).all() if _norm(p.barcode_gtin) == barcode), None)
            if product:
                result = "EXISTING"
                reason = "EXACT_BARCODE"
                conflicts = self._conflicts(product, data)
                candidates.append(self._candidate(product, "EXISTING", "BARCODE", conflicts))

        if result == "NEW":
            brand = _norm(data["brand"])
            name = _norm(data["product_name"])
            exact_name_candidates = [
                p for p in self.db.query(Product).order_by(Product.product_name.asc(), Product.product_id.asc()).all()
                if name and _norm(p.product_name) == name and (not brand or _norm(p.brand) == brand)
            ]
            for product in exact_name_candidates:
                conflicts = self._conflicts(product, data)
                # PO decision: a size or variant/type/color difference identifies
                # a distinct Product. It is not a duplicate candidate.
                if "size_value" in conflicts or "size_unit" in conflicts or "variant" in conflicts:
                    continue
                tier = "EXACT_NAME_OPERATOR_REVIEW"
                candidates.append(self._candidate(product, "POSSIBLE_MATCH", tier, conflicts))
            if candidates:
                result = "POSSIBLE_MATCH"
                reason = "EXACT_NAME_REQUIRES_OPERATOR_REVIEW"

        audit = DuplicateCheckAudit(
            check_id=f"DCA-{uuid.uuid4().hex}",
            actor_id=actor_id,
            actor_role=next((r for r in _ROLE_ORDER if r in roles), None),
            result=result,
            product_id=data["product_id"],
            input_snapshot=_json(data),
            candidates=_json(candidates),
        )
        self.db.add(audit)
        self.db.flush()

        return {
            "check_id": audit.check_id,
            "result": result,
            "reason": reason,
            "candidates": candidates,
            "naming_reference": names,
            "operator_decision_required": result == "POSSIBLE_MATCH",
            "provenance": {
                "rule_version": "WP-258.1",
                "fuzzy_matching": False,
                "timestamp": audit.timestamp.isoformat() if audit.timestamp else None,
            },
        }

    def list_audits(self, *, product_id: Optional[str] = None, limit: int = 100) -> List[DuplicateCheckAudit]:
        query = self.db.query(DuplicateCheckAudit)
        if product_id:
            query = query.filter(DuplicateCheckAudit.product_id == product_id)
        return query.order_by(DuplicateCheckAudit.timestamp.desc()).limit(min(max(limit, 1), 500)).all()

    @staticmethod
    def _conflicts(product: Product, data: Dict[str, Any]) -> List[str]:
        conflicts: List[str] = []
        if data.get("brand") and _norm(product.brand) != _norm(data["brand"]):
            conflicts.append("brand")
        if data.get("product_name") and _norm(product.product_name) != _norm(data["product_name"]):
            conflicts.append("product_name")
        if data.get("variant") and _norm(product.variant) != _norm(data["variant"]):
            conflicts.append("variant")
        if data.get("size_value") is not None and product.size_value is not None and float(product.size_value) != float(data["size_value"]):
            conflicts.append("size_value")
        if data.get("size_unit") and _norm(product.size_unit) != _norm(data["size_unit"]):
            conflicts.append("size_unit")
        return conflicts

    @staticmethod
    def _candidate(product: Product, result: str, tier: str, conflicts: List[str]) -> Dict[str, Any]:
        return {
            "product_id": product.product_id,
            "brand": product.brand,
            "product_name": product.product_name,
            "variant": product.variant,
            "size_value": product.size_value,
            "size_unit": product.size_unit,
            "packaging_version": product.packaging_version,
            "result": result,
            "match_tier": tier,
            "conflicting_fields": conflicts,
        }
