"""Change-invalidation test scenarios; exercise version/dependency behavior."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ChangeScenario:
    scenario_id: str
    changed_input: str
    expected_policy: str

SCENARIOS=(
    ChangeScenario("CH01","target_color","full_invalidation_fresh_evaluation"),
    ChangeScenario("CH02","current_base","current_base_dependents_only"),
    ChangeScenario("CH03","service_history","history_safety_and_downstream"),
    ChangeScenario("CH04","product_evidence","product_dependent_outputs"),
    ChangeScenario("CH05","safety_screen","safety_and_downstream"),
    ChangeScenario("CH06","current_base+product_identity","union_of_dependencies"),
    ChangeScenario("CH07","unknown_input","full_fail_closed_invalidation"),
    ChangeScenario("CH08","decision_record","acceptance_consent_review_reset"),
    ChangeScenario("CH09","same_version","reject_change"),
    ChangeScenario("CH10","unrelated_output","preserve_unaffected"),
)

def change_scenarios()->tuple[ChangeScenario,...]:
    return SCENARIOS
