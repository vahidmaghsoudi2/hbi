# HBI MANIFEST
> Derived Read-Only Snapshot - NOT a Source of Truth
> Source of Truth: E:/HBI repository and its real artifacts
> Architecture Override > Derived Status

## META
| Key | Value |
|---|---|
| manifest_version | v0.3.1 |
| generated_at | 2026-08-13 18:40:05 |
| generated_by | hbi_manifest_generator.py (AUTO) |
| source_root | E:/HBI |
| schema_lock | v1.1 |
| manifest_type | DERIVED_READONLY_SNAPSHOT |
| overrides_file_exists | True |

## PROJECT_STATUS
current_phase: Phase 7 - Reality Check Preparation
overall_status: NOT_VERIFIED

## MISSIONS
> Evidence-Based only. No invention from Memory.

| Mission ID | Status | Evidence/Reason |
|---|---|---|
| NONE | NOT_VERIFIED | No Mission Artifact files found in Repository |

## ARCHITECTURE_GATES
> Architecture Override > Derived Status

| Gate | Layer | Status | Overridden | Conflict | Source |
|---|---|---|---|---|---|
| GATE 5 | Schema Lock v1.1 | LOCKED_APPROVED | NO | NO | README.md; docs/01_project_state/HBI_Handover.txt; docs/01_project_state/HBI_PROJECT_STATE.md; docs/09_gate_reports/GATE_STATUS_INDEX.md |
| GATE 6-1 | Models | NOT_VERIFIED | YES | NO | ARCHITECTURE_OVERRIDES.md |
| GATE 6-2 | Repositories | CONFLICT | NO | YES | README.md; docs/01_project_state/HBI_PROJECT_STATE.md; docs/09_gate_reports/GATE_STATUS_INDEX.md |
| GATE 6-3 | Services | CONFLICT | NO | YES | README.md; docs/01_project_state/HBI_PROJECT_STATE.md; docs/09_gate_reports/GATE_STATUS_INDEX.md |
| GATE 6-4A | Interface Contract | CONDITIONALLY_APPROVED | NO | NO | docs/01_project_state/HBI_PROJECT_STATE.md |
| GATE 6-4B | Interface Implementation | READY_FOR_REVIEW | NO | NO | docs/01_project_state/HBI_PROJECT_STATE.md |

## BLOCKING_ISSUES
> Extracted from real Artifact text. No invention.

| ID | Description | Severity | Source |
|---|---|---|---|
| BI-003 | Products C & D UNIDENTIFIED - awaiting PO physical info | HIGH | HBI_Handover.txt |
| BI-004 | Products A & B (ISDIN) VERIFIED but awaiting Evidence | HIGH | HBI_Handover.txt |
| BI-006 | GATE 6-1 NOT APPROVED in Handover - Override applied: NOT_VERIFIED | HIGH | HBI_Handover.txt |

## ARTIFACTS_INVENTORY
| Directory | File Count | Sample |
|---|---|---|
| app/ | 34 | app/__init__.py, app/interface/__init__.py, app/interface/cli.py |
| tests/ | 3 | tests/test_interface.py, tests/test_manifest_generator.py, tests/test_repositories.py |
| scripts/ | 7 | scripts/create_hbi_interface.py, scripts/create_hbi_models.py, scripts/create_hbi_repositories.py |
| docs/ | 16 | docs/01_project_state/ARCHITECTURE_OVERRIDES.md, docs/01_project_state/HBI_Handover.txt, docs/01_project_state/HBI_PROJECT_STATE.md |

## EVIDENCE_STATUS
> Extracted from real Artifact text.

| Product | Identity | Evidence | Source |
|---|---|---|---|
| Products A & B (ISDIN) | VERIFIED | AWAITING_EVIDENCE | Parsed from Handover |
| Products C & D | UNIDENTIFIED | BLOCKED | Parsed from Handover |

## UNKNOWN_REGISTRY
| Item | Status | Reason |
|---|---|---|
| GATE 6-1 (Models) | NOT_VERIFIED | Architecture Override applied |
| GATE 6-2 (Repositories) | CONFLICT | Insufficient/contradictory evidence |
| GATE 6-3 (Services) | CONFLICT | Insufficient/contradictory evidence |

## END OF MANIFEST
> DERIVED snapshot. Do NOT edit manually.
> Source of Truth = actual repository files.