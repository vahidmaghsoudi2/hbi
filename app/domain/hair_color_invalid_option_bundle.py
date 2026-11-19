"""Cross-module guard for invalid/conflicting option bundles."""
from __future__ import annotations
from dataclasses import dataclass
from app.domain.hair_color_option_selection import EvaluatedOption, select_reviewable_options
from app.domain.hair_color_four_motor_states import DecisionSignals, MotorState, decide_motor_state

@dataclass(frozen=True)
class OptionBundleResult:
    status: str
    options: tuple[EvaluatedOption,...]
    excluded: tuple[tuple[str,str],...]
    motor_state: str
    message: str

def validate_option_bundle(candidates: object,signals: object)->OptionBundleResult:
    if not isinstance(signals,DecisionSignals):
        return OptionBundleResult("invalid_gate",(),(),"stop_or_referral","Decision gate invalid; suppress options.")
    decision=decide_motor_state(signals)
    if decision.state!=MotorState.SUGGESTION_REVIEWABLE:
        status="blocked_by_gate" if decision.state!=MotorState.STOP_OR_REFERRAL else "stopped"
        return OptionBundleResult(status,(),(),decision.state.value,
            "Options suppressed by decision gate; resolve required data/conditions or stop/referral first.")
    selection=select_reviewable_options(candidates)
    if selection.status!="options_ready_for_review":
        return OptionBundleResult(selection.status,(),selection.excluded,decision.state.value,
            "Invalid, conflicting, unvalidated, or evidence-incomplete options are not presented.")
    return OptionBundleResult("options_ready_for_review",selection.selected,selection.excluded,decision.state.value,
        "Only evidence-backed validated options are shown for review; no execution consent implied.")
