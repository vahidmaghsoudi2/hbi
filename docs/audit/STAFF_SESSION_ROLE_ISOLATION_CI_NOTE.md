# Staff-session role isolation — CI evidence

- Workflow: HBI CI
- Run: #1081 — https://github.com/vahidmaghsoudi2/hbi/actions/runs/37991094438
- Exact code SHA tested: `2cdd975abb76cfed84c8a3405777082799608aa5`
- Result: `test` and `governance-tests` succeeded; the test job's strict-coverage step and frontend build passed.
- Scope: refresh-token claim isolation, staff-customer-session role isolation, customer identity contract, and sellable-inventory recommendation gates are covered by the branch's test suites.

This note is historical evidence for the stated SHA. A documentation-only refresh changes the branch head, so the new final SHA must receive its own CI result before being reported green.

Limitations:
- Live target database schema: NOT VERIFIED.
- Deployed target-runtime E2E: NOT VERIFIED.
- No migration/schema file is changed by PR #326; PR-introduced migration is NOT APPLICABLE.
- PR #326 remains Draft and unmerged pending the required verification and PO decision.
