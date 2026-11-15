"""Specialist-facing, read-only presentation projection for HBI Hair row 69.

Only synthetic CATALOG_READY context is presented. This module intentionally
does not expose a chemical recommendation, execution instruction, raw engine
trace, customer data, acceptance, or execution consent.
"""
from __future__ import annotations

from typing import Any

from app.domain.hair_data_governance import (
    is_permitted_synthetic_case,
    is_permitted_synthetic_identifier,
    is_permitted_synthetic_version,
)
from app.domain.hair_knowledge_case_bridge import (
    HairDecisionRun,
    HairDependency,
    build_approved_catalog_knowledge_package,
    build_catalog_identity_rule,
)
from app.reasoning.reasoning_engine import ENGINE_VERSION


_VIEW_VERSION = "1"
_LIMITATIONS = (
    "این خروجی فقط تطبیق هویت کاتالوگی را در دادهٔ مصنوعی نشان می‌دهد؛ پیشنهاد رنگ یا ترکیب رنگ نیست.",
    "هیچ ارزیابی شیمیایی، ایمنی، سازگاری محصول یا پیش‌بینی نتیجه انجام نشده است.",
    "این خروجی برای مشتری نیست و مجوز نمایش پیشنهاد به مشتری یا اجرای خدمت ایجاد نمی‌کند.",
    "نسخه/ویرایش رسمی ناشر و زمان ثبت رسمی ناشر در این برش احراز نشده‌اند.",
    "هیچ دادهٔ واقعی مشتری دریافت یا ذخیره نمی‌شود؛ خروجی فقط محاسبه‌ای و موقت است.",
)
_SAFE_REASON_CODES = frozenset({
    "REAL_CLIENT_DATA_BLOCKED_BY_PO_66_09",
    "CASE_OR_GOAL_VERSION_MISSING",
    "UNSAFE_CASE_OR_GOAL_VERSION_TOKEN",
    "SERVICE_KIND_OUTSIDE_ROW_68_CATALOG_SCOPE",
    "APPROVED_CATALOG_SNAPSHOT_UNAVAILABLE",
    "KNOWLEDGE_PACKAGE_NOT_APPROVED_OR_VERSIONED",
    "KNOWLEDGE_PACKAGE_SNAPSHOT_MISMATCH",
    "KNOWLEDGE_PACKAGE_HAS_NO_CLAIMS",
    "KNOWLEDGE_CLAIM_NOT_APPROVED_OR_TRACEABLE",
    "RULE_NOT_ACTIVE_WITHIN_APPROVED_CATALOG_SCOPE",
    "CASE_CATALOG_IDENTITY_INVALID",
    "CASE_IDENTITY_NOT_IN_PO_APPROVED_CATALOG_SNAPSHOT",
    "SYNTHETIC_CASE_BOUND_TO_APPROVED_CATALOG_KNOWLEDGE",
    "CATALOG_IDENTITY_REASONING_ENGINE_FAILED",
})
_REQUIRED_IDENTITY_FIELDS = ("brand", "series", "shade_number", "shade_name")


def _safe_reason_code(value: object) -> str:
    if isinstance(value, str) and value in _SAFE_REASON_CODES:
        return value
    prefix = "CASE_CATALOG_IDENTITY_INCOMPLETE:"
    if isinstance(value, str) and value.startswith(prefix):
        fields = value[len(prefix):].split(",")
        if fields and all(field in _REQUIRED_IDENTITY_FIELDS for field in fields):
            return prefix + ",".join(fields)
    return "UNRECOGNIZED_REASON_CODE"


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
    if not is_permitted_synthetic_identifier(run.run_id):
        raise ValueError("Only bounded synthetic run identifiers can be presented")

    version_values = (
        (run.case_version, "case"),
        (run.goal_version, "goal"),
    )
    for value, kind in version_values:
        if value in ("", None):
            if run.status != "STOP_DATA_GAP":
                raise ValueError("Only data-gap runs may omit case or goal version tokens")
        elif not is_permitted_synthetic_version(value, kind=kind):
            raise ValueError("Only typed synthetic version tokens can be presented")

    synthetic_allowed = is_permitted_synthetic_case(
        case_id=run.case_id,
        synthetic_data=run.case_id.startswith("SYNTHETIC-"),
    )
    if (
        not synthetic_allowed
        or run.persistence != "COMPUTED_ONLY"
        or run.status == "STOP_DATA_POLICY"
    ):
        raise ValueError("Only synthetic, computed-only Hair runs can be presented")

    package = build_approved_catalog_knowledge_package()
    if package is None:
        raise ValueError("Approved package lineage is unavailable")
    rule = build_catalog_identity_rule(package)
    expected_dependencies = (
        ("CASE", run.case_id, run.case_version),
        ("GOAL", run.case_id, run.goal_version),
        ("KNOWLEDGE_PACKAGE", package.package_id, package.version),
        ("RULE", rule.rule_id, rule.version),
        ("CATALOG_SNAPSHOT", package.snapshot_id, package.content_sha256),
    )
    actual_dependencies = tuple(
        (dependency.kind, dependency.dependency_id, dependency.version)
        for dependency in run.dependencies
        if isinstance(dependency, HairDependency)
    ) if isinstance(run.dependencies, tuple) else ()
    expected_lineage = (
        run.package_id == package.package_id
        and run.package_version == package.version
        and run.rule_id == rule.rule_id
        and run.rule_version == rule.version
        and run.snapshot_id == package.snapshot_id
        and run.content_sha256 == package.content_sha256
        and run.engine_version == ENGINE_VERSION
        and actual_dependencies == expected_dependencies
        and len(actual_dependencies) == len(run.dependencies)
    )
    if not expected_lineage:
        raise ValueError("Specialist package and dependency lineage failed validation")

    evidence = []
    if run.status == "CONTEXT_READY_FOR_CATALOG_IDENTITY_REASONING" and run.reasoning_result is None:
        raise ValueError("Successful specialist runs must carry approved evidence lineage")
    if run.reasoning_result is not None:
        package = build_approved_catalog_knowledge_package()
        if package is None or not isinstance(run.reasoning_result, dict):
            raise ValueError("Approved evidence package is unavailable for specialist projection")

        expected_evidence = []
        for claim in package.claims:
            expected_evidence.append({
                "evidence_id": claim.claim_id,
                "source_type": "APPROVED_HBI_KNOWLEDGE_PACKAGE",
                "source_reference": claim.source_url,
                "qa_status": claim.status,
            })
        for field in ("brand", "series", "shade_number", "shade_name"):
            expected_evidence.append({
                "evidence_id": f"{run.case_id}:{field}:{run.case_version}",
                "source_type": "SYNTHETIC_CASE_SNAPSHOT",
                "source_reference": f"synthetic://{run.case_id}/{field}",
                "qa_status": "SYNTHETIC_ONLY",
            })

        raw_evidence = run.reasoning_result.get("evidence_refs")
        if not isinstance(raw_evidence, (list, tuple)) or len(raw_evidence) != len(expected_evidence):
            raise ValueError("Specialist evidence lineage is incomplete or unexpected")
        actual_by_id = {}
        for item in raw_evidence:
            if not isinstance(item, dict):
                raise ValueError("Specialist evidence entries must be structured records")
            evidence_id = item.get("evidence_id") or item.get("id")
            if not isinstance(evidence_id, str) or evidence_id in actual_by_id:
                raise ValueError("Specialist evidence identifiers must be unique strings")
            actual_by_id[evidence_id] = item

        if set(actual_by_id) != {item["evidence_id"] for item in expected_evidence}:
            raise ValueError("Specialist evidence identifiers do not match the approved lineage")
        for expected in expected_evidence:
            actual = actual_by_id[expected["evidence_id"]]
            for field in ("source_type", "source_reference", "qa_status"):
                actual_value = (
                    actual.get("source_reference") or actual.get("source")
                    if field == "source_reference"
                    else actual.get(field)
                )
                if actual_value != expected[field]:
                    raise ValueError("Specialist evidence lineage failed validation")
            evidence.append(expected)

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
            "reason_code": _safe_reason_code(run.reason_code),
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
