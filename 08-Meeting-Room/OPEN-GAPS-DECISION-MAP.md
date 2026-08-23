# OPEN GAPS — DECISION MAP

**Purpose:** Usable map for next HBI decisions. Evidence-only. No Production change.  
**Author:** Grok2  
**HEAD at write:** `1ac0abc6853a35fa2761227520e0ecfef8ae3bcd`  
**Date:** 2026-08-23

---

## 1. Ready packages (need EXECUTE only)

| Gap | Artifact | Risk | Blocker |
|-----|----------|------|---------|
| Dual `get_db` deduplication | `08-Meeting-Room/CHANGE-PACKAGE-DUAL-GET-DB.md` | LOW | Explicit `EXECUTE_APPROVED` + SCOPE required. Package says READY — AWAITING EXECUTE. |
| Behavioral comparison already done | `08-Meeting-Room/TASK-HBI-003-GET-DB-COMPARISON.md` | — | Supports the package above. |

**Action if approved:** One scoped write to `app/core/deps.py` only, then Actions on that SHA, then ChatGPT audit.

---

## 2. Documentation drift (no code change needed)

| Gap | Evidence | Impact |
|-----|----------|--------|
| Handover vs recent product commits | Recent: `7de8edeb…` (register A–D), `a7aeace…` (Handover identity update). Older Handover text still carried historical PARTIAL/PENDING language in prior reads. | Readers may see mixed status if they do not check latest commits. |
| WORK-REGISTRY lag risk | File exists at `08-Meeting-Room/WORK-REGISTRY.md` | May not list newest operational line / product registration commits. |

**Action (docs-only, when ordered):** Sync Handover + Registry to current HEAD claims; do not invent new product facts.

---

## 3. Structural facts (verified by path existence)

| Item | Path / note | Status |
|------|-------------|--------|
| Active line Grok2+ChatGPT | `08-Meeting-Room/ACTIVE-LINE-GROK2-CHATGPT.md` | Registered |
| Execution bridge playbook | `08-Meeting-Room/GROK_EXECUTION_BRIDGE_PLAYBOOK.md` | Present |
| Multi-AI collab protocol | `08-Meeting-Room/HBI_MULTI_AI_COLLAB_PROTOCOL.md` | Present |
| Claim vs Evidence rules | `08-Meeting-Room/HBI_CLAIM_VS_EVIDENCE.md` | Present |
| Dual get_db change package | `08-Meeting-Room/CHANGE-PACKAGE-DUAL-GET-DB.md` | AWAITING EXECUTE |
| `data/` database in repo | Previously 404 on master | Still treat product DB as **not** in GitHub unless a new commit proves otherwise |

---

## 4. Recommended next decisions (for PO / Qwen1 / ChatGPT)

1. **EXECUTE or HOLD** dual-get_db package (only production-adjacent item currently packaged).  
2. **Order docs sync** of Handover + WORK-REGISTRY to HEAD if identity A–D registration is now authoritative.  
3. Do **not** start new Production work without SCOPE + EXECUTE line.

---

## 5. What Grok2 will NOT do without further order

- Write under `app/`  
- Declare final VERIFIED on the dual-get_db change  
- Invent missing Evidence or product fields  
- Expand scope beyond Meeting-Room / TRACE hygiene

```text
HBI HUB — TRACE STATUS
Actor: Grok2
Current Task: OPEN-GAPS decision map
Repository: vahidmaghsoudi2/hbi
Branch: master
HEAD (pre-write): 1ac0abc6853a35fa2761227520e0ecfef8ae3bcd
Changed: 08-Meeting-Room/OPEN-GAPS-DECISION-MAP.md
Actions: N/A (docs only)
Verdict: Decision map published from Repository reality — no Production change
```
