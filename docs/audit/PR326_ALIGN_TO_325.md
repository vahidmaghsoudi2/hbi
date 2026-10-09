# PR #326 alignment to PR #325 — verified snapshot

## Repository evidence
- PR #325 branch head: `a6fbc0c70f09c141f802852c3df797add5279c33`
- PR #326 code head before this documentation refresh: `2cdd975abb76cfed84c8a3405777082799608aa5`
- `app/api/routers/customers.py` blob: `8bca7143db32eb9cea79aeb910db0715e1dc9fc1`
- `tests/test_identity_contract_mobile_family_name.py` blob: `145b75cf22e75d6b9647ac8fb586fc2591b087a0`

The branch sync carries the PR #325 identity contract into PR #326 without changing `master`. Same-mobile identity uses the explicitly supplied `data.family_name`; the stored surname is not used as a fallback.

## CI evidence
- HBI CI run #1081: https://github.com/vahidmaghsoudi2/hbi/actions/runs/37991094438
- Exact tested code SHA: `2cdd975abb76cfed84c8a3405777082799608aa5`
- Result: `test` and `governance-tests` succeeded, including the strict-coverage test step and frontend build.

This note refresh creates a documentation-only commit after that code snapshot. CI must be checked again on the resulting branch head before calling the latest head green.

## Verification boundary
- PR-introduced migration: NOT APPLICABLE; this PR changes no model/schema/migration file.
- Live target database schema: NOT VERIFIED.
- Deployed target-runtime end-to-end: NOT VERIFIED.
- PR #326: Draft and unmerged; `master` unchanged.
- PO acceptance and merge: NOT recorded by this note.
