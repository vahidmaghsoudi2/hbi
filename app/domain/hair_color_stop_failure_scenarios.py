"""Ten stop/failure behavioral scenarios, integrated across domain gates."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class StopFailureScenario:
    scenario_id: str
    title: str
    expected_control: str

SCENARIOS=(
    StopFailureScenario("SF01","Safety stop","No execution-oriented recommendation."),
    StopFailureScenario("SF02","Engine failure","Suppress all run output."),
    StopFailureScenario("SF03","Data gap","Request specific required inputs."),
    StopFailureScenario("SF04","Knowledge gap","Do not guess or treat as customer-data gap."),
    StopFailureScenario("SF05","Client stop request","Record only performed steps; no auto-resume."),
    StopFailureScenario("SF06","Restart incomplete","Block restart when any fresh check missing."),
    StopFailureScenario("SF07","Fresh restart","New version and complete fresh checks required."),
    StopFailureScenario("SF08","Safety transition bypass","Safety stop cannot bypass workflow guards."),
    StopFailureScenario("SF09","Conditional output","Condition remains pending; no unqualified options."),
    StopFailureScenario("SF10","Outside scope","Stop/referral; no in-scope recommendation."),
)

def stop_failure_scenarios()->tuple[StopFailureScenario,...]:
    return SCENARIOS
