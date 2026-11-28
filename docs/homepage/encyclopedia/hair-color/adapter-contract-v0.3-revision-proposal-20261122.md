# Adapter Contract 0.2 → 0.3 revision proposal (review only)

**Status:** Technical proposal; not PO-approved; not runtime-authorized.  
**Date:** 2026-11-22  
**Intent:** Convert known H1 gaps into a small, reviewable contract revision and test plan. Do not modify 0.2-draft runtime, schema, fixtures, or tests until explicit approval.

## 1. Scope and guardrails

This proposal is limited to request semantics, evidence traceability, candidate structure, and authoritative publication checks. It preserves:
- four engine states, five consultation response states, ten workflow states as separate layers;
- DATA_GAP, KNOWLEDGE_GAP, ENGINE_FAIL distinctions;
- synthetic-only current policy; no real customer data;
- no engine authority for persistent suggestion IDs, client decisions, execution consent, workflow state, or performed steps;
- no chemical execution instructions or formula-generation capability;
- max three candidate options, hard constraints before ranking, ranking independent of input order;
- S06 and S08 wire mappings unresolved unless PO selects a proposal.

## 2. Request-operation semantics

### Current gap
Current Adapter request fields do not include question; existing test helper adds question at top level, but _REQUEST_FIELDS does not require it and the draft schema does not encode operation-specific conditional fields.

### Proposed design options (PO/contract review)
| Option | Question field design | Advantages | Risks/limitations |
|---|---|---|---|
| Q-A (recommended for simplicity) | question: non-empty string required only for ANSWER_QUESTION; forbidden/omitted for other operations | minimal, easy schema/test; natural-language context remains separate | may later need structured intent or referenced suggestion context |
| Q-B | question_context object with question text + exact suggestion ref/version for ledger lookup request | makes exact referent explicit | Orchestrator must resolve refs; engine must not author ledger truth |
| Q-C | question text plus question_about discriminated object (e.g. existing suggestion vs general case) | explicit routing semantics | more complex; may be premature |

**Recommendation:** Q-A for initial wire contract, with optional read-only question_about suggestion ref/version only if S11 needs it. Exact suggestion current status is checked by Orchestrator/Ledger, never by trusting engine context. PO must approve final request shape before runtime.

### Operation matrix (proposed)
| Operation | Required inputs | Decision behavior forbidden |
|---|---|---|
| EVALUATE_CASE | current case/target snapshot + pinned policy/evidence refs | no client decision or workflow event |
| REEVALUATE | fresh snapshot and changed/current target/data context | no automatic resume or carry-over consent |
| ANSWER_QUESTION | non-empty question; exact referent when about existing suggestion | cannot accept/reject/authorize service; no ledger mutation |

## 3. Typed request substructures (illustrative, not approved schema)

Proposed request adds target_ref, snapshot_ref, question, and optionally question_about exact suggestion ref/version. Case and policy context should become typed, provenance-bearing snapshots rather than opaque blobs. Evidence context is a collection of exact references and scope metadata, not model-created evidence.

Conditional rule proposal: question must be non-empty for ANSWER_QUESTION; question_about is allowed only if Orchestrator has resolved the referenced suggestion and supplied bounded, read-only context. A question is an interaction, not a decision event.

## 4. Provenance-bearing case fields (illustrative)

A datum should be a structured record with:
- field_ref and field_name;
- knowledge_state and value;
- source_class, source_ref, actor/source attribution;
- recorded_at and observed_at where distinct;
- derivation_ref if computed;
- case_ref and case_version.

The six approved knowledge states remain distinct: KNOWN, UNKNOWN, NOT_ASKED, MISSING, CONFLICT, NOT_APPLICABLE. Preserve false as a known value, not a proxy for unknown. Provenance classes need a final controlled vocabulary and schema review. This shape does not infer hidden attributes or chemistry from images.

## 5. Candidate output — run-local identity and claim/evidence links

Current response-level evidence_refs cannot demonstrate that each candidate/claim has applicable support. Proposal: each candidate has a request-local candidate_key, display summary, claim records, rule refs, evidence refs attached to the claim, scope-match/support status, explicit hard-constraint checks with evidence, conditions and limitations.

**Boundary:** illustrative fields only; no actual product, chemical, safety, feasibility, or result claims. Final statuses/enums and whether fields are required must be reviewed. Engine may propose local keys and claim links; it cannot create authoritative persistent suggestion_ref, active/rejected status, client acceptance, execution consent, or workflow. Orchestrator persists only after validation and gate passes.

### Candidate-validation requirements proposed
- candidate keys unique within one run;
- every material claim has applicable evidence/rule refs;
- each evidence ref resolves to request context and scope matches the claim;
- evidence support/status is not inferred from reference existence alone;
- hard-constraint results explicit; failed options never appear;
- candidate-specific blockers suppress candidate; global blockers suppress all options;
- candidate count <= 3 and no padding/fabrication;
- ranking is criteria-based and stable under input permutation;
- no executable chemical instruction fields (recursive prohibition preserved).

## 6. S06/S08 mapping alternatives — no decision made

| Fixture oracle | Meaning | Mapping alternative A | Mapping alternative B | Recommendation / PO gate |
|---|---|---|---|---|
| S06 KNOWLEDGE_GAP | data may be sufficient but applicable reliable evidence/rule unavailable; dependent output withheld | NEEDS_MORE_INFORMATION + KNOWLEDGE_GAP reason, consultation NEEDS_INFORMATION_OR_TEST | STOP_OR_REFER_WITH_REASON + KNOWLEDGE_GAP; OUT_OF_V1_SCOPE only if formal scope boundary exists | A better preserves evidence gap distinct from out-of-scope; confirm PO/contract mapping |
| S08 NOT_FEASIBLE_OR_UNVERIFIED | no valid alternative in fixture; explain constraint or uncertainty; do not invent option | STOP_OR_REFER_WITH_REASON + OUT_OF_SCOPE only when request is outside scope; otherwise separately define supported constraint reason | STOP_OR_REFER_WITH_REASON + KNOWLEDGE_GAP when feasibility is unverified | Do not map every no-option case to OUT_OF_V1_SCOPE; PO must decide |

No option is selected. Existing fixture oracle strings remain unchanged until an approved contract/fixture revision.

## 7. S11–S13 ledger and version references

The fixture traceability_oracle is test-only and should not be copied verbatim into wire response:
- S11 question: Orchestrator resolves exact suggestion ref/version, current ledger status, case/target lineage, and workflow stop state before requesting explanation; response cannot change decisions.
- S12 rejection: rejection event refers to exact persistent suggestion ref/version. Ledger records event; rejected version is no longer active. Alternative is a new candidate from fresh evaluation, never reactivation.
- S13 target change: target and case versions change through authoritative service. Dependency service recomputes affected output refs. Acceptance, execution consent and specialist review do not carry over to new target/version.

Open: exact version tuple, event ordering, current-ledger validation, atomicity, and invalidation protocol.

## 8. Publication gate — technical checklist proposed

Before a candidate or explanation is shown:
1. Resolve request identity, operation semantics, case/target versions.
2. Validate case snapshot provenance and conflict/missing-data states.
3. Pin policy/rule and evidence versions.
4. Validate each candidate key, claim, constraint, and candidate-specific evidence link.
5. Enforce consultation state/reason compatibility and option suppression.
6. If existing suggestion is referenced, resolve its exact persistent version from authoritative ledger.
7. Re-check case/target/evidence/policy/workflow/ledger state immediately before publish; stale dependency => suppress current output.
8. Orchestrator persists validated suggestion identity and audit/correlation refs; engine never does.
9. Publish only current validated response. Client question does not mutate acceptance/consent.
10. Workflow changes remain in workflow service.

Atomicity and retry semantics are open technical design, not implemented here.

## 9. Test proposal mapped to gaps

| ID | Scenario | Required assertion | Layer |
|---|---|---|---|
| Q01 | ANSWER_QUESTION missing question | reject before engine | Adapter request validation |
| Q02 | blank question | reject before engine | Adapter request validation |
| Q03 | question supplied on wrong operation | reject or explicitly ignore per approved contract; decision needed | Adapter |
| C01 | duplicate candidate keys | reject | response validation |
| C02 | candidate claim has no evidence link | withhold/reject candidate | response validation |
| C03 | candidate evidence ref not in request | reject | response validation |
| C04 | evidence in request but scope mismatch | candidate suppressed/rejected | evidence validator |
| C05 | candidate fails hard constraint | failed candidate absent | candidate gate |
| C06 | ranking input permuted | same ranked output | evaluator |
| C07 | >3 valid candidates | max three, no fabricated padding | evaluator/adapter |
| L01 | S11 exact suggestion not active | no explanation as current active suggestion | Orchestrator/ledger |
| L02 | S12 rejection exact ref/version | ledger records exact event; candidate not reactivated | Ledger |
| V01 | S13 target change | new target/case lineage; dependency outputs recomputed | Case Store/Dependency |
| V02 | unrelated datum change | unaffected output retained only if dependency proof exists | Dependency service |
| W01 | S14 stop then restart | stop event, performed steps, fresh reevaluation only | Workflow/Orchestrator |
| F01 | S15 engine failure | failed run correlation; no current/stale candidate published as current | Orchestrator/publish gate |
| F02 | concurrent case/target change at publish | stale output suppressed | atomic publication gate |

These are proposed tests, not additions to existing tests or new fixture oracles.

## 10. Approval/implementation gates

- **PO review:** Q-A/Q-B/Q-C question semantics; S06/S08 mapping; candidate field requirements if they affect product claims; event/policy behaviors.
- **Technical review:** validation ownership, schema conditional rules, claim/evidence link structure, correlation/idempotency, atomic publish protocol.
- **Specialist review:** any claim/rule about actual products, hair-color chemistry, safety, feasibility or result; this proposal does not contain or authorize such rules.
- **Implementation authorization:** runtime, schema, fixture, test, persistence, service, pilot, or release changes.
