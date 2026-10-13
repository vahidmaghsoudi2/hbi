"""Canonical claim-type vocabulary for the Skin Product Intake evidence contract.

Keep this vocabulary separate from reasoning-engine promotion labels. Claim types
describe the epistemic status of an evidence row, not its recommendation score.
"""

CLAIM_TYPES = frozenset({
    "FACT",
    "MANUFACTURER_CLAIM",
    "EVIDENCE",
    "INFERENCE",
    "UNKNOWN",
    "CONFLICT",
})
