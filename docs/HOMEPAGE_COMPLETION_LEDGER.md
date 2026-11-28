# HBI Homepage — Completion Ledger and No-Repeat Rule

**Mission:** HBI homepage/navigation completion, PR #363  
**Source of truth:** GitHub `master`  
**Homepage implementation PR:** https://github.com/vahidmaghsoudi2/hbi/pull/363  
**Merged implementation commit:** `0463044d7b49b4847b70d388766484fce5504392`

## No-repeat rule
Before homepage work, read this ledger and inspect only items marked OPEN/BLOCKED, failed checks, code changed after recorded evidence, or required post-merge verification. Do not re-audit or re-implement a VERIFIED item unless new evidence shows regression, relevant code changed, or the PO explicitly reopens it. Update this ledger whenever an item changes status.

## Tracked work items

| ID | Work item | Evidence | Status |
|---|---|---|---|
| HP-01 | Establish CI and browser evidence for homepage work | Final PR-head checks: CI https://github.com/actions/runs/38872575903; browser proof https://github.com/actions/runs/38872575898; auto evidence https://github.com/actions/runs/38872575900. All completed successfully for head `1b53fb7890e7671f404b33cdd857e26e1da34632`. | VERIFIED |
| HP-02 | Remove standalone catalog entry and redirect obsolete `/catalog` route | Implementation commit `e16cccfc0d338d4ea61cca6a8648bc15dc34241d`; earlier CI https://github.com/actions/runs/38868660433 and browser proof https://github.com/actions/runs/38868660269. Final browser proof also passed on the merged PR head. | VERIFIED |
| HP-03 | Remove placeholder Settings and place Admin logout in fixed header | Implementation commit `dd5648cec489f5e56be293720157be87ae2b49dd`; obsolete Settings assertion removed; final browser proof passed at `1b53fb7890e7671f404b33cdd857e26e1da34632`. | VERIFIED (superseded by HP-05) |
| HP-04 | Reconcile PR with current master, verify checks, merge and post-merge verify | PR #363 merged: `0463044d7b49b4847b70d388766484fce5504392`. GitHub reported conflict-free before merge; CI, browser proof, and auto evidence all passed on final PR head. | MERGED; post-merge local runtime check remains separate |
| HP-05 | Remove all management-account logout buttons from homepage surfaces | PO direction 2026-11-15. Verified absent from `NewHomePage.tsx` on current master. | DONE |
| HP-06 | Align dashboard (page-1 of gallery home) with approved system diagram / operational mock | Implementation and exact-head verification in [PR #674](https://github.com/vahidmaghsoudi2/hbi/pull/674), commit `38bb45b42792afc0f133ec0a562ce451f1fd0d33`: HBI CI 1076 passed / 89% coverage / 2 subtests; Auto Tasks success; Browser Proof 29 passed. Dashboard screenshot included in browser artifact. Master integration remains pending. | DONE (PR branch verified; merge pending) |

## Closure gate and verification boundary
- **Code integration:** VERIFIED in `master` at merge commit `0463044d7b49b4847b70d388766484fce5504392`.
- **Automated evidence:** HP-05 verified in master; HP-06 exact PR-head checks all passed on PR #674 (CI, Auto Tasks, Browser Proof). Integration/merge is pending.
- **Local Windows runtime/database:** not claimed as tested from GitHub workflows.
- If a post-merge regression appears, reopen only the affected item and attach the new evidence. Do not restart HP-01 through HP-03 without cause.

## Handoff
HP-05 is DONE on master; HP-06 is DONE on verified PR #674 branch, with integration pending. No further homepage work until PR #674 is integrated. Then continue Priority 2: Skin Intake Template Forms V1. Do not repeat HP-01 through HP-05.
