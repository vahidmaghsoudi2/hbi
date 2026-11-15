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



def _parse_evidence_refs(value: Any) -> Optional[List[str]]:
    """Read both JSON-list and the established comma-separated rebuild format."""
    if isinstance(value, list):
        refs = value
    elif isinstance(value, str):
        try:
            decoded = json.loads(value)
        except (TypeError, ValueError):
            # A malformed JSON-looking value must not be reinterpreted as a
            # comma-separated reference; report it as unreadable instead.
            if value.lstrip().startswith(("[", "{", '"')):
                return None
            refs = value.split(",")
        else:
            refs = decoded
    else:
        return None

    if not isinstance(refs, list) or not refs:
        return None
    if any(not isinstance(ref, str) or not ref.strip() for ref in refs):
        return None
    return [ref.strip() for ref in refs]


def _domain_statuses(pk: Any) -> Dict[str, str]:
    raw = getattr(pk, "domain_evidence_status", None) if pk is not None else None
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except (TypeError, ValueError):
            return {}
    if not isinstance(raw, dict):
        return {}
    aliases = {
        "use_case": "known_use_cases",
        "usage_instruction": "usage_instructions",
        "usage": "usage_instructions",
    }
    normalized: Dict[str, str] = {}
    # Canonical keys take precedence if both a canonical key and its legacy
    # alias are present; aliases fill only a missing canonical status.
    for key, value in raw.items():
        if key is None or value is None:
            continue
        raw_key = str(key).strip().lower()
        canonical = aliases.get(raw_key, raw_key)
        status = str(value).strip().upper()
        if canonical not in normalized or raw_key == canonical:
            normalized[canonical] = status
    return normalized


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
            refs = _parse_evidence_refs(value)
            if refs is None:
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

            product_market = (
                product_market_region or getattr(pk, "market_region", None) or ""
            ).strip().casefold()
            in_scope_refs = []
            scope_unknown = False
            scope_mismatch = False
            for ref in refs:
                evidence_market = (
                    getattr(by_claim[ref], "market_region", None) or ""
                ).strip().casefold()
                if not product_market or not evidence_market:
                    scope_unknown = True
                elif product_market != evidence_market:
                    scope_mismatch = True
                else:
                    in_scope_refs.append(ref)

            # An explicit in-scope conflict is more important than QA status.
            # Unknown or foreign-market conflicts must not leak into this scope.
            if any(
                (getattr(by_claim[ref], "conflict_status", None) or "").strip().upper()
                == "CONFLICT"
                for ref in in_scope_refs
            ):
                report.append({
                    "field": field, "label": label, "status": "CONFLICT",
                    "message": "در مراجع شواهد همین محصول و بازار تعارض ثبت شده است.",
                })
                continue

            if scope_mismatch or scope_unknown:
                detail = (
                    "بازار شاهد با بازار محصول هم‌خوان نیست."
                    if scope_mismatch
                    else "دامنه بازار محصول یا شاهد مشخص نیست؛ هم‌خوانی قابل تأیید نیست."
                )
                report.append({
                    "field": field, "label": label, "status": "PARTIAL",
                    "message": f"{detail} ردیابی نسخه بسته‌بندی نیز در مدل فعلی Evidence قابل اثبات نیست.",
                })
                continue

            unreviewed_refs = [
                ref for ref in in_scope_refs
                if (getattr(by_claim[ref], "qa_status", None) or "").strip().upper()
                not in {"APPROVED", "VERIFIED"}
            ]
            if unreviewed_refs:
                report.append({
                    "field": field, "label": label, "status": "PARTIAL",
                    "message": f"{len(unreviewed_refs)} شاهد هنوز QA تأییدشده ندارد؛ وضعیت شواهد تا تکمیل بازبینی قابل اتکا نیست.",
                })
                continue

            report.append({
                "field": field, "label": label, "status": "SUPPORTED",
                "message": "مراجع به شواهد تأییدشده همین محصول و بازار متصل شدند؛ ردیابی نسخه بسته‌بندی در مدل فعلی قابل اثبات نیست.",
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


def evaluate_product_knowledge_completeness(
    pk: Any,
    evidences: Optional[List[Any]] = None,
    product_market_region: Optional[str] = None,
) -> Dict[str, Any]:
    """Return completeness and field-level gaps; never decide candidate eligibility."""
    report = build_product_knowledge_gap_report(
        pk, evidences, product_market_region=product_market_region
    )
    incomplete = [item for item in report if item["status"] != "SUPPORTED"]
    missing_domains = [
        item["field"] for item in report
        if item["status"] in {"MISSING", "NOT_ASSESSED", "PARTIAL"}
    ]
    contraindications = next(
        item for item in report if item["field"] == "contraindications"
    )
    return {
        "status": "complete" if not incomplete else "partial",
        "missing_domains": missing_domains,
        "incomplete_domains": [
            {"field": item["field"], "status": item["status"]}
            for item in incomplete
        ],
        "contraindications_unreviewed": contraindications["status"] in {
            "MISSING", "NOT_ASSESSED", "PARTIAL"
        },
        "pk_record_missing": pk is None,
        "domain_report": report,
    }


def consultation_gap_warnings(
    report: List[Dict[str, str]], *, pk_record_missing: bool = False
) -> List[str]:
    """Prioritized consultation disclosure through the existing warnings channel."""
    warnings = []
    if pk_record_missing:
        warnings.append(
            "هشدار جدی PK: برای این محصول هیچ پرونده Product Knowledge ثبت نشده است؛ "
            "هر پنج حوزه نامعلوم‌اند. محصول صرفاً به‌دلیل نبود PK از candidate حذف نشده، "
            "اما ایمنی و موارد منع مصرف بررسی/تأیید نشده‌اند؛ این به معنی نبود منع مصرف نیست "
            "و تکمیل پرونده ضروری است."
        )
        return warnings

    warnings.extend(
        f"هشدار برای اپراتور/پزشک - اطلاعات ناقص محصول ({item['label']}): پاسخ فقط بر پایه داده‌های موجود ارائه شود؛ این مورد برای تکمیل بعدی ثبت شده است."
        for item in report
        if item["status"] in {"MISSING", "NOT_ASSESSED", "PARTIAL"}
        and item["field"] != "contraindications"
    )
    if any(
        item["field"] == "contraindications"
        and item["status"] in {"MISSING", "NOT_ASSESSED", "PARTIAL"}
        for item in report
    ):
        warnings.append(
            "هشدار به اپراتور/پزشک: موارد منع مصرف هنوز بررسی/تأیید نشده‌اند؛ خالی بودن این بخش به‌معنی نبود منع مصرف نیست."
        )
    return warnings
