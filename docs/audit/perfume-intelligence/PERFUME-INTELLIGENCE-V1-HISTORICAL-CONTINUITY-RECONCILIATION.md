# Perfume Intelligence V1 — Historical Continuity & Gap Reconciliation

## Status
Purpose: reconcile prior Perfume Intelligence work with current repository history.
Authority: evidence/reconciliation artifact only. No implementation authorization.

## 1. Executive Finding
The historical record does not support treating Perfume Intelligence as a brand-new task.
Substantial prior work already exists: research baseline, scope/domain boundaries, risk register, deferred register, manual-pilot direction, simulated-vs-real boundary, static reality audit, and independent static verification.
The remaining gaps are narrower: exact-SHA CI proof, runtime evidence, real/manual pilot execution proof, and a complete perfume-specific runtime decision trace.

## 2. Completed Historical Work
### Research baseline
Branch: docs/perfume-intelligence-research-archive
Commit: 21fc146de3d0cf25a4c83f2b9045ae1b7e49ad50
Artifact: docs/audit/perfume-intelligence/PERFUME-INTELLIGENCE-V1-CONSOLIDATED-DOMAIN-RESEARCH-BASELINE-v0.1.md
Result: consolidated research foundation established. Architecture, contract, schema, implementation, automatic scoring, automatic recommendation and automatic learning were explicitly not authorized.

### Reality audit
Branch: docs/perfume-v1-reality-integration-audit
Base SHA: bbe1a4eed81937fae1c7ecb7be5bb28af551458b
Artifact: docs/audit/PERFUME-INTELLIGENCE-V1-HBI-REALITY-INTEGRATION-AUDIT.md
Result: PI-V1-01 through PI-V1-10 were audited. Verdict: AUDIT PARTIAL — ADDITIONAL EVIDENCE REQUIRED.

### Independent verification
Commit: a0895796d4aac29210b865413779d354a293e06e
Result: PI-V1-01 through PI-V1-08 substantially confirmed at static level; PI-V1-09 partial; PI-V1-10 static governance claims confirmed. Runtime remained unavailable and exact-SHA CI remained unverified.

## 3. Evidence Status Reconciled
| Item | Current historical status |
|---|---|
| Research foundation | COMPLETED |
| Domain/scope lock | COMPLETED |
| Risk/deferred registers | COMPLETED |
| Static reality audit | COMPLETED / PARTIAL RESULT |
| Independent static verification | COMPLETED / PARTIAL RESULT |
| Exact-SHA CI for audit base | NOT VERIFIED |
| Runtime environment identity | NOT VERIFIED |
| Runtime PERFUME evidence | NOT VERIFIED |
| Runtime identity/availability | NOT VERIFIED |
| Manual real consultation | NOT ESTABLISHED |
| Perfume-specific runtime decision trace | NOT ESTABLISHED |
| Architecture | NOT DECIDED |
| Contract | NOT AUTHORIZED |
| Implementation | NOT AUTHORIZED |

## 4. E-01 through E-07 Are Not Seven New Tasks
E-01: exact-SHA CI evidence remains unverified.
E-02: runtime environment evidence remains unverified.
E-03: runtime PERFUME evidence remains unverified.
E-04: runtime identity/availability evidence remains unverified.
E-05: the research baseline is manual-pilot-ready, but completed real execution is not proven.
E-06: perfume-specific runtime decision-trace evidence is not proven.
E-07: independent re-check was already performed for the static audit evidence. A new re-check is conditional on genuinely new evidence.

Therefore the previous Evidence Gate must be read as a remaining-evidence register, not as a list of six implementation tasks or proof that the entire Perfume phase was never attempted.

## 5. Critical Distinction: Product Line PERFUME != Perfume Intelligence
The master history contains a separate Product Line V1 sequence.
Commit e0934923ac14871c03fea469963be3413d1f97e2 temporarily introduced PERFUME in the product_line allowlist.
PR #282 was merged as c17c3b17af1a9fc05af998fe9c09ac869de196d1 and its accepted Product Line V1 state is SKIN | HAIR | BEAUTY | TOOLS | OTHER, with PERFUME remaining only in the separate Accounting Category.
Commit 92e3fb9f0afdc2a95dc1f31517ba482921553b2a tests rejection of PERFUME from Product Line V1.
Commit 0a79e84393b91783b0a8160eb70a8658dbab5c58 removes PERFUME from the Intake UI product_line options.
This proves that older PERFUME product-line history is not evidence of a Perfume Intelligence implementation.

## 6. Correct Current Boundary
Research: DONE.
Static audit: DONE WITH PARTIAL RESULT.
Independent static verification: DONE FOR AVAILABLE STATIC EVIDENCE.
Runtime/manual-pilot proof: NOT ESTABLISHED.

Thus the project should not restart the Perfume Intelligence research/audit phase.
The first genuinely remaining work is evidence acquisition at the runtime/CI/manual-pilot boundary.

## 7. Hard Boundaries
No new perfume Product Master, Evidence engine, ProductKnowledge engine, lifecycle engine, fragrance-specific schema, numeric scoring, automatic ranking, automatic recommendation or automatic learning is authorized by this reconciliation.
Unknown remains Unknown. Conflict remains visible. Manufacturer Claim remains distinct from Fact. Customer Report remains distinct from Product Fact. AI inference remains distinct from verified knowledge.

## 8. Reconciliation Verdict
Historical continuity: CONFIRMED.
Research baseline: COMPLETED.
Static reality audit: COMPLETED / PARTIAL.
Independent static verification: COMPLETED / PARTIAL.
Exact-SHA CI: NOT VERIFIED.
Runtime proof: NOT ESTABLISHED.
Manual real pilot proof: NOT ESTABLISHED.
Perfume runtime decision trace: NOT ESTABLISHED.
Architecture: NOT DECIDED.
Contract: NOT AUTHORIZED.
Implementation: NOT AUTHORIZED.

## Provenance
Research baseline: 21fc146de3d0cf25a4c83f2b9045ae1b7e49ad50
Audit base: bbe1a4eed81937fae1c7ecb7be5bb28af551458b
Independent verification: a0895796d4aac29210b865413779d354a293e06e
Evidence Gate: 95e4d06968e313754168af0961442f7035cdfee8
Product Line V1 merge: c17c3b17af1a9fc05af998fe9c09ac869de196d1
Product Line PERFUME rejection test: 92e3fb9f0afdc2a95dc1f31517ba482921553b2a
Product Line Intake PERFUME removal: 0a79e84393b91783b0a8160eb70a8658dbab5c58