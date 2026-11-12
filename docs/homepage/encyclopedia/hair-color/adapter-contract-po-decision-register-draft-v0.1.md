# HBI Adapter Contract — PO Decision Register (Draft 0.1)

**Status:** PO decisions D-01–D-08 explicitly approved on 2026-11-12. Approval is limited to the documented meanings, design controls, and recommendations recorded below; it does not authorize implementation.  
**Scope:** documentation/design only. This register proposes defaults so review can be decisive and implementation does not invent semantics.

## 1. Decision principles already treated as binding

The following are existing project guardrails, not reopened decisions:

- Keep the four engine states, five consultation response states, and ten workflow states separate.
- Engine/Adapter cannot authoritatively create case versions, suggestion history, acceptance, execution consent, stop events, performed-step records, or workflow transitions.
- A question is not acceptance; acceptance is not execution consent.
- Rejection remains auditable and the rejected suggestion cannot return as active.
- A changed target requires a new evaluation version. Changed data invalidates only dependent outputs.
- After a client stop, automatic resume is prohibited; a restart request triggers fresh evaluation.
- Fail closed on safety stop, stale/mismatched versions, malformed output, material data conflict, or engine failure.
- `DATA_GAP`, `KNOWLEDGE_GAP`, and `ENGINE_FAIL` remain distinct.
- No chemical execution instruction capability is included in V1.
- Synthetic-only GitHub/CI fixtures; real customer data stays in the owner's offline local environment.
- No change to the 88-color catalogue.

## 2. Recommended wire identifiers

These identifiers are approved design-level names under D-01/D-02. They are not implemented runtime enums, and this approval does not authorize a runtime schema.

### 2.1 Four engine states

| Recommended identifier | Meaning | Recommendation |
|---|---|---|
| `SUGGESTION_REVIEWABLE` | Candidate suggestion can be reviewed | Keep |
| `CONDITIONAL_SUGGESTION` | Suggestion is valid only under explicit conditions | Keep |
| `NEEDS_MORE_INFORMATION` | Required data/test is missing or unresolved | Keep |
| `STOP_OR_REFER_WITH_REASON` | Current run must stop or refer with a reason | Keep |

### 2.2 Five consultation response states

| Recommended identifier | Meaning | Recommendation |
|---|---|---|
| `SYSTEM_REASONED_SUGGESTION` | System can provide a reasoned, evidence-bounded suggestion | Keep |
| `NEEDS_INFORMATION_OR_TEST` | Data or test is needed before a defensible suggestion | Keep |
| `NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW` | Remote assessment is insufficient | Keep |
| `SAFETY_STOP_NO_EXECUTION_SUGGESTION` | Safety concern blocks execution suggestion | Keep |
| `OUT_OF_V1_SCOPE` | Request cannot be answered within the approved V1 boundary | Keep |

**Important semantic boundary:** `KNOWLEDGE_GAP` is a reason code, not a sixth response state. When evidence is unavailable, the response must explicitly say that no reliable answer is available and withhold the dependent suggestion. Use `OUT_OF_V1_SCOPE` only when the requested claim/action is outside V1; do not use it as a generic synonym for every missing source.

## 3. Recommended reason-code registry

| Code | Use only when | Must not be conflated with |
|---|---|---|
| `DATA_GAP` | Required case data is absent/unknown/not asked | Knowledge or engine failure |
| `KNOWLEDGE_GAP` | Applicable reliable evidence/rule is unavailable | Missing client data |
| `ENGINE_FAIL` | Engine/retrieval/processing failed | A valid consultation outcome |
| `CONFLICTING_DATA` | Material sources disagree | Missing data |
| `SAFETY_CONCERN` | A safety constraint blocks the current path | General uncertainty |
| `OUT_OF_SCOPE` | Request is outside approved product scope | A generic evidence gap |
| `STALE_CASE_VERSION` | Evaluated snapshot no longer matches authoritative current version | A fresh valid evaluation |

Recommendation: preserve these as diagnostic codes separate from all state enums.

## 4. Knowledge-state representation

Recommendation: retain the six explicit values in Draft 0.2:

- `KNOWN`: a value is recorded and attributable to a source.
- `UNKNOWN`: the real-world value is not known.
- `NOT_ASKED`: the question has not been asked.
- `MISSING`: the field was expected but is absent from the supplied snapshot/request.
- `CONFLICT`: authoritative records disagree.
- `NOT_APPLICABLE`: the field does not apply.

Do not collapse `UNKNOWN`, `NOT_ASKED`, and `MISSING`. Do not represent an unknown safety answer as `false`. A value of false is valid only when explicitly recorded as a known value with provenance.

## 5. Canonical fixture-oracle mapping

The `expected_status` and `expected_action` labels in the README/JSON fixture manifest are test-oracle values. They are not wire enums. The exact oracle labels have been copied into Adapter Contract Draft 0.2.

The following mapping is a recommended interpretation, not a new test oracle:

| Scenario | Manifest oracle | Recommended engine state | Recommended response state | Reason |
|---|---|---|---|---|
| S01 | `SUGGESTION_REVIEWABLE` | `SUGGESTION_REVIEWABLE` | `SYSTEM_REASONED_SUGGESTION` | Complete case with applicable support |
| S02 | `DATA_GAP` | `NEEDS_MORE_INFORMATION` | `NEEDS_INFORMATION_OR_TEST` | Required history absent |
| S03 | `DATA_CONFLICT` | `NEEDS_MORE_INFORMATION` | `NEEDS_INFORMATION_OR_TEST` | Conflicting sources need resolution |
| S04 | `INSUFFICIENT_DATA` | `NEEDS_MORE_INFORMATION` | `NEEDS_INFORMATION_OR_TEST` | Image-only input cannot establish hidden facts |
| S05 | `PRODUCT_IDENTITY_UNRESOLVED` | `NEEDS_MORE_INFORMATION` | `NEEDS_INFORMATION_OR_TEST` | Exact product identity/scope absent |
| S06 | `KNOWLEDGE_GAP` | `STOP_OR_REFER_WITH_REASON` (provisional) | **Client-facing handling approved; wire mapping pending** | State that applicable reliable evidence is unavailable and withhold dependent output. Do not force `OUT_OF_V1_SCOPE` unless the requested claim/action is formally outside V1 |
| S07 | `SAFETY_STOP` | `STOP_OR_REFER_WITH_REASON` | `SAFETY_STOP_NO_EXECUTION_SUGGESTION` | Safety gate blocks options |
| S08 | `NOT_FEASIBLE_OR_UNVERIFIED` | `STOP_OR_REFER_WITH_REASON` (provisional) | **Client-facing handling approved; wire mapping pending** | State that no valid option exists under documented constraints and explain the supported reason; lack of a valid option does not itself mean the goal is outside V1 |
| S09 | `TWO_VALID_OPTIONS` | `SUGGESTION_REVIEWABLE` | `SYSTEM_REASONED_SUGGESTION` | Two options pass hard constraints |
| S10 | `ONE_VALID_OPTION` | `SUGGESTION_REVIEWABLE` | `SYSTEM_REASONED_SUGGESTION` | Exactly one option passes |
| S11 | `QUESTION_ANSWERED_DECISION_UNCHANGED` | `SUGGESTION_REVIEWABLE` | `SYSTEM_REASONED_SUGGESTION` | Explain existing suggestion; decision ledger unchanged |
| S12 | `SUGGESTION_REJECTED` | **No forced engine-state mapping** | **No forced response-state mapping** | Rejection is an authoritative ledger event, not inherently a data gap; evaluate any independent alternative in a separate fresh candidate run |
| S13 | `NEW_CASE_VERSION_REEVALUATION_REQUIRED` | Fresh evaluation | Determined by fresh evaluation | Version transition belongs to Orchestrator/Case Store |
| S14 | `CLIENT_REQUESTED_STOP` | Not an engine state | Not a consultation response | Workflow event owned by Workflow Engine |
| S15 | `ENGINE_FAIL` | Not a consultation state | Not a consultation response | Adapter failure envelope; no consultation result |



**S06/S08/S12 mapping caveat (updated 2026-11-12):** the PO has approved the client-facing handling for all three scenarios (Section 8.1). That approval does not, by itself, settle every wire-state mapping. Keep S12 as a ledger event with no forced engine/response state. For S06 and S08, retain the current provisional engine-state mappings and leave the exact S06/S08 response-state mapping unresolved under D-05, even though D-01/D-02 meanings and identifiers are approved; do not overload `OUT_OF_V1_SCOPE` or invent a sixth response state.

## 6. Adapter response and failure semantics

Recommendations:

1. Separate transport/adapter validation outcome from the consultation response.
2. If the engine fails, return a failure envelope with `consultation_result: null`, no options, and a correlation reference.
3. Do not make retryability a client-visible permission to reuse stale output.
4. Retry may be allowed only for transient technical failures and must use the same idempotency key for the same logical request. A retry must not create a new case version or duplicate decision events.
5. If the authoritative case/target version changes before response publication, suppress the result and return `STALE_CASE_VERSION`; reevaluate against the current snapshot instead of coercing the old response.
6. Never publish a previous successful response as the answer to a failed current run.

Suggested retry policy: transport timeout / temporary retrieval outage may be retryable; invalid request, unsupported contract, schema violation, version mismatch, safety stop, and evidence-scope mismatch are not automatically retryable. Retry policy and maximum attempts must be versioned configuration, not model discretion.

## 7. Data and evidence envelope

Recommended minimum datum envelope:

- `value` (nullable only when the knowledge state requires it);
- `knowledge_state`;
- `source_class`;
- `record_ref`;
- `recorded_at`;
- `observed_at` where relevant;
- `confidence` only where a defined measurement method exists; never use free-form model confidence as a substitute for evidence.

Recommended evidence reference fields:

- immutable `evidence_ref`;
- claim ID and exact claim text;
- publisher/source class;
- source URL or offline document locator;
- publication/revision date and version;
- exact product/material identity and market where applicable;
- precise passage/page/section;
- scope and limitations;
- review status, reviewer, review date, and re-review trigger;
- conflict links.

Only `VERIFIED_APPLICABLE` supports a rule within the exact reviewed scope. Other statuses remain non-authoritative for rule activation.

## 8. PO review queue — decision items, not implementation blockers to duplicate

| ID | Recommended disposition | Why |
|---|---|---|
| D-01 | **APPROVED 2026-11-12** — accept the four engine-state meanings and proposed identifiers in Section 2.1 | Preserves the four-state model; design approval only |
| D-02 | **APPROVED 2026-11-12** — accept the five consultation response meanings and proposed identifiers in Section 2.2 | Preserves the five-state model; no sixth response state |
| D-03 | **APPROVED 2026-11-12** — accept the six knowledge states and definitions in Section 4 | Prevents false/unknown/missing collapse |
| D-04 | **APPROVED 2026-11-12** — keep diagnostic reason codes separate from engine, response, and workflow states | Prevents semantic overloading |
| D-05 | **APPROVED 2026-11-12** — S01–S15 labels are test oracles only, not wire enums; S06/S08 response mapping remains unresolved and S12 remains a ledger event | Prevents fixture labels from being mistaken for wire enums |
| D-06 | **APPROVED 2026-11-12** — accept the failure-envelope, stale-output suppression, and idempotent retry semantics in Section 6 | Prevents stale output and duplicate case events |
| D-07 | **APPROVED 2026-11-12** — accept minimum datum provenance and evidence-reference requirements in Section 7; free-form model confidence is not evidence | Enables auditable exact-scope evidence use |
| D-08 | **APPROVED 2026-11-12:** S06 explicitly reports unavailable applicable evidence and withholds dependent output; S08 explicitly reports no valid option under current constraints and invents no substitute; S12 remains a rejection/ledger event with no forced engine/response state, and any independent alternative requires a fresh candidate run | Explicit PO approval; see decision record below |

### 8.2 Recorded PO approval — D-01 through D-07 (2026-11-12)

The Product Owner explicitly approved all seven recommendations:

1. **D-01 — engine states:** approve the four meanings and proposed identifiers in Section 2.1.
2. **D-02 — consultation response states:** approve the five meanings and proposed identifiers in Section 2.2. No sixth response state is created.
3. **D-03 — knowledge states:** approve the six distinct values in Section 4. Unknown, not asked, and missing remain distinct; an unknown safety answer is never coerced to false.
4. **D-04 — reason-code separation:** approve keeping diagnostic reason codes distinct from all state layers, including data gap, knowledge gap, conflict, safety, scope, stale version, and engine failure.
5. **D-05 — fixture-oracle boundary:** approve S01–S15 labels as test expectations only, not wire enums. S06/S08 response mapping remains unresolved rather than inferred; S12 remains a ledger event with no forced engine/response state.
6. **D-06 — failure and retry semantics:** approve the conceptual failure envelope, publication-time stale-output suppression, and idempotent retry constraints in Section 6.
7. **D-07 — provenance/evidence envelope:** approve the minimum provenance and evidence-reference requirements in Section 7; free-form model confidence is not evidence.

Together with Section 8.1, D-01–D-08 are now approved at the documentation/design level. This does **not** approve runtime schemas, code, adapter implementation, engine integration, product behavior, pilot, release, or merge. The unresolved S06/S08 response mapping is deliberately retained under D-05.

### 8.1 Recorded PO approval — 2026-11-12

The Product Owner approved all three decisions below:

1. **S06 / D-08:** Report that no reliable applicable evidence is available; withhold dependent output; do not guess or misuse `OUT_OF_V1_SCOPE`. Specialist referral is appropriate only when independently justified.
2. **S08 / D-08:** Report that no valid option exists under the current documented constraints, explain the supported reason, and do not invent a substitute. A distinct fresh evaluation may assess an independent alternative only if it passes all hard constraints.
3. **S12 / D-08:** Record the exact rejected suggestion/version in the authoritative ledger and exclude it from active options. Do not force an engine or response state. Any independent alternative requires a fresh candidate run; otherwise explain that no valid alternative is available.

These approvals resolve the S06, S08, and S12 presentation/ledger decisions. D-01–D-07 are separately approved in Section 8.2. No approval authorizes runtime schemas, implementation, pilot, release, or merge.



## 9. Work that can proceed without changing product authority

- Static consistency audit of Draft 0.2, README manifest, fixture JSON, JSON Schema, and runner assertions.
- Documentation corrections and synthetic-only tests for contract integrity.
- Exact-head CI verification and PR evidence updates.
- A traceability matrix linking every wire field to its owner, source, and validation rule.

## 10. Explicit stop line

This register does not authorize runtime JSON Schema changes, adapter stub, engine integration, product behavior, chemical instructions, customer-data processing in cloud, catalogue changes, pilot, release, or PR merge. Those remain outside the current authorized scope.
