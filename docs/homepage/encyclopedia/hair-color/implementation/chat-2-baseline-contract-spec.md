# Chat 2/6 — Baseline & Executable Contract Specification

**Status:** Documentation contract drafted and reconciled. This is not runtime code or a production authorization.  
**Baseline:** Activity 42 handoff (PR #643), Activity 43 tracking matrix, owner decisions summarized in project context.

## 1. Version 1 scope

### Included in the intended first implementation
- Catalog identity and exact catalog membership/lookup; fail-closed behavior.
- Owner-defined rules only within their explicit scope.
- Typed consultation intake: current base, target preference, prior services, regional hair-state, source/confidence/uncertainty/conflict.
- Four motor states, five response states, ten workflow states and guarded transitions.
- Missing-data, knowledge-gap, safety/scope, condition, and internal-failure controls.
- Candidate validation, evidence/goal-fit basis, ranking, maximum three valid alternatives (never truncate invalid candidates into valid ones).
- Rejection trace and rejected suggestion suppression.
- Target versioning and dependency-based invalidation.
- Client stop and fresh restart gate.
- Separate question, suggestion acceptance, and execution consent.
- Evidence/review/correction record structures and audit trace.
- Synthetic fixtures and test-only implementation until approved.

### Excluded from V1
- Customer-facing/production advice or service execution.
- Deterministic result or formula from one photo.
- Image inference of pigment, porosity/structure, or chemical history.
- Fuzzy shade/product equivalence or unsupported chemistry/performance claims.
- Auto-resume after client stop.
- Automatic acceptance or execution consent.
- Silent promotion of specialist or PO pending statuses.
- Product-document axes previously excluded by PO; they must not become blockers in this scope.

## 2. Input contract

All fields are typed/structured; no field may be silently inferred when its source or confidence is unknown. Missing required fields are represented as missing/unknown and routed through clarification or a safe non-advice state.

| Input group | Required semantics | Validation/handling |
|---|---|---|
| Case identity | Stable case ID and current version | Reject malformed identity; version is monotonic |
| Current base | Descriptive level/base, source, confidence, region(s), uncertainty | Image-only does not establish chemistry or structure; uncertain/conflicting input cannot be treated as confirmed |
| Target preference | Explicit client goal, dimensions, priority/constraints, clarification status | Goal change creates new version and fresh evaluation |
| Service history | Type, date/recency if known, source, confidence, region, unknown vs none-reported | Unknown is not equivalent to no history; conflicts are retained and gated |
| Regional state | Root/mid/ends or relevant zones; state descriptors, source/confidence, uncertainty | Preserve regional differences; no image-only inference of chemical history or hair structure |
| Catalog selection | Exact series/code identity and membership | Unknown/non-member code fails closed; no fuzzy equivalence |
| Client interaction events | question, reject, accept, execution consent, stop, restart as distinct events | Explicit scoped event; no implicit decision |
| Evidence/review refs | Evidence ID, source, scope/version, reviewer identity/date/status when applicable | References must be traceable; pending review remains pending |

## 3. Output contract

Every response/run must include a canonical response state and a reason/limitation record. Output is suppressed on internal failure and on gates that prohibit a suggestion.

| Output | Contract |
|---|---|
| Response state | One of the five canonical response labels; conditional suggestion remains a motor state, not a sixth response label |
| Motor state | One of four canonical motor states, scoped to the run |
| Case state | One of ten workflow states; transitions guarded |
| Suggestions | Only valid, scoped, evidence/goal-fit candidates; rejected/invalid/unvalidated candidates are not active |
| Alternatives | At most three valid alternatives; do not truncate then treat invalid entries as valid |
| Reasons | User-understandable reason; no internal implementation leakage |
| Gaps | DATA_GAP, KNOWLEDGE_GAP, SAFETY_STOP, SCOPE, CONDITION, ENGINE_FAIL remain distinct; mixed gaps preserve all relevant gates |
| Version/dependencies | Current version, affected dependencies, invalidated outputs/reviews/decisions |
| Audit | Event ref, timestamps where available, actor/source, prior/new version, decision scope |
| Limitations | Explicit uncertainty and no-evidence limitations; no guessing |

## 4. Canonical states (names are contract-level; implementation enums may map but must preserve semantics)

### Four motor states
1. Suggestion reviewable by specialist.
2. Conditional suggestion tied to a named condition.
3. Request more information.
4. Stop/referral with reason.

### Five consultation response states
1. Suggestion reviewable by specialist.
2. More information or test needed.
3. In-person/specialist review needed.
4. Safety stop — no execution suggestion.
5. Outside V1 scope.

Conditional suggestion is not a sixth response state.

### Ten case workflow states
1. Incomplete acceptance.
2. Awaiting evaluation.
3. Awaiting test.
4. Safety stopped.
5. Ready for specialist decision.
6. Awaiting client confirmation.
7. Approved for execution.
8. In execution.
9. Needs follow-up.
10. Closed.

Transition guards must prohibit bypassing required evaluation, test, specialist/client gates, execution consent, or restart checks.

## 5. Interaction and event rules
- Informational client questions before decision do not force accept/reject and preserve case, suggestion, and version unless dependencies change.
- Suggestion rejection is traceable to suggestion ID/version/fingerprint; rejected suggestion must not resurface as active. Alternatives are only valid, evidence-scoped and goal-fit; maximum three.
- Suggestion acceptance and execution consent are separate, explicit, scoped events. Neither is inferred from questions, positive language, or acceptance alone.
- Target change: new version and fresh evaluation; invalidate affected suggestions and dependent decisions/reviews.
- Effective data change: dependency-based re-evaluation only; affected acceptance, consent, and specialist review do not carry automatically.
- Client stop: record request; record only steps actually performed; no auto-resume. Restart requires fresh evaluation of current state, data, safety, rules, evidence, and fresh authorization.
- No evidence: state that reliable answer is unavailable; do not guess.
- ENGINE_FAIL/internal control failure: fail closed and suppress output for that run.
- DATA_GAP, KNOWLEDGE_GAP, and ENGINE_FAIL are distinct; mixed gaps are not collapsed into a single reason.

## 6. Candidate/suggestion gate
A candidate is eligible for display only if all applicable gates pass:
- exact catalog identity/membership when product-specific;
- within V1 scope;
- required data sufficient and not unresolved conflicting;
- no safety, scope, or engine stop;
- evidence/validation status supports the claim at its scope;
- goal-fit basis is explicit;
- candidate is not rejected or invalidated for the current version;
- conditional requirements, if any, are clearly stated and unmet conditions do not permit unconditional output.

If only one candidate is valid, show one. If multiple valid options, rank by documented goal-fit and technical-validity basis and show no more than three. Do not create candidates by fuzzy similarity or fill a quota.

## 7. Version and dependency contract
- Case version is monotonic; each effective change records old/new version, source, scope, and affected dependency set.
- Target change triggers full target-dependent fresh evaluation and invalidates target-dependent suggestions and decisions.
- Data changes invalidate only dependent outputs; unrelated unaffected outputs may remain, but their dependency provenance must be recorded.
- Unknown dependency mapping fails closed for affected outputs.
- Acceptance, execution consent, and specialist review are scoped to exact case version/suggestion/dependency; no automatic carry-over to changed versions.
- Stop/restart is not a continuation token; restart is a fresh evaluation and authorization.

## 8. Error taxonomy and precedence
- DATA_GAP: required case data absent, unknown, conflicting, or insufficient.
- KNOWLEDGE_GAP: relevant rule/evidence unavailable or outside validated knowledge.
- SAFETY_STOP: safety condition prevents suggestion/execution pathway.
- SCOPE: request outside V1.
- CONDITION: valid path depends on an unmet named condition.
- ENGINE_FAIL: internal inconsistency, control failure, or unexpected engine failure.
- Preserve distinct reasons in mixed cases; apply output-suppression/fail-closed precedence for ENGINE_FAIL and SAFETY_STOP. No suggestion output may leak from a failed run. DATA_GAP/KNOWLEDGE_GAP do not authorize guessing.

## 9. Evidence/review record contract
A review record must include topic/rule ID, reviewer reference/authority, date, evidence references, evidence scope/version, finding/outcome, limitations, and record reference. Correction application requires actual scoped specialist acceptance, evidence refs, PO approval/ref, baseline/target versions, and an application receipt. A schema or blank record is not evidence of review. Owner-defined rules remain owner-defined; specialist review cannot silently change PO authority.

## 10. API/UI/persistence contract for H4 (design only; no implementation in Chat 2)
- API must validate input and return canonical states, reason codes mapped to plain-language explanations, limitations, version/dependency references, and audit IDs.
- Do not expose internal control implementation details or raw exception traces.
- Persist versioned case data and append-only decision/review/consent/stop/restart events; do not overwrite history.
- UI presents question, reject, accept, execution consent, and stop as separate controls/events; displays uncertainty, gaps, reasons, conditional requirements, and stop status.
- Synthetic data only; production/customer use remains disabled until release gate.

## 11. Acceptance criteria for Chat 3 (H1)
1. Exact catalog identity and membership lookup; unknown/nonmember fail closed.
2. Owner rules have explicit scope; no cross-brand/range generalization.
3. Typed intake preserves source/confidence/uncertainty/conflict and regional data.
4. Unknown is not treated as none-reported for service history.
5. Image-only inputs do not establish pigment, porosity/structure, or chemical history.
6. Target/current-base/history/region are separate fields and dependency groups.
7. Version and dependency identifiers are explicit; no fuzzy matching.
8. Unit/contract tests cover valid, missing, unknown, conflict, and out-of-scope inputs.
9. Synthetic fixtures only; no customer data.
10. No runtime consultation or production authorization implied by H1 completion.

## 12. PO / specialist decisions and gates
- H0 baseline/scope and implementation authorization are still a distinct PO gate; this chat's approval to proceed with documentation does not automatically approve runtime implementation.
- Specialist evidence/review remains pending and cannot be simulated.
- PO decides the intended V1 boundary and any scope changes; unresolved decisions are labeled and do not become assumptions.
- This specification does not authorize PR merge, deployment, customer-facing advice, or service execution.

## 13. Chat 2 completion and next step
Chat 2's deliverables are:
1. Activity 43 dependency/gate tracking matrix.
2. Baseline/executable-contract specification (this document).
3. README roadmap status/link reconciliation.

Chat 3 scope is H1 only: domain/catalog foundation in a synthetic/test environment, and it may begin only after the H0 baseline gate is explicitly reviewed/authorized. No H2 consultation-engine work in Chat 3.
