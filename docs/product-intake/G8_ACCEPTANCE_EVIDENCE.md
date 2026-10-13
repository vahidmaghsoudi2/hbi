# G8 Acceptance Evidence Ledger

**Current gate: G8 = BLOCKED / NOT VERIFIED**  
**Governing tracker:** [Issue #283](https://github.com/vahidmaghsoudi2/hbi/issues/283)  
**Roadmap:** [PRODUCT_INTAKE_ROADMAP.md](PRODUCT_INTAKE_ROADMAP.md)  
**Execution log:** [PRODUCT_INTAKE_EXECUTION_LOG.md](PRODUCT_INTAKE_EXECUTION_LOG.md)

A criterion is PASS only when raw evidence is linked, tied to an exact SHA/environment and independently reviewed. CI success and fixture-based browser proof are supporting evidence, not real-pilot acceptance.

| Criterion | Required evidence | Current status | Missing proof / note |
|---|---|---|---|
| A1 | Explicit product identity and operator-selected `product_line=SKIN`; no inference | PARTIAL | API test only; real operator session not evidenced |
| A2 | Duplicate check before create, including duplicate/unknown identity cases | PARTIAL | New-path test exists; negative/edge cases and real UI path not evidenced |
| A3 | Lifecycle state persisted and read back; no premature transition | PARTIAL | Draft state API/ORM test only |
| A4 | Source-attributed research and claims persisted/read back | PARTIAL | Draft assertions tested; real runtime record not evidenced |
| A5 | Invalid claim types/mappings rejected; required FACT provenance enforced | NOT VERIFIED | Negative validation evidence package missing |
| A6 | Safety, review, permission and approval gates enforced | NOT VERIFIED | Runtime gate-denial evidence missing |
| A7 | Authorized approval/activation and resulting state/audit readback | NOT VERIFIED | No approved real pilot transition evidenced |
| A8 | Recommendation eligibility/readback after legitimate gates; product-line boundary enforced; scoring unchanged | NOT VERIFIED | No real downstream recommendation readback evidenced |
| A9 | Disposable cleanup and production isolation independently proved | PARTIAL | Fixture teardown is not independent post-run cleanup/isolation proof |

## Supporting evidence (not G8 acceptance)

- [PR #355](https://github.com/vahidmaghsoudi2/hbi/pull/355): draft disposable API test; not a real operator pilot and not merged.
- [HBI CI run 38315913219](https://github.com/vahidmaghsoudi2/hbi/actions/runs/38315913219): successful test run on the PR #355 test head.
- [Pilot Browser Proof run 38315913216](https://github.com/vahidmaghsoudi2/hbi/actions/runs/38315913216): fixture/browser workflow, not end-to-end real product acceptance.
- [PR #364](https://github.com/vahidmaghsoudi2/hbi/pull/364): documentation-only draft; its green workflows do not prove G8.

## Acceptance rule

G8 remains BLOCKED / NOT VERIFIED until each required criterion is supported by raw, traceable evidence and independent review. Do not mutate production data, run migrations, change Product A–D, receive stock, alter recommendation scoring/weights/thresholds, or bypass the binding contract to force a PASS.
