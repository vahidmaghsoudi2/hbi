# Change Package — Dual get_db deduplication

**Status:** ✅ EXECUTED  
**Executed SHA:** `c0bb7accf8337408598f3045959af14d24adfbc2`  
**Actions:** success — https://github.com/vahidmaghsoudi2/hbi/actions/runs/32633998012  
**Executor:** Grok2 (per EXECUTE order)

---

## Result

- Local `get_db` body removed from `app/core/deps.py`
- Re-export: `from app.database import get_db`
- Diff: −11 / +1 on `app/core/deps.py` only
- Import path `from app.core.deps import get_db` preserved
- HBI CI green on execute SHA

## DONE WHEN (checklist)

1. ✅ Single session implementation for API path
2. ✅ Re-export works
3. ✅ Actions success on change SHA
4. ✅ TRACE recorded
5. ⏳ ChatGPT independent audit (not claimed by Grok2)
