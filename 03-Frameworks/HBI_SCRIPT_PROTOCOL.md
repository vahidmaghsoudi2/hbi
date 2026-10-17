# HBI — Script Protocol v2.2

**Status:** ACTIVE — specialized PowerShell delivery convention  
**Authority:** Subordinate to `docs/01_project_control/HBI_AGENT_EXECUTION_PROTOCOL.md` and `docs/01_project_control/PROJECT_RULES.md`.  
**Scope:** PowerShell blocks supplied to the Product Owner for local repository inspection or execution.  
**Repository:** `vahidmaghsoudi2/hbi`.

## 1. Precedence

This file governs only script format and reporting convenience. It does not authorize a repository mutation, destructive command, production operation, merge, or scope expansion. If a rule here conflicts with the unified execution protocol or a PO-approved domain contract, the higher-level authority wins.

## 2. Script delivery

1. When a PowerShell script is requested, provide one complete, directly copyable block and no more than three essential explanatory lines unless the task requires more.
2. A script must have one clear objective. Do not combine unrelated tasks into one script.
3. Use an explicit repository path variable. The last known local path is `E:\HBI_GitHub_Current`, but verify that it exists before using it; never assume a local path is valid merely because it appears in an old report.
4. Set `$ErrorActionPreference = "Stop"` for scripts that must fail closed. Use `Continue` only when intentionally collecting multiple independent diagnostics, and explicitly capture each failure.
5. Capture command output and errors when needed (for example, `2>&1 | Out-String`) without swallowing exit codes or converting failures into success.
6. For repository-state work, report the local HEAD and fetch/inspect the current remote default-branch SHA before drawing conclusions. If network access or authentication prevents this, report that limitation rather than using a stale SHA as current.
7. Never run `git reset --hard`, `git clean`, force-push, history rewrite, destructive deletion, or overwrite an existing file unless the PO explicitly authorized that exact action and the target has been inspected.
8. If the working tree has changes, identify and preserve them. Do not silently stash, discard, restore, or overwrite them.
9. For PowerShell work intended for the PO to run locally and return output to ChatGPT, provide one complete, efficient, directly pasteable block (not fragmented commands), use `E:\\HBI_GitHub_Current` after verifying the path, and automatically copy the concise final output to the clipboard with `Set-Clipboard`. Never copy credentials, tokens, secrets, or private data.
10. Never say a script was executed when only the text was drafted. Never report success based only on a script being generated.

## 3. Standard status

- `GREEN` — action succeeded and result was verified against its acceptance condition.
- `RED` — execution failed.
- `YELLOW` — partial, unverified, or blocked by missing evidence.
- `BLUE` — requires a Product Owner decision or authorization.

A command exit code of zero does not by itself mean the resulting artifact is verified.

## 4. Standard report

```text
TASK:
STATUS: GREEN | RED | YELLOW | BLUE
LOCAL PATH:
LOCAL HEAD:
REMOTE DEFAULT-BRANCH SHA:
ARTIFACTS / EVIDENCE:
FINDINGS:
BLOCKER:
NEXT ACTION:
TURN OWNER:
```

Only fill values that were actually observed. Mark inaccessible or unverified fields explicitly.

## 5. Final user instruction

When a PowerShell block is provided specifically for the user to run, end the short guidance with: «در چت Ctrl+V بزنید و ارسال کنید.»
