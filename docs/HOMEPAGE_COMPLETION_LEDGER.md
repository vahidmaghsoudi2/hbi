# HBI Homepage — Completion Ledger and No-Repeat Rule

**Mission:** HBI homepage/navigation completion, PR #363  
**Owner:** PO / homepage implementation owner  
**Source of truth:** GitHub repository; until merge, this ledger is an execution record on `feat/homepage-dashboard-stage2`, not a claim that `master` contains the changes.  
**Current branch head at registration:** `dd5648cec489f5e56be293720157be87ae2b49dd`  
**Current master at last verified check:** `335fd6e472dde72b9907366acaa04db28ebed943`  
**PR:** https://github.com/vahidmaghsoudi2/hbi/pull/363

## Durable rule: do not repeat completed work

Before any homepage task, read this ledger and inspect only:
1. items marked OPEN / BLOCKED;
2. failed checks or new evidence;
3. changes made after the recorded SHA;
4. post-merge verification when PR #363 is merged.

Do not re-audit or re-implement a VERIFIED item unless new evidence shows regression, the relevant code changed, or the PO explicitly reopens it. A chat summary alone is not evidence. Update this ledger in the same change that closes an item, with the commit SHA, test run URLs, and remaining blockers.

## Four work items

| ID | Work item | Recorded evidence | Status |
|---|---|---|---|
| HP-01 | Establish automated CI and browser evidence for the homepage work | Earlier green runs recorded in project context: CI https://github.com/actions/runs/38867266972 and browser proof https://github.com/actions/runs/38867267004. These are historical evidence only and must not be represented as checks for the current head. | VERIFIED at that historical checkpoint; current-head checks are tracked under HP-04 |
| HP-02 | Remove the standalone catalog as a competing entry and route the obsolete `/catalog` URL to the homepage | Commit `e16cccfc0d338d4ea61cca6a8648bc15dc34241d`; CI https://github.com/actions/runs/38868660433; browser proof https://github.com/actions/runs/38868660269. | VERIFIED for that commit; do not repeat unless regression/new evidence |
| HP-03 | Remove placeholder Settings from the homepage and place Admin logout in the fixed header; add browser assertion | Commit `dd5648cec489f5e56be293720157be87ae2b49dd`; test file `tests/browser/homepage-navigation.spec.cjs`. Exact-head checks were still running when this ledger was registered. | PARTIAL: implementation committed; exact-head checks are part of HP-04 |
| HP-04 | Integrate PR #363 safely with `master`, resolve conflicts, and complete current-head verification | PR #363 was retargeted to `master`; GitHub reported `mergeable=false` / `mergeable_state=dirty`. Current head `dd5648cec489f5e56be293720157be87ae2b49dd`; base `335fd6e472dde72b9907366acaa04db28ebed943`. | BLOCKED: conflicts must be resolved and required CI/browser checks must pass. Do not merge while blocked. |

## Merge and closure gate

HP-04 can be marked VERIFIED only after all of the following are recorded:
- conflict-free PR against current `master`;
- required CI and browser proof green for the exact final PR head;
- merge result and merge commit SHA;
- post-merge verification against the resulting `master` SHA;
- this ledger updated with evidence and no remaining homepage integration blocker.

Until then, PR #363 is **open / draft / unmerged**, and `master` must not be described as containing the homepage branch changes.

## Handoff

Next action: continue HP-04 only. Do not restart HP-01, HP-02, or HP-03 from scratch. First identify the actual conflicting files and resolve them on the PR branch without overwriting unrelated `master` changes; then rerun exact-head checks and update this ledger.
