import shutil
from pathlib import Path

PROJECT = Path("E:/HBI")
TODAY = "1405-05-22 (2026-08-13)"

print("=" * 60)
print("HBI REPOSITORY MEMORY SETUP (SAFE VERSION)")
print("=" * 60)

# ---------- 1) Folder structure ----------
FOLDERS = [
    "docs/01_project_state",
    "docs/02_architecture",
    "docs/03_decision_log",
    "docs/04_frameworks",
    "docs/05_knowledge_base/products",
    "docs/06_artifacts_index",
    "docs/07_evidence/products_a_b_isdin",
    "docs/07_evidence/products_c_d",
    "docs/08_ai_review_reports/deepseek",
    "docs/08_ai_review_reports/grok",
    "docs/08_ai_review_reports/perplexity",
    "docs/08_ai_review_reports/chatgpt",
    "docs/08_ai_review_reports/qwen",
    "docs/09_gate_reports",
    "docs/10_archive/FILE_DISPOSAL_RECORDS",
    "scripts",
]
for f in FOLDERS:
    p = PROJECT / f
    p.mkdir(parents=True, exist_ok=True)
    print("[DIR] " + str(p))

# ---------- 2) Core memory files ----------
FILES = {}

FILES["README.md"] = """# HBI - Maqsoudi Gallery
Central memory repository and Source of Truth for HBI project.

Last Updated: <<TODAY>>

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
"""

FILES[".gitignore"] = """# --- HBI Project .gitignore ---

# Database (runtime artifact)
data/*.db
data/*.sqlite
data/*.sqlite3

# Python bytecode
__pycache__/
*.py[cod]
*$py.class
*.so

# Virtual environments
env/
venv/
.venv/

# pytest cache
.pytest_cache/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Logs
*.log
"""

FILES["docs/01_project_state/HBI_PROJECT_STATE.md"] = """# HBI Project State
Last Updated: <<TODAY>>
Current Phase: Phase 7 - Reality Check Preparation

## Gate Status
| Gate | Status | Notes |
|---|---|---|
| GATE 5 - Schema Lock v1.1 | LOCKED and APPROVED | Change only via Change Request |
| GATE 6-1 - Models | APPROVED | 9 core models |
| GATE 6-2 - Repositories | APPROVED | Evidence/ProductKnowledge Repos missing |
| GATE 6-3 - Services | APPROVED | Evidence/ProductKnowledge Services missing |
| GATE 6-4A - Interface Contract | CONDITIONALLY APPROVED | |
| GATE 6-4B - Interface Implementation | READY FOR REVIEW | Awaiting final Independent Review |

## Architecture Skeleton
Customer -> Case -> Evidence/Knowledge -> Reasoning -> Recommendation -> Product/Inventory -> Outcome

## Known Gaps (truly missing)
- EvidenceRepository / EvidenceService
- ProductKnowledgeRepository / ProductKnowledgeService
- Real Reasoning Engine (currently _calculate_match_score returns fixed 0.75)
- Consent management (update_consent, withdraw_consent)

## Next Step
After Reality Check, build the real HBI Reasoning Core to transform the system
from a simple CRM into a Decision Support System.
"""

FILES["docs/02_architecture/HBI_ARCHITECTURE.md"] = """# HBI Architecture
Last Updated: <<TODAY>>

## Backend Layers
| Layer | Path | Gate | Status |
|---|---|---|---|
| Models | app/models/ | 6-1 | APPROVED |
| Repositories | app/repositories/ | 6-2 | APPROVED |
| Services | app/services/ | 6-3 | APPROVED |
| Interface (Facade/DTO/CLI) | app/interface/ | 6-4 | READY FOR REVIEW |

## Data Flow (Decision Support Flow)
Customer -> Case -> Evidence/Knowledge -> Reasoning -> Recommendation -> Product/Inventory -> Outcome

## Architecture Constraints
- Schema v1.1 is LOCKED (change only via Change Request)
- Facades are Use-Case-Oriented, not CRUD-Oriented
- Interface has NO direct access to Repository/Model/Database
"""

FILES["docs/02_architecture/HBI_DECISION_FLOW.md"] = """# HBI Decision Flow
Last Updated: <<TODAY>>

This document records the HBI decision flow from customer intake to recommendation output.

WARNING: This is a TEMPLATE. The Reasoning Engine details are not yet implemented.

## Steps
1. Customer Intake - register customer with Consent
2. Case Creation - open a need case
3. Evidence Gathering - collect evidence (NOT YET IMPLEMENTED)
4. Reasoning - match need to product knowledge (NOT YET IMPLEMENTED)
5. Recommendation - generate scored recommendation (currently Skeleton)
6. Outcome / Learning - record outcome for future learning (NOT YET IMPLEMENTED)
"""

FILES["docs/03_decision_log/DECISION_LOG_INDEX.md"] = """# Decision Log Index
Last Updated: <<TODAY>>

Every major project decision is recorded as an ADR (Architecture Decision Record).

| ADR | Subject | Status | Date |
|---|---|---|---|
| ADR-001 | Use quoted table name Case due to reserved keyword | ACCEPTED | 1405-05-21 |
| ADR-002 | Do not implement Evidence/ProductKnowledge in GATE 6-4B | ACCEPTED | 1405-05-21 |
| ADR-003 | Use GitHub as Source of Truth for project memory | PROPOSED | <<TODAY>> |

To add a new decision, create a file named ADR-XXX-short-title.md in this folder
and add a row to the table above.
"""

FILES["docs/05_knowledge_base/KB_INDEX.md"] = """# Knowledge Base Index
Last Updated: <<TODAY>>

This folder holds product and domain knowledge for HBI.

## Structure
- products/ - knowledge for each product (ingredients, use cases, evidence)

## Product Status
| Product | Identity Status | Gate |
|---|---|---|
| Products A and B (ISDIN) | VERIFIED | Awaiting Evidence |
| Products C and D | UNIDENTIFIED | Awaiting PO physical info |
"""

FILES["docs/06_artifacts_index/ARTIFACTS_INDEX.md"] = """# HBI Artifacts Index
Last Updated: <<TODAY>>

Mapping between documentation and actual Backend code.

| Artifact | Code Path | Gate | Status |
|---|---|---|---|
| Models | app/models/ | 6-1 | APPROVED |
| Repositories | app/repositories/ | 6-2 | APPROVED |
| Services | app/services/ | 6-3 | APPROVED |
| Interface / Contracts | app/interface/ | 6-4 | READY FOR REVIEW |

## Gaps
| Artifact | Status |
|---|---|
| EvidenceRepository | MISSING |
| ProductKnowledgeRepository | MISSING |
| EvidenceService | MISSING |
| ProductKnowledgeService | MISSING |
"""

FILES["docs/07_evidence/EVIDENCE_INDEX.md"] = """# Evidence Index
Last Updated: <<TODAY>>

Product evidence is maintained per Framework 3 (Evidence Ledger).

## Structure
- products_a_b_isdin/ - evidence for VERIFIED products
- products_c_d/ - awaiting identity information

## Status
WARNING: No evidence has been registered yet.
This section becomes active once EvidenceService is decided and implemented.
"""

FILES["docs/09_gate_reports/GATE_STATUS_INDEX.md"] = """# Gate Reports Index
Last Updated: <<TODAY>>

| Gate | Report File | Status |
|---|---|---|
| GATE 5 - Schema Lock | GATE_5_SCHEMA_LOCK.md | LOCKED and APPROVED |
| GATE 6-1 - Models | GATE_6-1_MODELS.md | APPROVED |
| GATE 6-2 - Repositories | GATE_6-2_REPOSITORIES.md | APPROVED |
| GATE 6-3 - Services | GATE_6-3_SERVICES.md | APPROVED |
| GATE 6-4 - Interface | GATE_6-4_INTERFACE.md | READY FOR REVIEW |
| GATE 7 - Reality Check | GATE_7_REALITY_CHECK.md | PENDING |

Each Gate report must be saved in this folder as a separate Markdown file.
"""

FILES["docs/10_archive/README.md"] = """# Archive
Obsolete but traceable files are kept in this folder.

WARNING: No file is removed from this folder without Product Owner approval
and a recorded Disposal Record.
"""

# ---------- 3) Write files (only if missing) ----------
for rel, content in FILES.items():
    content = content.replace("<<TODAY>>", TODAY)
    p = PROJECT / rel
    if p.exists():
        print("[SKIP] already exists: " + rel)
    else:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        print("[FILE] created: " + rel)

# ---------- 4) Move generator scripts to scripts/ ----------
GENERATORS = [
    "create_hbi_models.py",
    "create_hbi_repositories.py",
    "create_hbi_services.py",
    "create_hbi_interface.py",
    "hbi_check.py",
    "hbi_gate64_preflight.py",
]
for g in GENERATORS:
    src = PROJECT / g
    dst = PROJECT / "scripts" / g
    if src.exists() and not dst.exists():
        shutil.move(str(src), str(dst))
        print("[MOVE] " + g + " -> scripts/")
    elif dst.exists():
        print("[SKIP] already in scripts/: " + g)
    else:
        print("[WARN] not found: " + g)

print("=" * 60)
print("DONE. Structure created. No existing file was deleted.")
print("=" * 60)