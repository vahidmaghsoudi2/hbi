"""Deterministic, read-only Product Knowledge gap reporting.

Missing knowledge is recorded for later completion; it is not an eligibility
gate. Existing recommendation safety and governance gates remain authoritative.
"""
import json
from typing import Any, Dict, List, Optional


KNOWLEDGE_FIELDS = (
    ("ingredients", "ترکیبات"),
    ("known_use_cases", "موارد کاربرد"),
    ("usage_instructions", "دستور مصرف"),
    ("contraindications", "موارد منع مصرف و احتیاط"),
    ("evidence_refs", "مراجع شواهد"),
)


def _nonempty(value: Any) -> bool:
    return value is not None and bool(str(value).strip())


def _domain_statuses(pk: Any) -> Dict[str, str]:
    raw = getattr(pk, "domain_evidence_status", None) if pk is not None else None
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except (TypeError, ValueError):
            return {}
    if not isinstance(raw, dict):
        return {}
    return {
        str(key).strip().lower(): str(value).strip().upper()
        for key, value in raw.items()
        if key is not None and value is not None
    }


def build_product_knowledge_gap_report(
    pk: Any,
    evidences: Optional[List[Any]] = None,
    product_market_region: Optional[str] = None,
) -> List[Dict[str, str]]:
    """Return field-level status records without mutating any model or data."""
    evidences = evidences or []
    statuses = _domain_statuses(pk)
    report: List[Dict[str, str]] = []

    for field, label in KNOWLEDGE_FIELDS:
        value = getattr(pk, field, None) if pk is not None else None
        if not _nonempty(value):
            report.append({
                "field": field,
                "label": label,
                "status": "MISSING",
                "message": f"{label}: اطلاعات ثبت نشده و باید در تکمیل بعدی بررسی شود.",
            })
            continue

        if field == "evidence_refs":
            try:
                refs = json.loads(value) if isinstance(value, str) else value
            except (TypeError, ValueError):
                refs = None
            if not isinstance(refs, list) or not refs:
                report.append({
                    "field": field, "label": label, "status": "PARTIAL",
                    "message": "مراجع شواهد قابل‌خواندن نیستند؛ ردیابی منبع نیازمند تکمیل است.",
                })
                continue
            by_claim = {
                getattr(ev, "claim_id", None): ev
                for ev in evidences
                if getattr(ev, "claim_id", None)
                and getattr(ev, "product_id", None) == getattr(pk, "product_id", None)
            }
            unresolved = [ref for ref in refs if ref not in by_claim]
            if unresolved:
                report.append({
                    "field": field, "label": label, "status": "PARTIAL",
                    "message": f"{len(unresolved)} مرجع به شاهد همین محصول متصل نشد؛ ردیابی منبع نیازمند تکمیل است.",
                })
                continue
            product_market = (product_market_region or getattr(pk, "market_region", None) or "").strip().casefold()
            scope_unknown = False
            scope_mismatch = False
            for ref in refs:
                evidence_market = (getattr(by_claim[ref], "market_region", None) or "").strip().casefold()
                if not product_market or not evidence_market:
                    scope_unknown = True
                elif product_market != evidence_market:
                    scope_mismatch = True
            if scope_mismatch or scope_unknown:
                detail = "بازار شاهد با بازار محصول هم‌خوان نیست." if scope_mismatch else "دامنه بازار محصول یا شاهد مشخص نیست؛ هم‌خوانی قابل تأیید نیست."
                report.append({
                    "field": field, "label": label, "status": "PARTIAL",
                    "message": f"{detail} ردیابی نسخه بسته‌بندی نیز در مدل فعلی Evidence قابل اثبات نیست.",
                })
                continue
            if any((getattr(by_claim[ref], "conflict_status", "") or "").upper() == "CONFLICT" for ref in refs):
                status = "CONFLICT"
            else:
                status = "SUPPORTED"
            report.append({
                "field": field, "label": label, "status": status,
                "message": ("مراجع به شواهد همین محصول و بازار متصل شدند؛ ردیابی نسخه بسته‌بندی در مدل فعلی قابل اثبات نیست."
                            if status == "SUPPORTED" else "در مراجع شواهد تعارض ثبت شده است."),
            })
            continue

        domain_status = statuses.get(field)
        if domain_status not in {"SUPPORTED", "PARTIAL", "CONFLICT"}:
            status = "NOT_ASSESSED"
            message = f"{label}: متن ثبت شده، اما وضعیت ارزیابی این حوزه مشخص نیست."
        else:
            status = domain_status
            message = {
                "SUPPORTED": f"{label}: وضعیت پشتیبانی در ارزیابی حوزه ثبت شده است.",
                "PARTIAL": f"{label}: اطلاعات این حوزه ناقص است و باید تکمیل شود.",
                "CONFLICT": f"{label}: تعارض ثبت‌شده نیازمند بررسی است.",
            }[status]
        report.append({
            "field": field,
            "label": label,
            "status": status,
            "message": message,
        })

    return report


def consultation_gap_warnings(report: List[Dict[str, str]]) -> List[str]:
    """Customer-consultation disclosure for missing/unassessed/partial PK only."""
    return [
        f"اطلاعات ناقص محصول ({item['label']}): این پاسخ بر پایه اطلاعات موجود ارائه شده و این مورد برای تکمیل بعدی ثبت شده است."
        for item in report
        if item["status"] in {"MISSING", "NOT_ASSESSED", "PARTIAL"}
    ]
