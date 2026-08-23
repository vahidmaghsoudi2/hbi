# ACTIVE OPERATIONAL LINE — Grok2 + ChatGPT

**Status:** ACTIVE  
**Registered by:** Grok2  
**Date:** 2026-08-23  
**HEAD at registration:** `a7aeace375305bb9db6f685623607edb62b9b13f`

---

## Current Line

| Role | Actor | Capability |
|------|--------|------------|
| GitHub Executive (Write) | **Grok2** | Read + Write |
| Auditor / Reality Check | **ChatGPT** | Read only (no direct Write) |
| Gate / QA | Qwen1 | As ordered |
| Commander | مهندس مقصودی (PO) | Final authority |

Grok1 is not in the current direct operational line.

---

## Communication Rules (locked)

1. **PO is not a postman.**  
2. Grok2 writes operational notes / REQUEST TO CHATGPT in this folder when needed.  
3. ChatGPT reads from GitHub.  
4. If ChatGPT needs to instruct Grok2, message goes via PO.  
5. Prefer continuous work: Read → Analyze → Decide → Execute (docs/Meeting-Room) → Commit → Verify.

### REQUEST template (when blocked)

```text
REQUEST TO CHATGPT
TASK:
MISSING INFORMATION:
WHY IT IS REQUIRED:
WHAT HAS ALREADY BEEN CHECKED:
DECISION BLOCKED: YES/NO
```

---

## Open Items (from Repository reality)

| Item | Status | Notes |
|------|--------|-------|
| Dual `get_db` dedup (`app/core/deps.py`) | **AWAITING EXECUTE** | Package ready: `CHANGE-PACKAGE-DUAL-GET-DB.md`. No `app/` write until explicit EXECUTE. |
| Handover currency | Drift possible | Handover still references older SHA/status in places; recent commits registered Products A–D identity updates. |
| Production code changes | Restricted | Only with `EXECUTE_APPROVED` + SCOPE. |

---

## Authority Limits (Grok2)

- **Allowed now:** Meeting-Room docs, TRACE, status registration, low-risk documentation.
- **Forbidden without EXECUTE:** Any write under `app/`.
- **Forbidden always:** Declaring final VERIFIED for important changes; inventing missing Evidence; incomplete SHA.

---

## Next Preferred Action

1. Keep dual-get_db package waiting for explicit EXECUTE.  
2. Continue low-risk documentation / TRACE hygiene.  
3. If Evidence or decision is missing → use REQUEST TO CHATGPT template above.

```text
HBI HUB — TRACE STATUS
Actor: Grok2
Current Task: Register active operational line
Repository: vahidmaghsoudi2/hbi
Branch: master
HEAD (pre-write): a7aeace375305bb9db6f685623607edb62b9b13f
Changed: 08-Meeting-Room/ACTIVE-LINE-GROK2-CHATGPT.md
Actions: N/A (docs only)
Verdict: Operational line registered — no Production change
```
