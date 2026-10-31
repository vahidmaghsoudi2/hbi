# HBI - Maqsoudi Gallery
Central memory repository and Source of Truth for HBI project.

Last Updated: 1405-08-09 (2026-10-31)

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


## Developer Setup (local)

Short onboarding only. This is **not** product acceptance and does **not** replace `docs/01_project_control/PROJECT_RULES.md`.

### Prerequisites
- Python **3.12** (matches GitHub Actions)
- Node.js + npm (frontend)
- Git

### Backend
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
source .venv/bin/activate
pip install -r requirements.txt
# lean CI set (optional): pip install -r requirements-ci.txt
mkdir -p data
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- Default database: `sqlite:///./data/hbi.db` (override with `DATABASE_URL`)
- API docs: http://127.0.0.1:8000/docs

### Frontend
```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

### Tests
```bash
pytest tests/ -q
```

### Windows one-click launcher
- `scripts/start-hbi.bat` or `scripts/start-hbi.ps1`
- Starts backend on `:8000` and frontend on `:5173` after a Git sync check

### Environment notes
| Variable | Role |
|---|---|
| `DATABASE_URL` | DB URL; default `sqlite:///./data/hbi.db` |
| `HBI_ENV` | default `development` |
| `JWT_SECRET_KEY` | required when `HBI_ENV=production` |

Before any product work: read `docs/01_project_control/PROJECT_RULES.md` and verify current `origin/master` SHA.

---

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
