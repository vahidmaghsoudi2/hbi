# HBI Homepage — Completion Ledger and No-Repeat Rule

**Mission:** HBI homepage/navigation completion, PR #363  
**Source of truth:** GitHub `master`; this ledger tracks the PR branch until merge.  
**PR:** https://github.com/vahidmaghsoudi2/hbi/pull/363

## No-repeat rule
Before homepage work, read this ledger and inspect only items marked OPEN/BLOCKED, failed checks, changed code after recorded evidence, or required post-merge verification. Do not re-audit or re-implement a VERIFIED item unless new evidence shows regression, relevant code changed, or the PO explicitly reopens it. Update this ledger whenever an item changes status.

## Four tracked work items

| ID | Work item | Evidence | Status |
|---|---|---|---|
| HP-01 | Establish CI and browser evidence for homepage work | Historical runs: https://github.com/actions/runs/38867266972 and https://github.com/actions/runs/38867267004. These are not evidence for the current reconciled head. | Historical checkpoint verified; exact-head checks required |
| HP-02 | Remove standalone catalog entry and redirect obsolete `/catalog` route | Commit `e16cccfc0d338d4ea61cca6a8648bc15dc34241d`; CI https://github.com/actions/runs/38868660433; browser proof https://github.com/actions/runs/38868660269. | Verified at recorded commit; do not repeat without regression evidence |
| HP-03 | Remove placeholder Settings and place Admin logout in fixed header | Original implementation commit `dd5648cec489f5e56be293720157be87ae2b49dd`; browser assertion in `tests/browser/homepage-navigation.spec.cjs`. | Implementation present; exact final-head checks required |
| HP-04 | Reconcile PR with current master, verify checks, merge and post-merge verify | Master baseline at reconciliation: `335fd6e472dde72b9907366acaa04db28ebed943`. | OPEN until exact-head CI/browser checks pass, PR merges, and post-merge master is verified |

## Closure gate
HP-04 is VERIFIED only when the PR is conflict-free against current master, required CI and browser proof pass on the exact final head, merge SHA is recorded, and post-merge verification against master is complete. Until then, do not describe the homepage work as merged or complete.

## Handoff
Continue HP-04 only. Do not restart HP-01, HP-02, or HP-03. Fix only newly evidenced blockers, then update this ledger with CI/browser run URLs and merge evidence.
