"""Persian, user-facing rendering for the Hair Color intake/triage response.

This renderer is informational only. It never translates a blocked response into
recommendations, chemistry instructions, formula/process steps, or guarantees.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any


_STATUS_MESSAGES = {
    "SAFETY_STOP_NO_EXECUTION_SUGGESTION": (
        "بررسی به‌دلیل اعلام نگرانی ایمنی متوقف شد.",
        "تا بررسی فرد متخصص، از ادامه مسیر مشاوره یا اجرای کار خودداری کنید.",
    ),
    "OUT_OF_V1_SCOPE": (
        "این درخواست در محدوده نسخه فعلی مشاوره نیست.",
        "برای بررسی، به متخصص واجد صلاحیت مراجعه کنید.",
    ),
    "NEEDS_INFORMATION_OR_TEST": (
        "اطلاعات پرونده کافی یا یکدست نیست؛ فعلاً پیشنهاد قطعی ارائه نمی‌شود.",
        "موارد مشخص‌شده را روشن کنید و سپس ارزیابی تازه انجام دهید.",
    ),
    "NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW": (
        "این پرونده به بررسی حضوری یا متخصص نیاز دارد.",
        "سامانه در حال حاضر مبنای تأییدشده‌ای برای پیشنهاد قابل اتکا ندارد.",
    ),
    "SYSTEM_REASONED_SUGGESTION": (
        "پاسخ ساختاریافته آماده بررسی تخصصی است.",
        "این وضعیت به معنی تأیید نهایی یا اجازه اجرا نیست.",
    ),
}


def render_persian_response(response: Mapping[str, Any]) -> dict[str, Any]:
    """Return a safe, compact Persian presentation for a validated response."""
    status = response.get("consultation_status")
    title, message = _STATUS_MESSAGES.get(
        status,
        ("وضعیت مشاوره مشخص نیست.", "پاسخ باید بررسی شود؛ هیچ اقدام اجرایی از آن برداشت نکنید."),
    )
    raw_missing = response.get("missing_information", [])
    missing_fields: list[str] = []
    if isinstance(raw_missing, list):
        for item in raw_missing:
            if isinstance(item, Mapping):
                field = item.get("field")
                if isinstance(field, str) and field.strip() and field not in missing_fields:
                    missing_fields.append(field)
            elif isinstance(item, str) and item.strip() and item not in missing_fields:
                missing_fields.append(item)

    return {
        "title": title,
        "message": message,
        "missing_fields": missing_fields,
        "next_step": "تکمیل داده‌های لازم یا ارجاع به متخصص؛ بدون توصیه رنگ یا دستور اجرا.",
        "options": [],
        "execution_authorized": False,
    }
