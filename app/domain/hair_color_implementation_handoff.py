"""Implementation handoff stage registry; readiness remains gated."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class HandoffStage:
    stage_id: str
    title: str
    dependencies: tuple[str,...]
    status: str

STAGES=(
    HandoffStage("H0","PO gate and baseline",(),"pending_PO_decision"),
    HandoffStage("H1","Domain/catalog foundation",("H0",),"not_started"),
    HandoffStage("H2","Consultation engine controls",("H1",),"not_started"),
    HandoffStage("H3","Evidence and specialist review",("H2",),"pending_external_review"),
    HandoffStage("H4","API/persistence/UI integration",("H1","H2","H3"),"not_started"),
    HandoffStage("H5","Verification",("H1","H2","H3","H4"),"not_started"),
    HandoffStage("H6","PO release decision",("H5",),"pending_PO_decision"),
)

def handoff_stages()->tuple[HandoffStage,...]:
    return STAGES

def implementation_authorized()->bool:
    return False
