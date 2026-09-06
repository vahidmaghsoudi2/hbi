# Governance_INDEX.md

This is the canonical index for HBI governance, documentation, and evidence. It maps important files and directories to their purpose and owner.

## Canonical documents (preserve these)
- HBI_MANIFEST.md — Project manifest and high-level structure. (root)
- HBI_Handover.txt — Project handover and historical notes. (root)
- HBI_TEAM_RESPONSIBILITIES.md — Team responsibilities and roles. (root)
- docs00_criticalPROJECT_MEMORY.md — Project critical memory and decisions. (root)
- .obsidian/ — Obsidian vault used by project (preserve internal links).

## Core project control (mandatory)
- `docs/01_project_control/PROJECT_RULES.md` — Project-wide mandatory rules (NO ASSUMPTION, Reality Audit, Evidence, ONE OWNER, Frozen/Accepted, etc.).
- `docs/01_project_control/HBI_INDEPENDENT_OUTPUT_VERIFICATION_POLICY.md` — **Independent Output Verification & Trust Control** (DONE ≠ VERIFIED ≠ ACCEPTED ≠ MERGED; Independent Verifier; risk-based verification; operational trust). Complements PROJECT_RULES; does not replace them.
- `docs/01_project_state/MISSION_OWNERSHIP_POLICY.md` — End-to-end mission ownership.
- `docs/P4_PRODUCT_INTAKE_GOVERNANCE_CONTRACT_V1.md` — P4 Product Intake & Governance Contract.
- `docs/P4_IMPLEMENTATION_GUIDE.md` — P4 implementation guidance.

## Governance and Gates
- 02-Gates/ — Gate definitions and verification scripts.
- verify_gate61.py, gate61_report.txt — existing gate verification artifacts.

## Evidence
- 07-Evidence/ — Canonical storage for artifacts and evidence produced by CI and Agents.
- .github/workflows/* — Workflows that generate or upload evidence artifacts.

## Meeting & Decisions
- 08-Meeting-Room/ — Meeting notes and decision records.

## Engineering
- app/ — Application source code.
- tests/ — Test suite (ensure tests are present and meaningful).
- requirements*.txt, pytest.ini — CI requirements and test config.

## Agent-related
- agent-jobs/ — scripts for agent jobs (review before reuse).
- hbi-agent-runner.ps1 — agent runner script (preserve and review before change).

## Next steps (guidance)
1. Do not duplicate canonical documents — update them in-place and reference them from this index.
2. Preserve .obsidian and ensure any renames update internal links.
3. Use AGENTS.md for agent policy; do not bypass it.
4. Independent Verification of work-product claims is governed by `HBI_INDEPENDENT_OUTPUT_VERIFICATION_POLICY.md` (IOV-001).

