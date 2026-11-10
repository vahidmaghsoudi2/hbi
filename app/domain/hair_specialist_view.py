"""Specialist-facing, read-only presentation projection for HBI Hair row 69.

Only synthetic CATALOG_READY context is presented. This module intentionally
does not expose a chemical recommendation, execution instruction, raw engine
trace, customer data, acceptance, or execution consent.
"""
from __future__ import annotations

from typing import Any

from app.domain.hair_data_governance import is_permitted_synthetic_case
from app.domain.hair_knowledge_case_bridge import HairDecisionRun


_VIEW_VERSION = "1"
_LIMITATIONS = (
    "این خروجی فقط تطبیق هویت کاتالوگی را در دادهٔ مصنوعی نشان می‌دهد؛ پیشنهاد رنگ یا ترکیب رنگ نیست.",
    "هیچ ارزیابی شیمیایی، ایمنی، سازگاری محصول یا پیش‌بینی نتیجه انجام نشده است.",
    "این خروجی برای مشتری نیست و مجوز نمایش پیشنهاد به مشتری یا اجرای خدمت ایجاد نمی‌کند.",
    "نسخه/ویرایش رسمی ناشر و زمان ثبت رسمی ناشر در این برش احراز نشده‌اند.",
    "هیچ دادهٔ واقعی مشتری دریافت یا ذخیره نمی‌شود؛ خروجی فقط محاسبه‌ای و موقت است.",
)
_STATUS_MESSAGES = {
    "CONTEXT_READY_FOR_CATALOG_IDENTITY_REASONING": (
        "زمینهٔ مصنوعی به Snapshot کاتالوگ متصل شد؛ این نتیجه صرفاً آماده‌بودن زمینه برای بررسی هویت کاتالوگی را نشان می‌دهد."
    ),
    "STOP_DATA_POLICY": "نمایش متوقف شد: سیاست داده فقط پروندهٔ مصنوعی را می‌پذیرد.",
    "STOP_OUT_OF_DOMAIN": "نمایش متوقف شد: نوع خدمت خارج از دامنهٔ این برش است.",
    "STOP_DATA_GAP": "نمایش متوقف شد: دادهٔ ضروری یا نسخهٔ پرونده ناقص است.",
    "STOP_KNOWLEDGE_GAP": "نمایش متوقف شد: دانش یا مرجع قابل‌ردیابی کافی نیست.",
}


def build_hair_specialist_view(run: HairDecisionRun) -> dict[str, Any]:
    """Create a safe, specialist-internal projection from a computed-only run."""
    if not isinstance(run, HairDecisionRun):
        raise TypeError("run must be a HairDecisionRun")

    synthetic_allowed = is_permitted_synthetic_case(
        case_id=run.case_id,
        synthetic_data=run.case_id.startswith("SYNTHETIC-"),
    )
    if (not synthetic_allowed or run.persistence != "COMPUTED_ONLY"\n            or run.status == "STOP_DATA_POLICY"):
        raise ValueError("Only synthetic, computed-only Hair runs can be presented")

    raw_result = run.reasoning_result or {}
    raw_evidence = raw_result.get("evidence_refs", ())
    evidence = []
    if isinstance(raw_evidence, (list, tuple)):
        for item in raw_evidence:
            if not isinstance(item, dict):
                continue
            evidence.append({
                "evidence_id": str(item.get("evidence_id") or item.get("id") or "UNSPECIFIED"),
                "source_type": str(item.get("source_type") or "UNSPECIFIED"),
                "source_reference": str(item.get("source_reference") or item.get("source") or "UNSPECIFIED"),
                "qa_status": str(item.get("qa_status") or "UNSPECIFIED"),
            })

    return {
        "view_version": _VIEW_VERSION,
        "audience": "INTERNAL_REVIEW_ONLY",
        "data_class": "SYNTHETIC_ONLY",
        "case": {
            "case_id": run.case_id,
            "case_version": run.case_version,
            "goal_version": run.goal_version,
            "service_kind": ("CATALOG_READY" if run.status != "STOP_OUT_OF_DOMAIN" else "OUT_OF_SCOPE"),
        },
        "decision": {
            "status": run.status,
            "reason_code": run.reason_code,
            "summary_fa": _STATUS_MESSAGES.get(
                run.status,
                "وضعیت این اجرا در قرارداد نمایش تعریف نشده است؛ نتیجه منتشر نمی‌شود.",
            ),
            "recommendation": None,
            "display_allowed": False,
            "client_visible": False,
        },
        "evidence": evidence,
        "lineage": {
            "run_id": run.run_id,
            "knowledge_package_id": run.package_id,
            "knowledge_package_version": run.package_version,
            "rule_id": run.rule_id,
            "rule_version": run.rule_version,
            "snapshot_id": run.snapshot_id,
            "content_sha256": run.content_sha256,
            "engine_version": run.engine_version,
            "dependencies": [
                {
                    "kind": dependency.kind,
                    "dependency_id": dependency.dependency_id,
                    "version": dependency.version,
                }
                for dependency in run.dependencies
            ],
            "persistence": "COMPUTED_ONLY",
        },
        "review_controls": {
            "specialist_review_required_by_this_slice": False,
            "specialist_review_recorded": False,
            "acceptance_inherited": False,
            "execution_consent_inherited": False,
            "available_actions": [],
        },
        "limitations": list(_LIMITATIONS),
    }


__all__ = ["build_hair_specialist_view"]
