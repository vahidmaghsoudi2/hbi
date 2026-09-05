# Governance_INDEX.md

This is the canonical index for HBI governance, documentation, and evidence. It maps important files and directories to their purpose and owner.

## Canonical documents (preserve these)
- HBI_MANIFEST.md — Project manifest and high-level structure. (root)
- HBI_Handover.txt — Project handover and historical notes. (root)
- HBI_TEAM_RESPONSIBILITIES.md — Team responsibilities and roles. (root)
- docs00_criticalPROJECT_MEMORY.md — Project critical memory and decisions. (root)
- .obsidian/ — Obsidian vault used by project (preserve internal links).

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

