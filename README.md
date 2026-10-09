# HBI - Maqsoudi Gallery
Central memory repository and Source of Truth for HBI project.

Last Updated: 1405-05-22 (2026-08-13)

## Repository Structure
| Path | Role |
|---|---|
| app/ | Backend code (Models, Repositories, Services, Interface) |
| tests/ | Interface and Repository tests |
| docs/ | Project memory (documents, evidence, reports) |
| scripts/ | Generators and one-time tools |
| data/ | Runtime database (gitignored) |

## Gate Status
| Gate | Status |
|---|---|
| GATE 5 - Schema Lock v1.1 | LOCKED and APPROVED |
| GATE 6-1 - Models | APPROVED |
| GATE 6-2 - Repositories | APPROVED |
| GATE 6-3 - Services | APPROVED |
| GATE 6-4 - Interface | READY FOR REVIEW |

## Quick Links
- Project State: docs/01_project_state/HBI_PROJECT_STATE.md
- Architecture: docs/02_architecture/HBI_ARCHITECTURE.md
- Decision Log: docs/03_decision_log/DECISION_LOG_INDEX.md
- QA Frameworks: docs/04_frameworks/
- Evidence: docs/07_evidence/
- Gate Reports: docs/09_gate_reports/

---

## Start Here

If you are new to HBI, read these in order:

1. `docs/01_project_control/PROJECT_RULES.md` — mandatory project rules
2. `docs/01_project_state/HBI_PROJECT_STATE.md` — current project state
3. `docs/02_architecture/HBI_ARCHITECTURE.md` — system architecture
4. `docs/03_decision_log/DECISION_LOG_INDEX.md` — key decisions
5. `docs/07_evidence/` — verification evidence
6. `docs/09_gate_reports/` — gate/review reports

For day-to-day work, **GitHub `master` is the source of truth**. Historical reports are evidence of past states and should not be treated as the current state without checking the current Master SHA.

## Verification

HBI has automated GitHub Actions verification. The current CI pipeline runs both the main test suite and governance tests; recent post-merge runs have completed successfully on Master.

The repository currently contains a substantial automated test suite. Test coverage and pass counts should be taken from the CI run for the exact commit being reviewed rather than from a static README claim.

## Repository Hygiene

The `scripts/` directory is intended for generators and one-time operational tools. Before adding another maintenance script, first check whether an existing tool can be extended or reused.

Historical evidence files should remain traceable. A report is moved or archived only after checking repository references so that evidence links are not broken.

The repository currently contains both root-level `fix_customer_name.py` and `fix_customer_name2.py`. Their relationship and usage should be reviewed before either file is removed, merged, or renamed.

## PROJECT RULES — MANDATORY ENTRY GATE

Before performing any project work, every human or AI contributor MUST read:

`docs/01_project_control/PROJECT_RULES.md`

This file is mandatory project policy.

No implementation, architecture change, schema change, API change, documentation change, or data modification may begin before:

1. Reading PROJECT_RULES.md
2. Verifying current origin/master SHA
3. Performing the required Reality Audit
4. Identifying existing / partial / missing / unknown / conflict states
5. Confirming the applicable Unit roadmap and execution package

**GitHub master is the Project Source of Truth.**

Mandatory principles:

- NO ASSUMPTION
- NO INVENTED DATA
- TRACEABILITY / ردپا
- 0→100 OWNERSHIP
- COMPLETE EXECUTION PACKAGE BEFORE START
- SAFE GIT OPERATIONS
- TEST + EVIDENCE BEFORE DONE
- COMPLETE HANDOFF FOR CONTINUITY

Complete rules:

`docs/01_project_control/PROJECT_RULES.md`

