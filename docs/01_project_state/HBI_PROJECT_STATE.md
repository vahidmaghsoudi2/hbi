# HBI Project State
Last Updated: 2026-08-23
Current Phase: **READY FOR PO PILOT DECISION** (ops package complete)

## Tiers
| Tier | Status |
|---|---|
| Phase-1 Pilot Ready | YES (pending PO “PILOT START”) |
| Production Ready | NO — Version Next / POD-001 |
| Version Next backlog | OTP, unfreeze A–D, REGULATORY, UI, perf |

## Operational locks
| Item | Status |
|---|---|
| Products A–D + seed_products.json | **FROZEN** |
| EVIDENCE_MISSING hard-gate | **ACTIVE** |
| Grok2 | Backend / Recommendation Executor |
| Grok1 | Knowledge / Data / QA / Ops docs |

## SoT
- Ops / Pilot decision: `docs/09_gate_reports/HBI_FINAL_OPERATIONS_READINESS.md`
- QA package: `docs/09_gate_reports/HBI_PILOT_READINESS_QA_PACKAGE.md`
- Registry: `08-Meeting-Room/WORK-REGISTRY.md`

## Architecture
Customer → Case → Evidence/Knowledge → Reasoning → Recommendation → Product/Inventory → Outcome
