"""Test-only synthetic hair-colour engine for Adapter integration tests.

This module is deliberately under tests/: it is not part of the application
runtime and contains no hair-colour chemistry or product recommendation logic.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


SCENARIO_IDS = tuple(f"S{i:02d}" for i in range(1, 16))


class SyntheticHairColorEngine:
    """Deterministic fixture engine selected only by a test scenario ID."""

    def __call__(self, request: dict[str, Any]) -> dict[str, Any]:
        case_context = request["case_context"]
        scenario_id = case_context.get("synthetic_scenario_id")
        if scenario_id not in SCENARIO_IDS:
            raise ValueError("unknown synthetic_scenario_id")

        if scenario_id == "S15":
            raise TimeoutError("synthetic engine failure")

        evidence_refs = [
            item["evidence_ref"]
            for item in request["evidence_context"]
            if isinstance(item, Mapping) and isinstance(item.get("evidence_ref"), str)
        ]

        result = {
            "request_id": request["request_id"],
            "case_ref": request["case_ref"],
            "evaluated_case_version": request["case_version"],
            "evaluated_target_version": request["target_version"],
            "engine_state": "SUGGESTION_REVIEWABLE",
            "consultation_status": "SYSTEM_REASONED_SUGGESTION",
            "reason_codes": [],
            "summary": f"Synthetic fixture {scenario_id}; not a product recommendation.",
            "options": [{}],
            "missing_information": [],
            "evidence_refs": evidence_refs[:1],
            "limitations": ["Synthetic-only test output; no scientific evidence."],
            "next_step": {},
        }

        blocked = {
            "S02": ("DATA_GAP", "NEEDS_MORE_INFORMATION", "NEEDS_INFORMATION_OR_TEST"),
            "S03": ("CONFLICTING_DATA", "NEEDS_MORE_INFORMATION", "NEEDS_INFORMATION_OR_TEST"),
            "S04": ("DATA_GAP", "NEEDS_MORE_INFORMATION", "NEEDS_INFORMATION_OR_TEST"),
            "S05": ("DATA_GAP", "NEEDS_MORE_INFORMATION", "NEEDS_INFORMATION_OR_TEST"),
            "S06": ("KNOWLEDGE_GAP", "NEEDS_MORE_INFORMATION", "NEEDS_INFORMATION_OR_TEST"),
            "S07": ("SAFETY_CONCERN", "STOP_OR_REFER_WITH_REASON", "SAFETY_STOP_NO_EXECUTION_SUGGESTION"),
        }
        if scenario_id in blocked:
            reason, engine_state, consultation_status = blocked[scenario_id]
            result.update(
                reason_codes=[reason],
                engine_state=engine_state,
                consultation_status=consultation_status,
                options=[],
            )

        if scenario_id == "S08":
            result.update(
                engine_state="STOP_OR_REFER_WITH_REASON",
                consultation_status="NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW",
                options=[],
            )
        elif scenario_id == "S09":
            result["options"] = [{}, {}]
        elif scenario_id in {"S11", "S12", "S14"}:
            result["options"] = []
        elif scenario_id == "S13":
            result["summary"] = "Fresh synthetic evaluation for the supplied case and target versions."

        if scenario_id == "S11":
            result["summary"] = "Question answered; no client decision is made by the adapter or engine."
        elif scenario_id == "S12":
            result["summary"] = "Rejection and suggestion-ledger ownership remain outside the adapter."
        elif scenario_id == "S14":
            result["summary"] = "Fresh reevaluation fixture only; no resume or workflow transition is performed."

        return deepcopy(result)
