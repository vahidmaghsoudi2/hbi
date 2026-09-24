"""Minimal deterministic Skin next-question vertical slice.

This module is intentionally bounded to one existing recommendation input:
the canonical `concerns` / primary skin need surface.

No question database, LLM, scoring, ranking, eligibility, or ProfileFact writes.
"""
from __future__ import annotations

import json
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.case import Case
from app.services.profile_fact_context_service import ProfileFactContextService


QUESTION_ID = "skin.primary_need.v1"
FACTOR_KEY = "concerns"
CONTRACT_VERSION = "1"

OPTIONS = (
    {"value": "hydration", "label": "آبرسانی"},
    {"value": "sun_protection", "label": "محافظت در برابر آفتاب"},
)

_PROMPT = "نیاز اصلی پوست شما در این مراجعه چیست؟"


class SkinNextQuestionService:
    """One deterministic Evidence Gap -> Next Question boundary for Skin."""

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
        decoded.setdefault("version", CONTRACT_VERSION)
        decoded.setdefault("gaps", [])
        decoded.setdefault("answers", [])
        return decoded

    def _save_state(self, case: Case, state: Dict[str, Any]) -> None:
        case.evidence_gaps = json.dumps(
            state, ensure_ascii=False, sort_keys=True
        )
        self.db.add(case)
        self.db.flush()

    def _context(self, case: Case, current_input: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        case_input = self.current_input_from_case(case)
        case_input.update(current_input or {})
        return self.context_service.build(case, case_input)

    @staticmethod
    def _has_concern(profile: Dict[str, Any]) -> bool:
        value = profile.get(FACTOR_KEY)
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
        profile = self._context(case, current_input)
        trace = profile.get("_profile_fact_context") or {}

        if self._has_concern(profile):
            return None

        conflict = next(
            (
                item for item in trace.get("conflicts", [])
                if item.get("attribute_key") == FACTOR_KEY
            ),
            None,
        )
        unknown = next(
            (
                item for item in trace.get("unknowns", [])
                if item.get("attribute_key") == FACTOR_KEY
            ),
            None,
        )

        if conflict:
            gap_status = "CONFLICTED"
            gap_detail = {
                "profile_fact_ids": conflict.get("profile_fact_ids", []),
                "values": conflict.get("values", []),
            }
            mode = "CLARIFICATION"
        elif unknown:
            gap_status = "UNKNOWN"
            gap_detail = {
                "profile_fact_id": unknown.get("profile_fact_id"),
                "value_state": unknown.get("value_state"),
            }
            mode = "CLARIFICATION"
        else:
            gap_status = "MISSING"
            gap_detail = {}
            mode = "MISSING_INPUT"

        gap_id = f"{case.case_id}:{QUESTION_ID}"
        return {
            "question_id": QUESTION_ID,
            "case_id": case.case_id,
            "factor": FACTOR_KEY,
            "mode": mode,
            "prompt": _PROMPT,
            "options": list(OPTIONS),
            "evidence_gap": {
                "gap_id": gap_id,
                "factor": FACTOR_KEY,
                "status": gap_status,
                **gap_detail,
            },
        }

    def capture_answer(self, case: Case, question_id: str, answer: str) -> Dict[str, Any]:
        if question_id != QUESTION_ID:
            raise ValueError("Unsupported question_id")

        allowed = {item["value"] for item in OPTIONS}
        if answer not in allowed:
            raise ValueError("Answer must be one of the bounded Skin question options")

        state = self._decode_case_state(case)
        gap_id = f"{case.case_id}:{QUESTION_ID}"
        gap = {
            "gap_id": gap_id,
            "factor": FACTOR_KEY,
            "status": "RESOLVED",
            "resolution": "CURRENT_CASE_ANSWER",
            "question_id": QUESTION_ID,
        }
        state["gaps"] = [
            item for item in state["gaps"]
            if item.get("gap_id") != gap_id
        ] + [gap]

        answer_record = {
            "question_id": QUESTION_ID,
            "factor": FACTOR_KEY,
            "value": answer,
            "source": "CURRENT_CASE_CONSULTATION",
            "value_state": "KNOWN",
        }
        state["answers"] = [
            item for item in state["answers"]
            if item.get("question_id") != QUESTION_ID
        ] + [answer_record]

        self._save_state(case, state)
        return {
            "case_id": case.case_id,
            "question_id": QUESTION_ID,
            "factor": FACTOR_KEY,
            "answer": answer,
            "value_state": "KNOWN",
            "source": "CURRENT_CASE_CONSULTATION",
            "evidence_gap": gap,
        }

    @classmethod
    def current_input_from_case(cls, case: Case) -> Dict[str, Any]:
        state = cls._decode_case_state(case)
        answers = [
            item for item in state.get("answers", [])
            if item.get("question_id") == QUESTION_ID
        ]
        if not answers:
            return {}
        latest = answers[-1]
        return {FACTOR_KEY: latest.get("value")}
