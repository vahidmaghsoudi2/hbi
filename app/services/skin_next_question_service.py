"""Deterministic, Case-owned Skin consultation questions.

The flow reuses Case.evidence_gaps; it adds no tables, migrations or LLM
generation. Every answer is customer-reported context, not a diagnosis.
"""
from __future__ import annotations

import json
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.case import Case
from app.services.profile_fact_context_service import ProfileFactContextService


CONTRACT_VERSION = "2"
QUESTION_ID = "skin.primary_need.v2"
LEGACY_QUESTION_ID = "skin.primary_need.v1"
FACTOR_KEY = "concerns"

QUESTION_DEFINITIONS = (
    {
        "question_id": QUESTION_ID,
        "factor": "concerns",
        "prompt": "در این مراجعه کدام‌یک از نیازهای پوستی زیر را می‌خواهید بررسی کنیم؟ امکان انتخاب چند مورد وجود دارد.",
        "answer_type": "MULTI_SELECT",
        "options": [
            {"value": "ضدآفتاب", "label": "ضدآفتاب / SPF"},
            {"value": "آبرسان", "label": "آبرسانی پوست"},
            {"value": "لک صورت", "label": "لک و تیرگی"},
            {"value": "پوست حساس", "label": "حساسیت / قرمزی"},
            {"value": "ضدچروک", "label": "ضدچروک"},
            {"value": "کنترل چربی", "label": "پوست چرب"},
        ],
        "max_length": 200,
    },
    {
        "question_id": "skin.current_type.v1",
        "factor": "skin_profile",
        "prompt": "نوع پوست از نگاه مشتری چیست؟",
        "answer_type": "MULTI_SELECT",
        "options": [
            {"value": "خشک", "label": "خشک"},
            {"value": "چرب", "label": "چرب"},
            {"value": "مختلط", "label": "مختلط"},
            {"value": "معمولی", "label": "معمولی"},
            {"value": "حساس", "label": "حساس"},
            {"value": "unknown", "label": "نامشخص"},
        ],
        "max_length": 120,
    },
    {
        "question_id": "skin.duration.v1",
        "factor": "duration",
        "prompt": "این نگرانی از چه زمانی وجود داشته است؟",
        "answer_type": "SINGLE_SELECT",
        "options": [
            {"value": "less_than_week", "label": "کمتر از یک هفته"},
            {"value": "one_to_four_weeks", "label": "۱ تا ۴ هفته"},
            {"value": "one_to_three_months", "label": "۱ تا ۳ ماه"},
            {"value": "over_three_months", "label": "بیش از ۳ ماه"},
            {"value": "unknown", "label": "نامشخص"},
        ],
    },
    {
        "question_id": "skin.self_reported_severity.v1",
        "factor": "self_reported_severity",
        "prompt": "شدت این نگرانی از نگاه خود مشتری چقدر است؟",
        "helper": "این پاسخ فقط برداشت شخصی مشتری است و ارزیابی شدت بالینی محسوب نمی‌شود.",
        "answer_type": "SINGLE_SELECT",
        "options": [
            {"value": "mild", "label": "کم"},
            {"value": "moderate", "label": "متوسط"},
            {"value": "high", "label": "زیاد"},
            {"value": "unknown", "label": "نامشخص"},
        ],
    },
    {
        "question_id": "skin.affected_area.v1",
        "factor": "affected_area",
        "prompt": "این نگرانی در کدام ناحیه دیده می‌شود؟",
        "answer_type": "SINGLE_SELECT",
        "options": [
            {"value": "face", "label": "صورت"},
            {"value": "body", "label": "بدن"},
            {"value": "face_and_body", "label": "صورت و بدن"},
            {"value": "scalp", "label": "پوست سر"},
            {"value": "hands", "label": "دست‌ها"},
            {"value": "other", "label": "ناحیه دیگر"},
            {"value": "unknown", "label": "نامشخص"},
        ],
    },
    {
        "question_id": "skin.aggravating_factors.v1",
        "factor": "aggravating_factors",
        "prompt": "چه چیزهایی به گفته مشتری این وضعیت را تشدید می‌کنند؟",
        "answer_type": "MULTI_SELECT",
        "options": [
            {"value": "sun_exposure", "label": "آفتاب"},
            {"value": "heat", "label": "گرما"},
            {"value": "cold_weather", "label": "هوای سرد"},
            {"value": "friction", "label": "اصطکاک"},
            {"value": "sweat", "label": "تعریق"},
            {"value": "cosmetics", "label": "برخی محصولات آرایشی/بهداشتی"},
            {"value": "other", "label": "عامل دیگر"},
            {"value": "unknown", "label": "نامشخص"},
        ],
        "max_length": 160,
    },
    {
        "question_id": "skin.product_history.v1",
        "factor": "product_history",
        "prompt": "مشتری اخیراً از چه محصولات پوستی استفاده کرده و چه واکنشی دیده است؟",
        "helper": "نام محصول و واکنش گزارش‌شده را ثبت کنید؛ علت یا حساسیت را از روی این پاسخ استنتاج نکنید.",
        "answer_type": "TEXT",
        "max_length": 600,
    },
    {
        "question_id": "skin.additional_context.v1",
        "factor": "additional_context",
        "prompt": "توضیح تکمیلی مشتری (اختیاری)",
        "answer_type": "TEXT",
        "max_length": 600,
    },
)


class SkinNextQuestionService:
    """Bounded Case-owned consultation capture with no diagnostic inference."""

    def __init__(self, db: Session):
        self.db = db
        self.context_service = ProfileFactContextService(db)

    @staticmethod
    def _decode_case_state(case: Case) -> Dict[str, Any]:
        raw = case.evidence_gaps
        if not raw:
            return {"version": CONTRACT_VERSION, "gaps": [], "answers": []}
        try:
            decoded = json.loads(raw)
        except (TypeError, ValueError):
            return {
                "version": CONTRACT_VERSION,
                "gaps": [],
                "answers": [],
                "legacy_evidence_gaps": raw,
            }
        if not isinstance(decoded, dict):
            return {"version": CONTRACT_VERSION, "gaps": [], "answers": []}
        if not isinstance(decoded.get("gaps"), list):
            decoded["gaps"] = []
        if not isinstance(decoded.get("answers"), list):
            decoded["answers"] = []
        decoded.setdefault("version", CONTRACT_VERSION)
        return decoded

    def _save_state(self, case: Case, state: Dict[str, Any]) -> None:
        case.evidence_gaps = json.dumps(state, ensure_ascii=False, sort_keys=True)
        self.db.add(case)
        self.db.flush()

    @staticmethod
    def _present(value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, (list, tuple, set)):
            return any(str(item).strip() for item in value)
        return bool(str(value).strip())

    def get_question(
        self,
        case: Case,
        current_input: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        state = self._decode_case_state(case)
        answers = {
            item.get("question_id"): item
            for item in state.get("answers", [])
            if isinstance(item, dict) and item.get("question_id")
        }
        supplied = current_input or {}

        for definition in QUESTION_DEFINITIONS:
            question_id = definition["question_id"]
            factor = definition["factor"]
            if question_id in answers:
                continue
            # A legacy primary-need answer is already a Case-owned answer for
            # the same concept; do not ask the v2 primary question again.
            if question_id == QUESTION_ID and LEGACY_QUESTION_ID in answers:
                continue
            # Profile/Quick Intake values do not replace the explicit primary
            # Case answer. Other caller-supplied factors may skip a duplicate
            # prompt only when they are already supplied in this request.
            if factor != FACTOR_KEY and self._present(supplied.get(factor)):
                continue

            mode = "MISSING_INPUT"
            gap_status = "MISSING"
            gap_detail: Dict[str, Any] = {}
            if question_id == QUESTION_ID:
                profile = self.context_service.build(case, supplied)
                trace = profile.get("_profile_fact_context") or {}
                conflict = next(
                    (item for item in trace.get("conflicts", []) if item.get("attribute_key") == FACTOR_KEY),
                    None,
                )
                unknown = next(
                    (item for item in trace.get("unknowns", []) if item.get("attribute_key") == FACTOR_KEY),
                    None,
                )
                if conflict:
                    mode = "CLARIFICATION"
                    gap_status = "CONFLICTED"
                    gap_detail = {
                        "profile_fact_ids": conflict.get("profile_fact_ids", []),
                        "values": conflict.get("values", []),
                    }
                elif unknown:
                    mode = "CLARIFICATION"
                    gap_status = "UNKNOWN"
                    gap_detail = {
                        "profile_fact_id": unknown.get("profile_fact_id"),
                        "value_state": unknown.get("value_state"),
                    }

            question = {
                "question_id": question_id,
                "case_id": case.case_id,
                "factor": factor,
                "mode": mode,
                "prompt": definition["prompt"],
                "answer_type": definition["answer_type"],
                "options": list(definition.get("options", [])),
                "evidence_gap": {
                    "gap_id": f"{case.case_id}:{question_id}",
                    "factor": factor,
                    "status": gap_status,
                    **gap_detail,
                },
            }
            if definition.get("helper"):
                question["helper"] = definition["helper"]
            if definition.get("max_length"):
                question["max_length"] = definition["max_length"]
            return question
        return None

    @staticmethod
    def _validate_answer(definition: Dict[str, Any], answer: Any) -> tuple[Any, str]:
        answer_type = definition["answer_type"]
        allowed = {item["value"] for item in definition.get("options", [])}

        if answer_type == "MULTI_SELECT":
            if isinstance(answer, list):
                parts = [item.strip() for item in answer if isinstance(item, str) and item.strip()]
                if len(parts) != len(answer):
                    raise ValueError("Answer must contain only bounded question options")
            elif isinstance(answer, str):
                parts = [item.strip() for item in answer.split(",") if item.strip()]
            else:
                raise ValueError("Answer must contain bounded question options")
            if not parts or any(item not in allowed for item in parts):
                raise ValueError("Answer must contain only bounded question options")
            if "unknown" in parts and len(parts) > 1:
                raise ValueError("unknown cannot be combined with another option")
            normalized = list(dict.fromkeys(parts))
            return normalized, "UNKNOWN" if normalized == ["unknown"] else "KNOWN"

        if answer_type == "SINGLE_SELECT":
            if isinstance(answer, list):
                if len(answer) != 1 or not isinstance(answer[0], str):
                    raise ValueError("Answer must contain exactly one bounded option")
                value = answer[0].strip()
            elif isinstance(answer, str):
                value = answer.strip()
            else:
                raise ValueError("Answer must be one of the bounded question options")
            if value not in allowed:
                raise ValueError("Answer must be one of the bounded question options")
            return value, "UNKNOWN" if value == "unknown" else "KNOWN"

        if answer_type == "TEXT":
            if isinstance(answer, list):
                if len(answer) > 1 or (answer and not isinstance(answer[0], str)):
                    raise ValueError("Text answer must be a single string")
                value = answer[0].strip() if answer else ""
            elif isinstance(answer, str):
                value = answer.strip()
            else:
                raise ValueError("Text answer must be a string")
            if not value or value.casefold() in {"unknown", "نامشخص", "نمی‌دانم"}:
                return "unknown", "UNKNOWN"
            if len(value) > int(definition.get("max_length", 600)):
                raise ValueError("Text answer exceeds the allowed length")
            return value, "KNOWN"

        raise ValueError("Unsupported answer type")

    def capture_answer(self, case: Case, question_id: str, answer: Any) -> Dict[str, Any]:
        definition = next(
            (item for item in QUESTION_DEFINITIONS if item["question_id"] == question_id),
            None,
        )
        if question_id == LEGACY_QUESTION_ID:
            definition = {
                "question_id": LEGACY_QUESTION_ID,
                "factor": FACTOR_KEY,
                "answer_type": "MULTI_SELECT",
                "options": [
                    {"value": "hydration", "label": "hydration"},
                    {"value": "sun_protection", "label": "sun_protection"},
                ],
            }
        if definition is None:
            raise ValueError("Unsupported question_id")

        value, value_state = self._validate_answer(definition, answer)
        factor = definition["factor"]
        gap_id = f"{case.case_id}:{question_id}"
        gap = {
            "gap_id": gap_id,
            "factor": factor,
            "status": "UNKNOWN" if value_state == "UNKNOWN" else "RESOLVED",
            "resolution": "CUSTOMER_REPORTED_CASE_ANSWER",
            "question_id": question_id,
        }
        state = self._decode_case_state(case)
        state["version"] = CONTRACT_VERSION
        state["gaps"] = [
            item for item in state["gaps"]
            if not isinstance(item, dict) or item.get("gap_id") != gap_id
        ] + [gap]
        answer_record = {
            "question_id": question_id,
            "factor": factor,
            "value": value,
            "source": "CURRENT_CASE_CONSULTATION",
            "value_state": value_state,
        }
        state["answers"] = [
            item for item in state["answers"]
            if not isinstance(item, dict) or item.get("question_id") != question_id
        ] + [answer_record]
        self._save_state(case, state)
        return {
            "case_id": case.case_id,
            "question_id": question_id,
            "factor": factor,
            "answer": value,
            "value_state": value_state,
            "source": "CURRENT_CASE_CONSULTATION",
            "evidence_gap": gap,
        }

    @classmethod
    def current_input_from_case(cls, case: Case) -> Dict[str, Any]:
        state = cls._decode_case_state(case)
        latest_by_question = {
            item.get("question_id"): item
            for item in state.get("answers", [])
            if isinstance(item, dict) and item.get("question_id")
        }
        result: Dict[str, Any] = {}
        primary = latest_by_question.get(QUESTION_ID) or latest_by_question.get(LEGACY_QUESTION_ID)
        if primary:
            value = primary.get("value")
            result[FACTOR_KEY] = value if isinstance(value, list) else [value]
        skin_type = latest_by_question.get("skin.current_type.v1")
        if skin_type:
            value = skin_type.get("value")
            result["skin_profile"] = ",".join(value) if isinstance(value, list) else value
        return result
