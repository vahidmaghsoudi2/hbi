# HBI Active Session

## Status
- **Last Updated:** 2026-08-20
- **Active Phase:** Technical Improvements (Post Phase-1 Hardening)
- **Previous:** GATE 9 / Phase 1 CLOSED successfully

## Official Kick-off (Qwen + PO) — 2026-08-20
Phase 1 closed successfully. Project now enters **Technical Improvements** phase to bullet-proof the system before production deployment.

### Locked PO Decisions (still in force)
- Products C & D remain **UNIDENTIFIED**
- No identity/evidence action for C/D until further PO instruction

---

## Technical Improvements — Assignments

### 1. DeepSeek (Backend)
- [ ] Fix StarletteDeprecationWarning (httpx related)
- [ ] Write Unit Tests for reasoning modules:
  - `app/reasoning/claim_validator.py`
  - `app/reasoning/reasoning_engine.py`
  - `app/reasoning/conflict_analyzer.py`
- [ ] Raise overall Coverage to **> 80%**

### 2. Perplexity (Evidence Steward / QA)
- [ ] Review new unit tests and confirm they strictly validate Framework 4 & 5 rules with **NO ASSUMPTION**
- [ ] Run final Coverage Report:
  ```bash
  pytest --cov=app --cov-report=term-missing
  ```
- [ ] Confirm threshold > 80% is met

### 3. All Members
- Strict **NO ASSUMPTION** principle
- Any conflict or missing information → Conflict Register + Source of Truth

---

## Current Reasoning Modules
| Module | Path | Test Coverage Status |
|---|---|---|
| claim_validator | app/reasoning/claim_validator.py | Needs dedicated unit tests |
| reasoning_engine | app/reasoning/reasoning_engine.py | Needs dedicated unit tests |
| conflict_analyzer | app/reasoning/conflict_analyzer.py | Needs dedicated unit tests |
| scoring | app/reasoning/scoring.py | Partial (test_scoring_engine.py exists) |

---

## Team Status

| Agent | Role | Current Task |
|---|---|---|
| DeepSeek | Backend | StarletteDeprecationWarning + Unit Tests for reasoning |
| Perplexity | QA / Evidence | Review tests + Final Coverage Report |
| Grok | Red Team / Support | Supporting Technical Improvements |
| Qwen | PM / Data QA | Coordination + receiving final reports |
| PO | Decision Maker | C/D locked UNIDENTIFIED |

---

## For AI Agent (Qwen)
1. Read this file first
2. Enforce NO ASSUMPTION
3. Accept only Artifact-based reports (especially full pytest --cov output)
4. Products C & D stay UNIDENTIFIED
5. Track DeepSeek unit tests + Perplexity coverage confirmation
