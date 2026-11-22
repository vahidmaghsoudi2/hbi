# Adapter Contract 0.3 — synthetic technical specification (implementation-ready draft)

**Date:** 2026-11-22  
**Status:** Technical spec draft for synthetic scope only. It does not authorize runtime/schema/test implementation, product advice, chemical rules, real-client data, pilot, or release.  
**Prior-work rule:** This document refines the existing 0.3 proposal; it does not repeat the H1 audit, ownership matrix, or PO decision record.  
**Inputs:** Adapter 0.2-draft; H1 audit; ownership/publication gates; 0.3 revision proposal; Chat 1 technical decision record.

## 1. Scope of this revision

Only technical envelope and validation behaviors are specified here. All values and evidence refs in test examples must be synthetic placeholders. No real product/color claims, chemistry, or safety/feasibility assertions are permitted.

Resolved defaults delegated for synthetic contract closure:
- Q1: `ANSWER_QUESTION` requires a non-empty `question`; other operations reject the field.
- S06: retain `KNOWLEDGE_GAP`; suppress candidates. Next-owner is encoded as consultation status: `NEEDS_INFORMATION_OR_TEST` when the caller can supply additional evidence/data, or `NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW` when specialist ownership is required. The distinction must be explicit; no default inference from the reason code alone.
- S08: introduce typed `NO_VALID_OPTION` reason in the next version; engine state `STOP_OR_REFER_WITH_REASON`; no options. It is not synonymous with `OUT_OF_SCOPE` or `KNOWLEDGE_GAP`.

## 2. Operation-specific request rules

| Operation | Required | Allowed extra | Rejected |
|---|---|---|---|
| `EVALUATE_CASE` | common envelope | case/target snapshot, evidence refs, policy ref | question, question_about |
| `REEVALUATE` | common envelope + fresh snapshot identifiers | change-cause refs, dependency refs | question, question_about; resume token |
| `ANSWER_QUESTION` | common envelope + nonblank question | read-only `question_about` suggestion ref/version; resolved bounded context from Orchestrator | decision/consent/workflow mutation fields |

Question envelope:
```json
{
  "question": "Synthetic example question",
  "question_about": {
    "suggestion_ref": "SUG-MOCK-01",
    "suggestion_version": 1
  }
}
```
The Adapter validates shape only. Orchestrator/Ledger validates that suggestion identity/version is current and eligible; the engine receives only bounded read-only context. No response can carry decision or consent mutation.

## 3. Typed value/provenance record (contract-level minimum)

```json
{
  "field_ref": "FIELD-MOCK-01",
  "field_name": "synthetic_field",
  "knowledge_state": "KNOWN",
  "value": "MOCK-VALUE",
  "source_class": "SYNTHETIC_FIXTURE",
  "source_ref": "SOURCE-MOCK-01",
  "case_ref": "CASE-MOCK-01",
  "case_version": 1
}
```

Rules:
- Required identity and state are validated; optional value is present only when state supports a value.
- `UNKNOWN`, `NOT_ASKED`, `MISSING`, and `CONFLICT` never become empty/default values.
- `KNOWN` may carry false, zero, or empty only if the field's own type permits it; empty string is not accepted as a known non-empty text datum.
- `NOT_APPLICABLE` has no value.
- Provenance class and source refs are synthetically validated; real source-class allowlist and specialist review are outside this draft.
- No image-derived hidden-history or chemical inference fields are defined.

## 4. Candidate structure and validation ownership

Illustrative candidate:
```json
{
  "candidate_key": "CAND-MOCK-01",
  "rank": 1,
  "summary": "Synthetic placeholder only",
  "claims": [
    {
      "claim_ref": "CLAIM-MOCK-01",
      "claim_text": "Synthetic assertion only",
      "rule_ref": "RULE-MOCK-01",
      "evidence_refs": ["EVIDENCE-MOCK-01"],
      "support_status": "MOCK_SUPPORTED"
    }
  ],
  "constraint_checks": [
    {"constraint_ref": "CONSTRAINT-MOCK-01", "status": "PASS", "evidence_refs": ["EVIDENCE-MOCK-01"]}
  ],
  "conditions": [],
  "limitations": ["Synthetic fixture only"]
}
```

Validation split:
- Adapter: structural types, uniqueness, max-3, no forbidden keys, non-empty refs, referential presence against request context, blocked-state option suppression.
- Evidence/claim validator: scope applicability and review status. Evidence reference presence alone is not proof of applicability.
- Orchestrator: exact versions, current case/target/workflow/ledger checks, freshness and atomic publication.
- Policy/specialist authority: any substantive product, chemistry, safety, feasibility, or result rule.

Candidate hard constraints:
- Candidate must be withheld if any required check is `FAIL`, `UNKNOWN`, or absent.
- Global blocking state suppresses all candidates.
- Each candidate key unique within run; ranking values unique and contiguous 1..N, N≤3.
- Ranking must be deterministic under input permutation; ties resolved by stable candidate key only after substantive score/criteria tie.
- No padding to three.

## 5. Reason codes and state compatibility additions

Add `NO_VALID_OPTION` as a typed reason code for contract 0.3. It means evaluated constraints leave no candidate valid in the current synthetic run. It does not imply out-of-scope or missing evidence.

Compatibility requirements:
| Engine state | Consultation status | Reason(s) | Options |
|---|---|---|---|
| `SUGGESTION_REVIEWABLE` | `SYSTEM_REASONED_SUGGESTION` | no blocking reasons | 1–3, all validated |
| `CONDITIONAL_SUGGESTION` | `SYSTEM_REASONED_SUGGESTION` | no global blocker; candidate conditions explicit | 1–3, conditions structured |
| `NEEDS_MORE_INFORMATION` | `NEEDS_INFORMATION_OR_TEST` | `DATA_GAP`, `CONFLICTING_DATA`, or `KNOWLEDGE_GAP` when caller can resolve | 0 |
| `STOP_OR_REFER_WITH_REASON` | `NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW` | specialist-owned issue, `SAFETY_CONCERN`, or explicit review reason | 0 |
| `STOP_OR_REFER_WITH_REASON` | `SAFETY_STOP_NO_EXECUTION_SUGGESTION` | `SAFETY_CONCERN` | 0 |
| `STOP_OR_REFER_WITH_REASON` | `OUT_OF_V1_SCOPE` | `OUT_OF_SCOPE` only when formal boundary applies | 0 |
| `STOP_OR_REFER_WITH_REASON` | `NEEDS_INFORMATION_OR_TEST` | `NO_VALID_OPTION` with actionable missing/constraint explanation where caller can resolve | 0 |

`ENGINE_FAIL` remains transport/run failure, not a successful consultation response. It must be correlated to run/request and must not expose candidates.

## 6. Version and publication envelope (Orchestrator-facing; not engine authority)

Minimum freshness tuple to check at publication:
`case_ref + case_version + target_ref + target_version + policy_ref/version + evidence refs/versions + workflow_ref/version + ledger snapshot/version`.

Publication protocol draft:
1. Validate response against the immutable request snapshot.
2. Resolve external current versions and ledger/workflow status.
3. If any material dependency differs, mark run `STALE_SUPPRESSED`; publish nothing from this run.
4. Persist validated candidate(s) and assigned suggestion identity in one transaction or equivalent compare-and-swap boundary.
5. Commit audit/correlation record with run status.
6. Display only after commit succeeds.
7. Retry uses same idempotency key for same request; a new evaluation receives a new run identity.
8. Any failure between validation and commit yields no client-visible candidate. No stale fallback is implicit.

This is a service-boundary specification only; persistence/locking protocol must be implemented and separately tested.

## 7. Test exit checklist for the implementation phase

- [ ] operation-specific question required/forbidden validation
- [ ] typed provenance record states and value/state consistency
- [ ] duplicate candidate key and rank rejected
- [ ] rank permutation determinism, stable tie-break
- [ ] candidate claim evidence link present and request-resolved
- [ ] scope/review applicability delegated and blocks invalid claim
- [ ] hard constraint fail/unknown suppresses candidate
- [ ] max three; no padding
- [ ] S06 next-owner variants distinct, options empty
- [ ] S08 `NO_VALID_OPTION`, options empty
- [ ] full state/reason/status compatibility matrix
- [ ] current ledger exact suggestion ref/version check for question/rejection flows
- [ ] target/case dependency invalidation
- [ ] stop event and restart fresh reevaluation, no automatic resume
- [ ] stale publish suppressed on version race
- [ ] idempotent retry; failed persistence never leaks candidate
- [ ] engine exception and malformed response produce no current result
- [ ] forbidden execution/decision/workflow fields recursively rejected

## 8. Decisions not assumed by this spec

- Specialist's actual domain coverage and evidence approval.
- Product claim/rule catalogue or chemistry.
- Production database, deployment, access-control technology, retention, TTL, notifications, revocation/remediation policy.
- Pilot, customer data, or release authorization.

## 9. Next step without rework

The next implementation task is a bounded synthetic contract revision on the existing adapter branch: operation validation + typed `NO_VALID_OPTION` + state matrix and focused tests. The current adapter and fixtures must first be checked for existing behavior; only failing gaps are changed. Existing test coverage is preserved and not duplicated.


## 11. Source-level implementation comparison (Chat 3; no code changes)

This section records direct inspection of the existing master implementation added in PR #547, rather than repeating the earlier static audit. The inspected source is `app/hair_color/adapter.py`, its schema `tests/schemas/hair-color-adapter-0.2-draft.schema.json`, and tests `tests/test_hair_color_adapter.py`. No runtime files were modified.

### Verified existing behavior (retain; do not reimplement)
- Request envelope checks required fields, contract version, request/case identifiers, supported operation, positive integer case/target versions, mapping/array context types, and recursive prohibition of chemical-execution fields.
- Engine exceptions fail closed as `EngineExecutionFailure`; a response marked `ENGINE_FAIL` cannot be treated as a successful consultation.
- Response identity and case/target versions must match request; state/reason values are allow-listed; duplicate reasons/evidence refs and >3 options are rejected.
- Evidence refs must exist in the request evidence context; candidates are suppressed for blocked engine/consultation states and blocking reason codes.
- Decision/workflow fields and prohibited chemical instruction fields are recursively rejected; engine input/output are copied to avoid mutable aliasing.
- Synthetic adapter tests already cover S01–S15 boundary behaviors, including specialist-review suppression, stale version rejection, fresh reevaluation, and engine exception handling. Preserve these tests and avoid duplicates.

### Concrete remaining contract gaps (verified against source)
| Gap | Existing source behavior | Required next bounded change | Authority / blocker |
|---|---|---|---|
| Q01–Q02 operation-specific question | `ANSWER_QUESTION` is an allowed operation but `question` is not required or validated. Existing S11 test supplies it but does not test absent/blank question. | Add operation-conditioned validation and focused negative tests. | Synthetic contract implementation scope; no product rule needed. |
| Q03 question on non-question operation | Request envelope/schema permits additional properties; `question` is not rejected on other operations. | Enforce the agreed strict operation-field rule. | Contract decision recorded in Chat 1; confirm implementation gate. |
| C01 candidate identity | Candidate option objects are opaque; no candidate-key uniqueness or structure check. | Define minimal synthetic candidate envelope; validate unique local keys. | Keep candidate fields non-claiming and synthetic. |
| C02–C04 claim/evidence binding | Evidence is validated only at response-level; each candidate has no claim/evidence applicability structure. | Add candidate-local evidence links and structural checks only; do not claim scientific applicability. | Evidence-scope validator remains a separate owner and must not be simulated. |
| State/reason compatibility | Existing validator checks a broad blocking predicate, not a full compatibility matrix. | Add table-driven structural matrix tests; preserve suppression behavior. | Must match the already approved five response states and four engine states. |
| S08 typed no-option reason | S08 currently returns an empty option set with specialist-review status in test fixture; there is no typed `NO_VALID_OPTION` reason code. | Add synthetic typed reason and test empty-option invariants; do not conflate with out-of-scope or knowledge-gap. | Contract reason-code change; use prior PO decision record. |
| Publication freshness/atomicity | Adapter validates version equality at response time only; it has no authoritative store, ledger, dependency service, CAS, or publish transaction. | Keep publication freshness/concurrency in Orchestrator/service-boundary design; Adapter must not pretend to implement it. | Separate service architecture/implementation authorization required. |
| Schema strictness | Adapter schema uses `additionalProperties: true` and `oneOf` envelope shapes; candidate and context fields are opaque. | Tighten only the request operation conditionals and minimal candidate structure in a separately authorized schema change. | Existing schema/tests must be inspected and preserved. |

### Non-duplicative execution sequence for the remaining chats
1. **Chat 4:** Implement only the already-decided synthetic request/candidate contract gaps (Q01–Q03, candidate-key structure, S08 typed reason, compatibility matrix) if implementation authorization is explicit; otherwise prepare a minimal patch and test diff without committing runtime changes.
2. **Chat 5:** Focused tests and validation evidence for changed paths; review service boundary/publish freshness as design-only where runtime authority is absent; final closeout with explicit remaining blockers and no release/pilot claim.

**Scope warning:** Source inspection does not establish specialist validation, real product behavior, chemistry, or publication correctness. Existing synthetic tests are contract boundary checks only.


## 12. Chat 4 implementation delta — source verified (2026-11-23)

The current PR head now contains a synthetic Contract 0.3 implementation for the bounded request/state/S08 items previously listed as gaps. This is a source inspection update; CI runs for this head were still in progress when recorded.

| Gap | Current source status | Remaining boundary |
|---|---|---|
| Q01–Q02 question required/nonblank | Implemented in Adapter; focused tests cover missing, null, blank, and whitespace-only question. | Schema operation conditional also exists; retain draft-only status. |
| Q03 question fields on non-question operations | Implemented rejection for question and question_about; tests cover both. | No Orchestrator referent-currentness check is provided by Adapter. |
| S08 typed reason | NO_VALID_OPTION added to reason enum and S08 synthetic fixture response; options remain empty. | Only synthetic semantics; no real feasibility or chemistry implication. |
| State/reason/status checks | Compatibility checks added for suggestion, information-needed, stop/refer, safety, scope, and no-valid-option mappings. | Matrix still needs expanded exhaustive boundary tests and review for any permitted tuple not covered. |
| Candidate structure and uniqueness (C01) | Not implemented: option objects remain opaque; candidate keys/ranks are not validated. | Minimal non-claiming candidate envelope, unique key/rank and deterministic-order checks remain. |
| Candidate-local claim/evidence relations (C02–C04) | Not implemented: response evidence refs are validated globally, not per candidate/claim. | Structural candidate/claim linkage only; evidence applicability stays with separate validator. |
| Provenance typed records | Not implemented in Adapter schema/runtime. | Remains outside this bounded change unless separately authorized. |
| Publication freshness / atomicity | Not implemented in Adapter (correct ownership boundary). | Orchestrator/service design and implementation remain separate; no publication claim. |

**Verified head at inspection:** 40f8584408d8228e8dc58b0148c17f5f99d18780. PR #651 currently reports mergeable. HBI CI, HBI Auto Tasks, and HBI Pilot Browser Proof were running; no outcome is claimed here.


## 13. Chat 4 implementation delta — candidate envelope (synthetic only; tests pending)

The Adapter now validates a minimal candidate envelope instead of accepting opaque option objects:
- required candidate key, rank, neutral summary, and non-empty claim list;
- unique candidate keys and rank values;
- ranks must be contiguous and match option order (1..N), with N ≤ 3;
- every claim has non-empty claim/rule identifiers and text, a non-empty unique evidence-ref list resolved against request evidence context, and the synthetic-only support marker `MOCK_SUPPORTED`;
- malformed candidate or claim structures fail closed before a response is returned.

The draft JSON Schema was tightened to describe this structure. Focused synthetic tests were added for duplicate keys/ranks, rank-order mismatch, missing candidate/claim fields, empty claims, unresolved claim evidence, and non-synthetic support marker.

**Limits:** This is structural linkage only. It does not evaluate evidence relevance, scientific validity, rule applicability, constraint completeness, candidate scoring, or real-world safety/feasibility. Claim text and evidence in fixtures are placeholders. Tests/CI have not yet been observed to pass on this new head; Chat 5 must verify workflow results and inspect any failures before closure.

## 14. Final-chat runtime gate and implementation status

### Runtime entry point added
- `app/hair_color/consultation.py` exposes `run_consultation(request)`.
- It uses `PolicyGateEngine` and the Contract 0.3 Adapter.
- `app/hair_color/policy_gate_engine.py` implements deterministic intake routing for explicit safety concern, out-of-scope, stale snapshot, missing intake fields, conflicting fields, question requests, and complete intake without approved knowledge.
- It **never emits candidate options**. Complete intake alone does not unlock domain recommendations.

### Verified design boundary
This is an executable intake/triage consultation, not a specialist color consultation. The specialist-approved knowledge/evidence bundle and its validation are still missing; therefore the runtime defaults to KNOWLEDGE_GAP and referral when intake is otherwise complete. This is deliberate fail-closed behavior, not a claim of project completion for real color advice.

### Tests added
- Candidate claim evidence must be included in response-level evidence refs and supplied request context.
- Request evidence refs must be non-empty and unique.
- DATA_GAP must carry explicit missing-information items.
- Public entry-point and policy-gate synthetic tests cover safety, scope, stale version, missing data, conflict, questions, complete intake without approved knowledge, and non-mutation.

### Not approved / not implemented
- Real product/shade/chemical knowledge, specialist rules, formula or processing instructions, feasibility or result claims.
- Specialist validation, product-specific evidence registry, real client data, case store, authoritative ledger, consent/workflow ownership, orchestrator publication atomicity/freshness, pilot, release, merge.
- CI outcomes for the latest commits remain pending at the time of this section's recording.
