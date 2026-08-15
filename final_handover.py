"""final_handover.py - Update Handover + create Phase 2 Kickoff Summary"""
import subprocess
from pathlib import Path
from datetime import datetime

P = Path("E:/HBI")
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Get current git log
r = subprocess.run(["git", "log", "--oneline", "-15"],
                   capture_output=True, text=True, cwd=str(P))
git_log = r.stdout

print("=" * 60)
print("STEP 1: Update HBI_Handover.txt")
print("=" * 60)

handover = P / "HBI_Handover.txt"
content = """HBI PROJECT HANDOVER
Project: Maqsoudi HBI — Phase 1 COMPLETE / Phase 2 KICKOFF
Owner: Engineer Maqsoudi
Last Update: """ + now + """
Updated by: Qwen (Data QA / Project Manager)

═══════════════════════════════════════════════════════
STATUS (VERIFIED)
═══════════════════════════════════════════════════════
✅ GATE 5 (Schema Lock v1.1): LOCKED & APPROVED
✅ GATE 6-1 (Models): APPROVED (verified 2026-08-17)
   • NameError: FIXED
   • Customer.name default='': FIXED (server_default + default)
   • CHECK constraints: 9 tables (per Schema v1.1)
   • PRAGMA foreign_keys=ON: ENABLED
✅ Products A & B (ISDIN): VERIFIED
   • Product A: ISDIN-FUSION-WATER-MAGIC-50 (Evidence: 4 claims)
   • Product B: ISDIN-FOTOULTRA-ACTIVE-UNIFY-COLOR-50 (Evidence: 6 claims)
✅ Test Suite: 48/48 PASS
✅ E2E on Real DB: 6/6 PASS, count=2 recommendations
✅ AD-3 Contract: 16 fields mapped in RecommendationDTO
✅ Scoring Engine: Real (AD-1, AD-2, AD-4)
✅ Git Status: CLEAN

═══════════════════════════════════════════════════════
PHASE 1: OFFICIALLY CLOSED (2026-08-16)
═══════════════════════════════════════════════════════
Closure Certificate: docs/09_gate_reports/PHASE1_CLOSURE_CERTIFICATE.md

═══════════════════════════════════════════════════════
DEFERRED TO NEXT VERSION (PO DECISION)
═══════════════════════════════════════════════════════
⏳ Products C & D: UNIDENTIFIED (awaiting PO physical info)
⏳ barcode_gtin for A & B: awaiting PO physical info
⏳ Independent Evidence (REGULATORY): Perplexity mission closed, no source found

═══════════════════════════════════════════════════════
PHASE 2: PENDING KICKOFF
═══════════════════════════════════════════════════════
Goals (approved by PO):
1. REST API Layer (FastAPI + JWT)
2. API Design (ChatGPT) → Implementation (DeepSeek) → Security (Grok)

Timeline:
- ChatGPT API Design: 72 hours (not yet started)
- DeepSeek Implementation: 7 days (after design)
- Grok Security Review: 7 days (after implementation)
- DeepSeek Fix Findings: 3 days
- Qwen Validation: 1 day

Prerequisites for Phase 2:
- FastAPI, uvicorn, python-jose, passlib, pydantic (NOT YET INSTALLED)
- tests/conftest.py shared fixtures (NOT YET CREATED)
- requirements.txt committed (NOT YET CREATED)

═══════════════════════════════════════════════════════
TEAM STATUS
═══════════════════════════════════════════════════════
- Qwen (Data QA / PM): ACTIVE — Project oversight
- Perplexity (Evidence): STANDBY — Mission closed
- ChatGPT (Integration Architect): AWAITING mission
- DeepSeek (Backend): AWAITING mission
- Grok (Red Team): AWAITING mission

═══════════════════════════════════════════════════════
QA FRAMEWORKS (LOCKED v0.1)
═══════════════════════════════════════════════════════
See: frameworks.txt
1. Validation Contract v0.1
2. QA Checklist v0.1 (5 phases, 32 checks)
3. Evidence Ledger Template v0.1
4. Claim Boundary Rules v0.1 (6 rules)
5. Unknown/Conflict Protocol v0.1

═══════════════════════════════════════════════════════
RECENT GIT HISTORY
═══════════════════════════════════════════════════════
""" + git_log + """

═══════════════════════════════════════════════════════
CRITICAL FILES (DO NOT DELETE)
═══════════════════════════════════════════════════════
- data/hbi.db (SQLite database)
- app/ (Backend: models, services, facades, repositories)
- tests/ (48 unit tests + E2E)
- docs/ (reports, architecture, closure docs)
- frameworks.txt (5 QA frameworks)
- HBI_Handover.txt (this file)

═══════════════════════════════════════════════════════
RECOVERY PROCEDURE
═══════════════════════════════════════════════════════
If context is lost, read in order:
1. This file (HBI_Handover.txt)
2. frameworks.txt
3. docs/09_gate_reports/PHASE1_CLOSURE_CERTIFICATE.md
4. git log
"""

handover.write_text(content, encoding="utf-8")
print("[OK] HBI_Handover.txt updated with current status")

print()
print("=" * 60)
print("STEP 2: Create Phase 2 Kickoff Summary")
print("=" * 60)

summary = P / "docs" / "00_critical" / "PHASE2_KICKOFF.md"
summary.parent.mkdir(parents=True, exist_ok=True)

kickoff = """# PHASE 2 KICKOFF — HANDOVER TO NEW CHAT

**Date:** """ + now + """
**Purpose:** Paste this into the new chat as the first message.

---

## Context for New Chat

I am Engineer Maqsoudi, PO of the HBI (Health & Beauty Intelligence) project.
Phase 1 is COMPLETE. Phase 2 is ready to start.

### Project Location
- Windows local: `E:\\HBI`
- Database: `data/hbi.db` (SQLite)
- Schema: v1.1 LOCKED

### Current Status
- ✅ 48/48 unit tests PASS
- ✅ E2E on real DB: 6/6 PASS
- ✅ GATE 6-1 (Models): APPROVED
- ✅ Products A & B: VERIFIED with 10 Evidence claims total
- ✅ AD-3 Contract: 16 fields mapped

### Team Members
- **Qwen**: Project Manager / Data QA (this chat partner)
- **ChatGPT**: Integration Architect (API Design)
- **DeepSeek**: Backend Engineer (API Implementation)
- **Grok**: Red Team (Security Review)
- **Perplexity**: Evidence Analyst (standby)

### Reference Documents
- `frameworks.txt` — 5 QA frameworks (LOCKED)
- `HBI_Handover.txt` — Full project handover

---

## Phase 2 Mission Brief (Already Drafted)

### Mission 1: ChatGPT — API Design (72 hours)
- Deliver: OpenAPI spec, API Design Doc, Security Doc
- Location: `docs/02_architecture/`
- Constraints: Use existing Facade layer, respect AD-3 Contract

### Mission 2: DeepSeek — API Implementation (7 days, after ChatGPT)
- Stack: FastAPI + JWT + Pydantic
- Structure: `app/api/` with routers
- Tests: Happy path, 400/401/403/404/409 cases
- Mocking: Facade layer must be mocked

### Mission 3: Grok — Security Review (7 days, after DeepSeek)
- Areas: OWASP Top 10, JWT, Input validation, Consent enforcement
- Deliver: `API_SECURITY_REVIEW_v0.1.md`

### Mission 4: DeepSeek — Fix Security Findings (3 days)

---

## Prerequisites (NOT YET DONE)

1. Install dependencies: