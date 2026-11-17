"""Read-only Acceptance Report builder governed by HBI Phase 0 policy."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.governance import ACTION_QA_CHANGE
from app.domain.claim_taxonomy import ALLOWED_CLAIM_TYPES
from app.models.evidence import Evidence
from app.models.evidence_mutation_log import EvidenceMutationLog
from app.models.product import Product
from app.models.product_knowledge import ProductKnowledge
from app.models.product_mutation_log import ProductMutationLog


_VERIFIED = "VERIFIED"
_QA_VALUES = {"VERIFIED", "REJECTED", "NEEDS_REVIEW", "PENDING", "APPROVED"}
_KNOWLEDGE_FIELDS = {
    "ingredients", "ingredient_roles", "ingredient_role",
    "claimed_benefits", "claimed_benefit", "benefit",
    "known_use_cases", "known_use_case", "use_case",
    "contraindications", "usage_instructions", "usage_instruction", "usage",
    "manufacturer_claims", "manufacturer_claim", "other_attributes",
    "other_attribute", "claim",
}
_PK_CONTENT_FIELDS = (
    "ingredients", "ingredient_roles", "claimed_benefits", "known_use_cases",
    "contraindications", "usage_instructions", "manufacturer_claims", "other_attributes",
)


def _text(value: Any) -> str:
    return str(value or "").strip()


def _nonempty(value: Any) -> bool:
    return bool(_text(value))


def _iso(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()
    return str(value)


def _json_object(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    if not value:
        return {}
    try:
        parsed = json.loads(value)
    except (TypeError, ValueError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _json_refs(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(item) for item in value if _nonempty(item)]
    if not _nonempty(value):
        return []
    try:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return [str(item) for item in parsed if _nonempty(item)]
    except (TypeError, ValueError):
        pass
    return [part.strip() for part in str(value).split(",") if part.strip()]


def _decision_from_log(row: Any, *, product_qa: bool = False) -> Optional[str]:
    after = _json_object(getattr(row, "after_state", None))
    value = after.get("qa_verdict") if product_qa else (
        after.get("qa_status") or getattr(row, "resulting_state", None)
    )
    value = _text(value).upper()
    return value or None


def _decision_record(row: Any, *, product_qa: bool = False) -> Dict[str, Any]:
    after = _json_object(getattr(row, "after_state", None))
    reason = getattr(row, "reason", None)
    decision = _decision_from_log(row, product_qa=product_qa)
    record = {
        "audit_record_id": getattr(row, "log_id", None),
        "audit_timestamp": _iso(getattr(row, "timestamp", None)),
        "actor": getattr(row, "actor_id", None),
        "role": getattr(row, "actor_role", None),
        "decision": decision,
        "reason": reason,
        "reason_status": "PRESENT" if _nonempty(reason) else "MISSING",
    }
    if product_qa:
        # Product QA notes are stored in the after-state snapshot, not in reason.
        record["qa_notes"] = after.get("qa_notes")
    return record


def _scope_status(evidence: Evidence, product: Product) -> Tuple[str, List[str]]:
    reasons: List[str] = []
    evidence_market = _text(getattr(evidence, "market_region", None)).upper()
    product_market = _text(getattr(product, "market_region", None)).upper()
    if not evidence_market or not product_market:
        reasons.append("MARKET_SCOPE_UNKNOWN")
    elif evidence_market != product_market:
        reasons.append("MARKET_SCOPE_MISMATCH")
        return "MIXED", reasons

    # Evidence currently has no formula/version column. Product.packaging_version
    # is not proof that a claim applies to that exact formula or package version.
    reasons.append("EVIDENCE_VERSION_SCOPE_UNAVAILABLE")
    return "UNKNOWN", reasons


def _canonical_field(evidence: Evidence) -> str:
    field = _text(getattr(evidence, "field", None)).lower()
    aliases = {
        "ingredient_role": "ingredient_roles",
        "claimed_benefit": "claimed_benefits",
        "benefit": "claimed_benefits",
        "known_use_case": "known_use_cases",
        "use_case": "known_use_cases",
        "usage_instruction": "usage_instructions",
        "usage": "usage_instructions",
        "manufacturer_claim": "manufacturer_claims",
        "other_attribute": "other_attributes",
    }
    if field == "claim" and _text(getattr(evidence, "claim_type", None)).upper() == "MANUFACTURER_CLAIM":
        return "manufacturer_claims"
    return aliases.get(field, field)


def _eligibility(evidence: Evidence, product: Product) -> Tuple[bool, List[str], str]:
    reasons: List[str] = []
    qa = _text(getattr(evidence, "qa_status", None)).upper()
    conflict = _text(getattr(evidence, "conflict_status", None)).upper()
    field = _text(getattr(evidence, "field", None)).lower()

    if qa != _VERIFIED:
        reasons.append("QA_STATUS_NOT_VERIFIED")
    if conflict == "CONFLICT":
        reasons.append("CONFLICT_UNRESOLVED")
    elif conflict not in {"NONE", "RESOLVED"}:
        reasons.append("CONFLICT_STATUS_UNKNOWN")
    if not field or field not in _KNOWLEDGE_FIELDS:
        reasons.append("INVALID_OR_UNKNOWN_FIELD")
    if not _nonempty(getattr(evidence, "claim", None)):
        reasons.append("CLAIM_MISSING")
    claim_type = _text(getattr(evidence, "claim_type", None)).upper()
    if not claim_type:
        reasons.append("CLAIM_TYPE_MISSING")
    elif claim_type not in ALLOWED_CLAIM_TYPES:
        reasons.append("CLAIM_TYPE_INVALID")
    if not _nonempty(getattr(evidence, "source_type", None)):
        reasons.append("SOURCE_TYPE_MISSING")
    if not _nonempty(getattr(evidence, "source_reference", None)):
        reasons.append("SOURCE_REFERENCE_MISSING")

    scope_status, scope_reasons = _scope_status(evidence, product)
    reasons.extend(scope_reasons)
    return not reasons, sorted(set(reasons)), scope_status


def _audit_history(rows: Iterable[Any], *, product_qa: bool = False) -> List[Dict[str, Any]]:
    selected = []
    for row in rows:
        action = _text(getattr(row, "action", None)).upper()
        if product_qa:
            if action != ACTION_QA_CHANGE:
                continue
        elif action != "VERIFY":
            continue
        decision = _decision_from_log(row, product_qa=product_qa)
        if product_qa:
            if not decision:
                continue
        elif decision not in {"VERIFIED", "REJECTED", "NEEDS_REVIEW"}:
            continue
        selected.append(_decision_record(row, product_qa=product_qa))
    return selected


def _max_timestamp(values: Iterable[Any]) -> Optional[str]:
    valid = []
    for value in values:
        if isinstance(value, datetime):
            normalized = value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)
            valid.append(normalized)
    if not valid:
        return None
    return _iso(max(valid))


def _product_report(
    product: Product,
    evidences: Sequence[Evidence],
    knowledge: Optional[ProductKnowledge],
    evidence_logs: Sequence[Any],
    product_logs: Sequence[Any],
    *,
    audit_tables: Dict[str, bool],
) -> Dict[str, Any]:
    evidence_logs_by_id: Dict[str, List[Any]] = {}
    for row in evidence_logs:
        evidence_logs_by_id.setdefault(row.target_id, []).append(row)
    product_qa_history = _audit_history(product_logs, product_qa=True)

    evidence_items: List[Dict[str, Any]] = []
    counts = {
        "total": len(evidences), "verified": 0, "pending": 0, "needs_review": 0,
        "rejected": 0, "conflicting": 0, "unknown_conflict": 0,
        "eligible": 0, "ineligible": 0, "unknown_scope": 0,
    }
    verified_fields = set()
    source_timestamps: List[Any] = [
        getattr(product, "updated_at", None),
        getattr(knowledge, "updated_at", None) if knowledge else None,
    ]
    for log in product_logs:
        source_timestamps.append(getattr(log, "timestamp", None))

    for ev in evidences:
        qa = _text(getattr(ev, "qa_status", None)).upper() or "UNKNOWN"
        conflict = _text(getattr(ev, "conflict_status", None)).upper() or "UNKNOWN"
        counts["verified"] += qa == "VERIFIED"
        counts["pending"] += qa == "PENDING"
        counts["needs_review"] += qa == "NEEDS_REVIEW"
        counts["rejected"] += qa == "REJECTED"
        counts["conflicting"] += conflict == "CONFLICT"
        counts["unknown_conflict"] += conflict not in {"NONE", "RESOLVED", "CONFLICT"}

        eligible, reasons, scope_status = _eligibility(ev, product)
        counts["eligible"] += eligible
        counts["ineligible"] += not eligible
        counts["unknown_scope"] += scope_status == "UNKNOWN"
        if eligible:
            verified_fields.add(_canonical_field(ev))

        history = _audit_history(evidence_logs_by_id.get(ev.evidence_id, []))
        latest = history[-1] if history else None
        current_notes = _text(getattr(ev, "notes", None))
        if not audit_tables["evidence"]:
            history_status = "UNAVAILABLE"
        elif "[REJECTED_BY_CONFLICT_RESOLUTION" in current_notes:
            history_status = "INCOMPLETE"
        elif history and latest and latest.get("decision") == qa:
            history_status = "CONSISTENT"
        elif history:
            history_status = "INCOMPLETE"
        elif qa in {"VERIFIED", "REJECTED", "NEEDS_REVIEW", "APPROVED"}:
            history_status = "NO_RECORDED_DECISION"
        else:
            history_status = "NO_DECISION_RECORDED"
        evidence_items.append({
            "evidence_id": ev.evidence_id,
            "field": ev.field,
            "claim": ev.claim,
            "claim_type": ev.claim_type,
            "source_type": ev.source_type,
            "source_reference": ev.source_reference,
            "qa_status": qa,
            "conflict_status": conflict,
            "market_region": ev.market_region,
            "scope_status": scope_status,
            "eligible": bool(eligible),
            "eligibility_reasons": reasons,
            "qa_decision_history": history,
            "latest_qa_decision": latest,
            "qa_decision_history_status": history_status,
        })
        source_timestamps.append(getattr(ev, "created_at", None))
        for row in evidence_logs_by_id.get(ev.evidence_id, []):
            source_timestamps.append(getattr(row, "timestamp", None))

    if not evidences:
        readiness = "NOT_ASSESSED"
    elif counts["eligible"] == counts["total"]:
        readiness = "READY"
    elif counts["eligible"] > 0:
        readiness = "PARTIAL"
    else:
        readiness = "BLOCKED"

    stored_fields = []
    if knowledge:
        stored_fields = [
            field for field in _PK_CONTENT_FIELDS
            if _nonempty(getattr(knowledge, field, None))
        ]
    contraindications_status = (
        "VERIFIED" if "contraindications" in verified_fields
        else "UNVERIFIED" if knowledge and _nonempty(knowledge.contraindications)
        else "UNKNOWN"
    )
    limitations = []
    if not audit_tables["evidence"]:
        limitations.append("EVIDENCE_AUDIT_TABLE_UNAVAILABLE")
    if not audit_tables["product"]:
        limitations.append("PRODUCT_AUDIT_TABLE_UNAVAILABLE")
    limitations.append(
        "Evidence model has no evidence-level formula/version scope; Product packaging_version cannot prove Evidence applicability."
    )
    if any(item.get("qa_decision_history_status") in {"INCOMPLETE", "NO_RECORDED_DECISION"} for item in evidence_items):
        limitations.append(
            "At least one current Evidence QA state has no matching per-row QA decision audit record; the report does not fabricate missing history."
        )

    source_timestamp = _max_timestamp(source_timestamps)
    return {
        "schema_version": "1.0.0",
        "report_id": f"AR-{uuid.uuid4().hex}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_data_timestamp": source_timestamp,
        "source_data_timestamp_status": "KNOWN" if source_timestamp else "UNKNOWN",
        "report_status": "COMPLETED",
        "evidence_readiness": readiness,
        "product": {
            "product_id": product.product_id,
            "brand": product.brand,
            "product_name": product.product_name,
            "identity_status": product.identity_status,
            "qa_verdict": product.qa_verdict,
            "lifecycle_status": product.status,
            "market_region": product.market_region,
            "packaging_version": product.packaging_version,
            "product_qa": {
                "qa_reviewed_at": _iso(product.qa_reviewed_at),
                "qa_notes": product.qa_notes,
                "qa_decision_history": product_qa_history,
                "latest_qa_decision": product_qa_history[-1] if product_qa_history else None,
            },
        },
        "evidence_summary": counts,
        "evidence": evidence_items,
        "knowledge": {
            "record_exists": knowledge is not None,
            "evidence_status": (knowledge.evidence_status or "UNKNOWN") if knowledge else "UNKNOWN",
            "knowledge_confidence": knowledge.knowledge_confidence if knowledge else None,
            "domain_evidence_status": _json_object(knowledge.domain_evidence_status) if knowledge else {},
            "stored_content_fields": stored_fields,
            "verified_content_fields": sorted(verified_fields),
            "evidence_refs": _json_refs(knowledge.evidence_refs) if knowledge else [],
            "contraindications_status": contraindications_status,
        },
        "data_availability": {
            "product_qa_audit_available": audit_tables["product"],
            "evidence_audit_available": audit_tables["evidence"],
            "evidence_market_scope_available": hasattr(Evidence, "market_region"),
            "evidence_formula_version_available": hasattr(Evidence, "formula_version"),
            "product_packaging_version_available": hasattr(Product, "packaging_version"),
            "product_packaging_version_value_present": _nonempty(product.packaging_version),
            "product_version_proves_evidence_scope": False,
        },
        "limitations": limitations,
    }


def build_acceptance_reports(db: Session, product_ids: Sequence[str]) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, bool], Dict[str, str]]:
    """Build reports with bounded query count; this function never writes."""
    ids = list(product_ids)
    products = db.query(Product).filter(Product.product_id.in_(ids)).all()
    product_map = {row.product_id: row for row in products}
    found_ids = list(product_map)
    if not found_ids:
        return {}, {"evidence": False, "product": False}, {}

    evidences = db.query(Evidence).filter(Evidence.product_id.in_(found_ids)).all()
    knowledge_rows = db.query(ProductKnowledge).filter(ProductKnowledge.product_id.in_(found_ids)).all()
    knowledge_map = {row.product_id: row for row in knowledge_rows}

    table_names = set(inspect(db.get_bind()).get_table_names())
    evidence_audit_available = EvidenceMutationLog.__tablename__ in table_names
    product_audit_available = ProductMutationLog.__tablename__ in table_names
    evidence_logs: List[Any] = []
    product_logs: List[Any] = []
    if evidence_audit_available:
        try:
            evidence_logs = (
                db.query(EvidenceMutationLog)
                .filter(EvidenceMutationLog.product_id.in_(found_ids))
                .order_by(EvidenceMutationLog.timestamp.asc(), EvidenceMutationLog.log_id.asc())
                .all()
            )
        except SQLAlchemyError:
            db.rollback()
            evidence_audit_available = False
    if product_audit_available:
        try:
            product_logs = (
                db.query(ProductMutationLog)
                .filter(
                    ProductMutationLog.target_entity == "Product",
                    ProductMutationLog.target_id.in_(found_ids),
                )
                .order_by(ProductMutationLog.timestamp.asc(), ProductMutationLog.log_id.asc())
                .all()
            )
        except SQLAlchemyError:
            db.rollback()
            product_audit_available = False

    evidence_by_product: Dict[str, List[Evidence]] = {pid: [] for pid in found_ids}
    evidence_logs_by_product: Dict[str, List[Any]] = {pid: [] for pid in found_ids}
    product_logs_by_product: Dict[str, List[Any]] = {pid: [] for pid in found_ids}
    for row in evidences:
        evidence_by_product.setdefault(row.product_id, []).append(row)
    for row in evidence_logs:
        evidence_logs_by_product.setdefault(row.product_id, []).append(row)
    for row in product_logs:
        product_logs_by_product.setdefault(row.target_id, []).append(row)

    audit_tables = {
        "evidence": evidence_audit_available,
        "product": product_audit_available,
    }
    reports: Dict[str, Dict[str, Any]] = {}
    errors: Dict[str, str] = {}
    for product_id, product in product_map.items():
        try:
            reports[product_id] = _product_report(
                product,
                evidence_by_product.get(product_id, []),
                knowledge_map.get(product_id),
                evidence_logs_by_product.get(product_id, []),
                product_logs_by_product.get(product_id, []),
                audit_tables=audit_tables,
            )
        except Exception as exc:
            # Isolate a malformed row/product so a cohort report can continue.
            errors[product_id] = type(exc).__name__
    return reports, audit_tables, errors
