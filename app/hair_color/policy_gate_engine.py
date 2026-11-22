"""Fail-closed consultation policy gate for Hair Color.

This runtime module performs intake routing only. It does not recommend shades,
formulas, products, chemical processes, processing parameters, or outcomes.
Without a specialist-approved knowledge bundle, it never emits candidates.
"""
from __future__ import annotations

from typing import Any, Mapping


class PolicyGateEngine:
    """Deterministic intake gate; conservative defaults prevent unsupported advice."""

    def __call__(self, request: dict[str, Any]) -> dict[str, Any]:
        case = request["case_context"]
        policy = request["policy_context"]
        evidence = request["evidence_context"]
        supplied_refs = [
            item["evidence_ref"]
            for item in evidence
            if isinstance(item, Mapping) and isinstance(item.get("evidence_ref"), str)
        ]

        base = {
            "request_id": request["request_id"],
            "case_ref": request["case_ref"],
            "evaluated_case_version": request["case_version"],
            "evaluated_target_version": request["target_version"],
            "engine_state": "STOP_OR_REFER_WITH_REASON",
            "consultation_status": "NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW",
            "reason_codes": ["KNOWLEDGE_GAP"],
            "summary": (
                "No specialist-approved knowledge bundle is available for this case. "
                "The system cannot provide a reliable color recommendation."
            ),
            "options": [],
            "missing_information": [],
            "evidence_refs": [],
            "limitations": [
                "Intake and routing only; no specialist-validated color advice.",
                "No chemical instructions, formulas, processing parameters, product equivalence, or outcome guarantees.",
            ],
            "next_step": {
                "action": "SPECIALIST_REVIEW",
                "reason": "No approved domain knowledge is available to support a recommendation.",
            },
        }

        safety = policy.get("safety_concern")
        if safety is True:
            base.update(
                consultation_status="SAFETY_STOP_NO_EXECUTION_SUGGESTION",
                reason_codes=["SAFETY_CONCERN"],
                summary="A safety concern was reported. Stop the recommendation path and seek qualified review.",
                next_step={"action": "STOP_AND_REFER", "reason": "Reported safety concern."},
            )
            return base

        if policy.get("out_of_scope") is True:
            base.update(
                consultation_status="OUT_OF_V1_SCOPE",
                reason_codes=["OUT_OF_SCOPE"],
                summary="This request is outside the supported consultation scope.",
                next_step={"action": "REFER", "reason": "Out-of-scope request."},
            )
            return base

        if policy.get("stale_snapshot") is True:
            base.update(
                reason_codes=["STALE_CASE_VERSION"],
                summary="The case snapshot is stale. A fresh evaluation is required.",
                next_step={"action": "FRESH_EVALUATION", "reason": "Case or target version changed."},
            )
            return base

        missing = case.get("missing_fields", [])
        conflicting = case.get("conflicting_fields", [])
        if isinstance(missing, list) and missing:
            base.update(
                engine_state="NEEDS_MORE_INFORMATION",
                consultation_status="NEEDS_INFORMATION_OR_TEST",
                reason_codes=["DATA_GAP"],
                summary="Required intake information is missing. No recommendation is issued.",
                missing_information=[
                    {"field": field, "reason": "Required intake field not supplied."}
                    for field in missing if isinstance(field, str) and field.strip()
                ],
                next_step={"action": "ASK_FOR_INFORMATION", "fields": missing},
            )
            return base

        if isinstance(conflicting, list) and conflicting:
            base.update(
                engine_state="NEEDS_MORE_INFORMATION",
                consultation_status="NEEDS_INFORMATION_OR_TEST",
                reason_codes=["CONFLICTING_DATA"],
                summary="The intake contains conflicting information. It must be clarified before proceeding.",
                missing_information=[
                    {"field": field, "reason": "Conflicting intake data needs clarification."}
                    for field in conflicting if isinstance(field, str) and field.strip()
                ],
                next_step={"action": "CLARIFY_CONFLICTS", "fields": conflicting},
            )
            return base

        if request["operation"] == "ANSWER_QUESTION":
            base.update(
                summary="The system cannot reliably answer this question from approved evidence. Specialist review is required.",
                next_step={"action": "SPECIALIST_REVIEW", "reason": "Question is not supported by approved evidence."},
            )
            return base

        # Even complete intake is not sufficient to unlock domain advice.
        base["summary"] = (
            "Intake is complete, but a specialist-approved knowledge and evidence bundle "
            "is not available. No color recommendation is issued."
        )
        base["next_step"] = {
            "action": "SPECIALIST_REVIEW",
            "reason": "Domain knowledge validation and evidence approval are outstanding.",
        }
        return base
