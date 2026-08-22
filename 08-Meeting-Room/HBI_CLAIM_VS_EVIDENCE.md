# HBI — Claim vs Evidence (LOCKED)

**Status:** LOCKED
**Date:** 2026-08-23

```text
Claim ≠ Evidence.
GitHub state + test/Actions result = Evidence.
```

## Forbidden

- Partial or placeholder SHAs (`a1b2c3d...`, invented tips)
- Naming files as "ready" without path existing on `master`
- Treating chat text as Source of Truth

## Required for any Write/Done claim

1. Full 40-character commit SHA from GitHub API or `git rev-parse`
2. Path exists under that SHA (raw URL or API get_contents)
3. If tests required: Actions run URL with conclusion on that SHA

## Reality Check (PO / Qwen1)

Before trusting any AI package:

```powershell
cd E:\hbi
git fetch origin
git rev-parse origin/master
git ls-tree -r --name-only origin/master | Select-String "path/of/claimed/file"
```

If missing → REJECT; demand real push first.
