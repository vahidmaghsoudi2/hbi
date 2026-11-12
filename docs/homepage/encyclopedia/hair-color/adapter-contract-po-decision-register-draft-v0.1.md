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
- Synthetic-only data in every environment for the current version; no real customer data may be processed or retained, including in an offline local environment.
- No change to the 88-color catalogue.

## 2. PO-approved design-level identifiers (D-01/D-02)

These identifiers are approved design-level names under D-01/D-02. They are not implemented runtime enums, and this approval does not authorize a runtime schema.

### 2.1 Four engine states — design identifiers approved

| Approved design identifier | Meaning | PO disposition |
|---|---|---|
| `SUGGESTION_REVIEWABLE` | Candidate suggestion can be reviewed | Keep |
| `CONDITIONAL_SUGGESTION` | Suggestion is valid only under explicit conditions | Keep |
| `NEEDS_MORE_INFORMATION` | Required data/test is missing or unresolved | Keep |
| `STOP_OR_REFER_WITH_REASON` | Current run must stop or refer with a reason | Keep |

### 2.2 Five consultation response states — design identifiers approved

| Recommended identifier | Meaning | Recommendation |
|---|---|---|
| `SYSTEM_REASONED_SUGGESTION` | System can provide a reasoned, evidence-bounded suggestion | Keep |
| `NEEDS_INFORMATION_OR_TEST` | Data or test is needed before a defensible suggestion | Keep |
| `NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW` | Remote assessment is insufficient | Keep |
| `SAFETY_STOP_NO_EXECUTION_SUGGESTION` | Safety concern blocks execution suggestion | Keep |
| `OUT_OF_V1_SCOPE` | Request cannot be answered within the approved V1 boundary | Keep |

**Important semantic boundary:** `KNOWLEDGE_GAP` is a reason code, not a sixth response state. When evidence is unavailable, the response must explicitly say that no reliable answer is available and withhold the dependent suggestion. Use `OUT_OF_V1_SCOPE` only when the requested claim/action is outside V1; do not use it as a generic synonym for every missing source.

## 3. PO-approved reason-code separation (D-04)

| Code | Use only when | Must not be conflated with |
|---|---|---|
| `DATA_GAP` | Required case data is absent/unknown/not asked | Knowledge or engine failure |
| `KNOWLEDGE_GAP` | Applicable reliable evidence/rule is unavailable | Missing client data |
| `ENGINE_FAIL` | Engine/retrieval/processing failed | A valid consultation outcome |
| `CONFLICTING_DATA` | Material sources disagree | Missing data |
| `SAFETY_CONCERN` | A safety constraint blocks the current path | General uncertainty |
| `OUT_OF_SCOPE` | Request is outside approved product scope | A generic evidence gap |
| `STALE_CASE_VERSION` | Evaluated snapshot no longer matches authoritative current version | A fresh valid evaluation |

PO approval: preserve these as diagnostic codes separate from all state enums.

**Naming boundary:** `OUT_OF_SCOPE` is the diagnostic reason code in this registry; `OUT_OF_V1_SCOPE` is the approved consultation-response identifier. They serve different layers and must not be substituted for one another. A mapping between them is allowed only when the request is demonstrably outside the approved V1 boundary.


## 4. Knowledge-state representation — approved (D-03)

PO approval: retain the six explicit values in Draft 0.2:

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

## 6. Adapter response and failure semantics — approved design invariants (D-06)

PO-approved conceptual rules:

1. Separate transport/adapter validation outcome from the consultation response.
2. If the engine fails, return a failure envelope with `consultation_result: null`, no options, and a correlation reference.
3. Do not make retryability a client-visible permission to reuse stale output.
4. Retry may be allowed only for transient technical failures and must use the same idempotency key for the same logical request. A retry must not create a new case version or duplicate decision events.
5. If the authoritative case/target version changes before response publication, suppress the result and return `STALE_CASE_VERSION`; reevaluate against the current snapshot instead of coercing the old response.
6. Never publish a previous successful response as the answer to a failed current run.

Suggested retry policy: transport timeout / temporary retrieval outage may be retryable; invalid request, unsupported contract, schema violation, version mismatch, safety stop, and evidence-scope mismatch are not automatically retryable. Retry policy and maximum attempts must be versioned configuration, not model discretion.

## 7. Data and evidence envelope — approved minimum (D-07)

PO-approved minimum datum envelope:

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


### 6.1 Static audit follow-up — unresolved protocol details (2026-11-12)

A cross-check of D-06 against the current Adapter Contract Draft 0.2 and synthetic fixtures S11–S15 confirmed the approved invariants but identified details that are not yet defined. These remain open; this note does not add a new PO decision:

- The request contract has no normative `idempotency_key` field or definition of logical-request scope, uniqueness, retention, or retry-versus-new-evaluation distinction.
- The Orchestrator is responsible for publication, but no atomic compare-and-publish/current-version gate is specified for the authoritative `(case_version, target_version)` pair.
- Request and response examples carry case/target versions, but the normative equality/binding rule and target-only-change behavior are not fully specified.
- S11 prose requires authoritative ledger validation before display; the fixture does not assert active/not-rejected status at publication. S12 asserts rejection behavior but does not carry a concrete suggestion reference/version tuple.
- S15 requires suppression of stale output for the failed run, but exact run/correlation scope and the distinction between suppressing publication and retaining historical audit records are unspecified.
- Retryable failure classification and maximum attempts remain versioned-configuration decisions, as already stated in Section 6; the illustrative `retryable` boolean is not a complete protocol.

The detailed scenario-by-scenario traceability and the single `source` → `source_class` example correction are recorded in Section 7.1 of `adapter-contract-draft-v0.2.md`. The decision register remains a draft record; no runtime schema, engine behavior, or implementation authorization follows from this audit.


### 6.2 Static audit — suggestion ledger and version traceability (2026-11-12)

Cross-check of the approved PO rules against the Adapter Contract, README scenario definitions, and S11–S13 machine fixtures:

- **Confirmed:** Orchestrator/Case Store and the authoritative ledger own persistent suggestion references and active/rejected status. The engine cannot mint or reactivate a suggestion. Rejection remains auditable and excludes the exact rejected suggestion/version. An independent alternative requires a fresh candidate run.
- **S11 gap:** the README and illustrative response identify an existing V1 suggestion, but the machine fixture does not contain a structured suggestion reference/version or assert that the ledger still marks it active and not rejected immediately before display.
- **S12 gap:** the README identifies the exact synthetic suggestion/version, while the machine fixture stores only a descriptive input profile and generic rejection assertions; no structured target reference/version or before/after ledger state is present.
- **S13 gap:** the README describes CASE-V1 to CASE-V2, but the machine fixture does not bind an explicit prior/new case-version and target-version pair.
- **Open design detail:** the contract has not yet defined the normative ledger reference tuple binding a suggestion to case/target version, evaluation run, and decision events, nor a time-based expiry/revalidation policy. No TTL or new field is approved by this audit.

Conclusion: no contradiction with D-08/S12 or other recorded PO decisions was found. The gap is machine-readable traceability and unresolved protocol detail, not a reason to alter the approved rejection semantics. Fixture/schema/runner changes are deferred pending a separately reviewed proposal and explicit approval where policy is involved. See Section 7.2 of `adapter-contract-draft-v0.2.md`.


### 6.3 Static audit — field ownership and provenance across JSON examples (2026-11-12)

A static review of all six illustrative examples (S01, S02, S07, S11, S14, S15) was completed against the Section 1 authority principles and D-07.

- **S01:** Orchestrator/Case Store owns request/case/version identifiers; product and evidence registries own product identity, document references, evidence status, and scope matching; policy source owns policy version/constraints. The two known case data items include the D-07 minimum `source_class`, `record_ref`, and `recorded_at`. The `NOT_ASKED` safety item does not invent a value/source. Mock evidence is not a complete evidence record; opaque product/evidence references require trusted external resolution.
- **S02:** request/case/version values are trusted identifiers echoed and validated by the Adapter. Consultation state, explanation, missing-field reason, limitations, and next-step proposal may be engine-produced. The `accepted_sources` list must be constrained by trusted policy, not invented by the engine.
- **S07:** safety-alert and evidence references must resolve against trusted records. The engine may produce a reasoned stop/explanation proposal but cannot mint the referenced alert or evidence identity.
- **S11:** ledger identity/version/status and evidence references are trusted read-only fields; explanatory text may be engine-produced. The example's Orchestrator-composed ownership note is consistent. Existing fixture traceability gaps remain as recorded in Section 6.2.
- **S14:** the event is Workflow Engine-owned. Event/case identifiers and recorded time are service-generated; actor attribution must come from authenticated interaction context; workflow action and no-auto-resume behavior are Workflow Engine-controlled.
- **S15:** request identity is Orchestrator-owned; failure/correlation telemetry is Adapter/observability-owned; stale-output publication outcome is controlled by the Orchestrator publication gate. These must not be trusted as model-authored fields.

**D-07 boundary:** no new mandatory `recorded_by` field is introduced. The S01/S07 mock evidence references are placeholders and do not satisfy the full recommended evidence-reference metadata. Exact product/evidence resolution remains external to the model. The examples do not themselves prove scientific applicability.

**Conclusion:** no direct contradiction was found, but ownership for S01–S02, S07, and S15 had been implicit. This audit makes the intended ownership explicit in Adapter Contract Draft 0.2, Section 9.7. It does not change JSON, fixtures, schema, runner, tests, runtime interfaces, product behavior, or any PO decision. Existing open protocol and S11–S13 traceability issues remain open.

### 6.4 Static audit — evidence validity, scope, and citation traceability (2026-11-12)

A static review of all six illustrative examples (S01, S02, S07, S11, S14, S15) against D-07 and the evidence-ownership rules found:

- S01's `DOC-MOCK-A` is test-only. Its `scope_match: true` and `PRODUCT-ID-A` / `EXACT_MATCH` values are synthetic placeholders, not proof of scientific applicability or verified product identity.
- S02's empty `evidence_refs` is appropriate for a data-gap response; `accepted_sources` must remain a trusted policy allowlist, not model-authored evidence.
- S07's mock safety/evidence tokens require resolution against trusted safety/evidence records and provide no scientific support by themselves.
- S11's `EVIDENCE-MOCK-A` is not support for the existing suggestion; the Orchestrator must resolve the ledger entry and every material evidence reference before display.
- S14 is a workflow event, not an evidence claim. S15 correlation/failure telemetry is operational traceability, not scientific evidence.

No example contains a complete, independently checkable evidence citation (claim, publisher/source class, locator, version/date, exact passage, scope, and review status). Only `VERIFIED_APPLICABLE` may support a rule within its exact reviewed scope. A reference identifier, a positive scope flag, or an exact-identity label cannot replace trusted registry resolution. Product identity and claim-level evidence applicability are separate checks.

Conclusion: the examples are structurally illustrative only; none of their mock references is scientific evidence. No JSON, fixture, schema, runner, test, runtime behavior, new evidence field, TTL, review policy, or PO decision was added. See Adapter Contract Draft 0.2, Section 9.8. External evidence verification remains a separate prerequisite.

### 6.5 Static audit — evidence-status vocabulary consistency (2026-11-12)

Cross-document comparison found the six README/D-07 evidence statuses semantically consistent with the Adapter Contract and the D-07 rule-activation boundary. `VERIFIED_APPLICABLE` alone supports a rule within its exact reviewed scope. `PARTIALLY_SUPPORTED` may support only a limited, non-prescriptive explanation of the portion actually supported; this does not activate a rule. `CONFLICTING` blocks operational use while unresolved; `NOT_APPLICABLE` means the source does not match the claim's subject/scope; `UNVERIFIED` means identity/documentation/review is insufficient; `OUTDATED` means the source is not current for the assessment.

Open details, not settled by this audit: status granularity (source vs source–claim vs product/market/version assessment); independent treatment of multiple claims/passages in one document; versioning and propagation of status changes/review/conflicts/supersession; and coexistence of different statuses across scopes. No precedence, automatic transition, expiry, or review timing is inferred. No evidence status was assigned or changed, and no source was externally verified. No fixture/schema/runner/runtime or PO policy decision changed. See Adapter Contract Draft 0.2, Section 9.9.

### 6.6 Static audit — evidence-status impact on dependent suggestions (2026-11-12)

The current approved boundaries establish dependency-aware withholding but do not yet define a complete evidence-to-suggestion dependency protocol.

Confirmed: a changed datum invalidates only dependent outputs; material claims without applicable traceable evidence cannot support an executable suggestion; S06 withholds knowledge-dependent output; S13 requires fresh evaluation and dependent-output rechecking after target change; S15 suppresses failed-run and stale output. Evidence status must be evaluated at claim/scope level, not blanket-applied to every claim in a document or every suggestion in a case.

Conservative impact interpretation: `VERIFIED_APPLICABLE` may enter evaluation but does not approve a suggestion by itself; `PARTIALLY_SUPPORTED` cannot support unsupported portions or an operational rule; `CONFLICTING`, `NOT_APPLICABLE`, `UNVERIFIED`, and `OUTDATED` cannot support the affected claim, so dependent suggestions must be withheld unless other independently applicable evidence supports a fresh evaluation. This is an interpretation of existing boundaries, not a newly approved transition policy.

Open protocol details: normative claim→evidence→candidate→suggestion/version→case/target/run linkage; affected-output computation for shared or multi-source dependencies; authoritative status-revision detection and synchronization with publication gate; revalidation and event handling for already displayed/accepted suggestions; and status transition/precedence/expiry policy. No graph, field, automatic transition, TTL, or review cadence is approved or inferred. No source/status was changed or externally verified; no fixtures/schema/runner/tests/runtime or PO decision changed. See Adapter Contract Draft 0.2, Section 9.10.

### 6.7 Static audit — evidence validity against client decisions and workflow events (2026-11-12)

The cross-check found no contradiction among the approved decision boundaries, but identified missing protocol detail when evidence validity changes after a client event.

Confirmed: S11 questions do not change acceptance or execution consent; acceptance is not execution consent; rejection remains auditable and the exact rejected suggestion/version cannot reactivate; stop blocks automatic continuation; restart requires fresh evaluation; a new target/case version does not inherit acceptance, consent, or specialist review. None of these client events can make invalid or non-applicable evidence authoritative, and evidence availability cannot create client consent.

Conservative boundary: if a material evidence dependency is no longer applicable before a pending service step, the dependent suggestion/output must not be treated as currently supported. Preserve the historical client decision events; do not silently erase, rewrite, or infer their revocation. A fresh evaluation must use current evidence. This does not decide whether prior acceptance/consent is suspended, renewed, superseded, or requires client reconfirmation.

Open details: event ordering/atomicity between evidence-status revision, acceptance/consent, stop and publication; invalidation when evidence changes without case/target version change; ledger representation preserving historical decisions while blocking unsupported use; notification/reconfirmation policy; treatment/remediation of already displayed or partially performed workflows; and missing combined fixture coverage for evidence revision after acceptance, after rejection, and before/after stop/restart. No automatic revocation, re-consent, notification, rollback, TTL, or workflow state is approved or inferred. No fixture/schema/runner/tests/runtime or PO decision changed. See Adapter Contract Draft 0.2, Section 9.11.

### 6.8 Static audit — event ordering, concurrency, and stale publication races (2026-11-12)

Confirmed authority boundaries: Case Store/Orchestrator owns case/target versions; the authoritative evidence source owns evidence status; the decision ledger owns client decision history; Workflow Engine owns stop/restart and performed-step history; Orchestrator decides publication. Engine/Adapter output alone cannot establish that these records are still current.

Conservative conclusions: (a) evidence revised after evaluation but before publication makes dependent output ineligible until fresh evaluation; (b) acceptance/consent cannot override evidence validity and historical decisions must remain auditable; (c) a stopped workflow must not be continued by an old run; (d) restart requires fresh evaluation and a delayed response from the old run must not be substituted; (e) retries of the same logical request retain D-06 idempotency constraints.

Unresolved: event linearization/order; atomic compare-and-publish across case/target, evidence, ledger, and workflow state; event sequence/version and out-of-order delivery; exact run identity across stop/restart; idempotency key representation/scope/retention; and handling of already displayed or partly acted-on results after later revisions. No timestamp precedence, lock/transaction strategy, new field/state, automatic revocation, notification, reconfirmation, rollback, or remediation policy is approved or inferred. No fixture/schema/runner/tests/runtime or PO decision changed. See Adapter Contract Draft 0.2, Section 9.12.

### 6.9 Proposed publication-gate design — review only (2026-11-12)

This is a design proposal derived from the Section 6.8 concurrency audit; it is not an approved protocol.

**Separate gates:** (1) advice publication and (2) service authorization. Publishing advice must not imply client acceptance, execution consent, or performed service.

**Logical publication preconditions:** current case/target context; currently applicable material evidence dependencies; same eligible suggestion/version in the authoritative ledger; non-stopped/non-superseded workflow path; response belongs to the current run; and no failed-current-run fallback. Any failed, unavailable, or conflicting required check withholds affected output.

**Concurrency requirement:** all required checks and the publish decision need one logical linearization point. Independent reads followed by an unprotected write leave a time-of-check/time-of-use race. Engineering options are (A) a serialized authoritative Orchestrator boundary, (B) conditional commit across authoritative stores if equivalent atomicity can be demonstrated, or (C) snapshot reads followed by ordinary publish. Option C alone is insufficient. Working recommendation: approve the logical compare-and-publish requirement for architecture review, then evaluate A against the actual topology; no implementation mechanism is selected or approved.

Open technical details: dependency invalidation without case/target version changes; stop/restart run boundary; event identity and idempotency/deduplication scope; audit of suppressed publication; and fail-closed behavior when authorities are unavailable or conflicting. No field names, event IDs, counters, timestamps, TTLs, retry limits, locks, transaction APIs, or states are proposed.

PO policy remains separate: notification/reconfirmation/suspension after evidence revision and remediation of partly performed work are not decided. Eight synthetic test objectives are listed in Adapter Contract Section 9.13; none has been added to fixtures. No PO decision, schema, fixture, runner, test, runtime, or product behavior changed. No implementation/pilot/release/merge authorization is created.

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


### 6.10 Consolidated field ownership and traceability matrix (2026-11-12)

Adapter Contract Draft 0.2 Section 9.14 consolidates field-family ownership, producer/transport boundaries, validation authority, and missing/conflict/stale handling.

- The matrix explicitly separates source-of-truth ownership from data entry, transport, echo, validation, and publication.
- Confirmed conceptual boundaries include: Case Store/Orchestrator for case identity and versions; trusted policy source for `accepted_sources`; authoritative evidence source for evidence identity/scope/status; Orchestrator/Case Store/decision ledger for persistent suggestion identity and client decision history; Workflow Engine for stop/restart and performed-step history; Adapter/observability for failure envelope/telemetry; and Orchestrator for publication outcome.
- Exact product/evidence/safety registry deployments, authenticated event protocol, evidence dependency graph, idempotency key protocol, atomic compare-and-publish mechanism, and cross-source audit protocol remain proposed or unresolved as explicitly labeled.
- The table introduces no runtime fields, enums, schema, database/API, fixture changes, tests, policy transitions, TTL, retry limit, or implementation mechanism. It does not change D-01–D-08 or grant implementation/pilot/release/merge authorization.
- This is a documentation-only consolidation; no customer data, scientific evidence status, product behavior, fixture, schema, runner, or test changed.


### 6.11 Proposed S11–S13 machine-traceability model — review only (2026-11-12)

Adapter Contract Draft 0.2 Section 9.15 converts the previously identified gaps into a reviewable conceptual linkage proposal; it is not an approved wire schema.

- **Shared relationship:** persistent suggestion identity/version must be traceable to authoritative case identity, case/target versions, the evaluation run, relevant decision-ledger history, and material evidence/dependency context. This is a conceptual tuple only; no literal field names or event schema are approved.
- **S11:** before answering about an existing suggestion, Orchestrator resolves the authoritative suggestion/ledger relationship against current case/target context and verifies eligibility for display. Question/answer history remains separate from acceptance and execution consent.
- **S12:** rejection must identify the exact persistent suggestion/version in its case/target context; the ledger preserves the historical rejection and excludes that exact version from active options. Any alternative requires a fresh candidate evaluation.
- **S13:** the prior and new case/target versions must be distinguishable; dependency-based re-evaluation applies to affected outputs, while independent data is preserved. Prior acceptance, consent, specialist review, and suggestions do not automatically transfer.
- **Future synthetic coverage:** S11 pre-display ledger eligibility; S12 exact-version before/after ledger state; S13 explicit prior/new case-target pair and dependency outcomes; cross-scenario mismatch/stale-reference rejection. No fixture or schema change was made.
- **Still unresolved:** literal fields/nullability, ledger event/reference structure, run identity/correlation, dependency representation, eligibility vocabulary, publication-time version equality, expiry/revalidation, and atomic cross-authority publication. No TTL, automatic transition, notification, revocation, or retry rule is inferred.

This proposal does not alter D-01–D-08 or the approved S12 rejection semantics. It grants no implementation, pilot, release, or merge authorization. Fixture, schema, runner, tests, and product behavior remain unchanged.


### 6.12 S11–S13 traceability-gap closure sequence (2026-11-12)

Adapter Contract Draft 0.2 Section 9.16 classifies the remaining S11–S13 traceability gaps by decision authority, closure evidence, and dependency order.

- Contract-design work must follow confirmed source-of-truth ownership; it must not begin by guessing JSON properties or nullability.
- Ledger identity/event semantics, evaluation-run correlation, and evidence dependencies require explicit architecture definitions and synthetic counterexamples.
- Publication eligibility and cross-authority consistency require a topology-backed design; a successful CI run alone does not establish atomic publication safety.
- Evidence changes after acceptance/consent, expiry/revalidation, notification/reconfirmation, and partly performed work remain PO policy questions. No policy outcome is inferred.
- A wire-contract/schema proposal is a later, separate review gate. Approval of documentation or a schema proposal would not itself authorize implementation.

This is a planning/traceability clarification only. It does not change D-01–D-08, add a PO decision, close any unresolved item, change fixtures/schema/runner/tests, or authorize runtime implementation, pilot, release, or merge. PR #535 remains Draft and unmerged.


### 6.13 Decision-ledger identity and event semantics — cross-reference (2026-11-12)

Adapter Contract Draft 0.2 Section 9.17 separates persistent suggestion identity, suggestion version, evaluation-run identity, and decision-event identity, and distinguishes question, rejection, acceptance, explicit execution consent, and workflow stop.

The section records existing approved boundaries without creating a new PO decision:
- S11 questions do not mutate acceptance or execution consent.
- S12 rejection remains auditable and excludes the exact rejected suggestion/version from active options; it does not force a consultation state or authorize a replacement.
- Acceptance remains distinct from explicit execution consent.
- Stop/performed-step history remains under Workflow Engine authority.
- Engine-local candidate content and echoed references cannot substitute for authoritative persistent identity or ledger history.

Literal identifiers, event payloads, authentication, idempotency/deduplication, event ordering, retention, cross-store atomicity, expiry/revalidation, and post-consent evidence-change policy remain unresolved under Section 9.16. This cross-reference does not add a PO decision, close an open issue, change fixture/schema/runner/tests, or authorize implementation, pilot, release, or merge.

### 6.14 S11/S12 reference-sequence boundaries — cross-reference (2026-11-12)

Adapter Contract Draft 0.2 Section 9.18 records separate conceptual sequences for an explanatory question (S11) and rejection of an exact suggestion version (S12).

- **S11:** resolve the existing suggestion/version and its case/target, ledger, and material evidence relationships before explanation. A question does not alter acceptance, rejection, execution consent, workflow state, suggestion version, or evaluation history merely by being asked.
- **S12:** preserve the rejection against the exact persistent suggestion/version and exclude that version from active options. Rejection does not force an engine/response/workflow state or create a replacement. An independent alternative requires a fresh candidate evaluation; otherwise no alternative is invented.
- The examples are conceptual, not executable protocol or ledger schema. They do not define event names, payloads, identifiers, ordering, authentication, or storage behavior.
- Duplicate delivery/retry and a repeated intentional client action remain distinct but unresolved cases; no deduplication or idempotency mechanism is inferred.

No new PO decision is proposed or recorded. No fixture, schema, runner, test, runtime interface, or product behavior changed. Existing S12 approval and D-01–D-08 remain unchanged. No implementation, pilot, release, or merge authorization is created.


### 6.15 Static audit — complete fixture assertion enforcement (2026-11-12)

Adapter Contract Draft 0.2 Section 9.19 records the assertion-coverage audit and its limited remediation:

- 15 synthetic fixtures declare 48 assertions; the README-embedded and external JSON manifests are identical.
- The prior runner required 11 named assertions. The runner now requires all 48 scenario-specific assertions and rejects duplicate assertion entries.
- Unit tests exercise omission of every declared assertion and duplicate-entry rejection.
- This strengthens manifest/oracle integrity only. It does not execute product behavior, establish that assertions are scientifically or operationally true, or close S11–S13 identity/ledger/version/publication gaps.
- No PO decision, product runtime, adapter, engine, API, DB, UI, real-customer data, catalogue, scientific evidence status, or product behavior changed. All 15 product-behavior scenarios remain BLOCKED; no implementation, pilot, release, or merge authorization is created.


### 6.16 S13 target-change reference sequence — cross-reference (2026-11-12)

Adapter Contract Draft 0.2 Section 9.20 records a conceptual sequence for target changes and prior/new version lineage:

- Resolve the authoritative prior case/target context and the explicit changed goal; do not infer either from response text or a run-local candidate.
- Preserve a traceable prior/new case-target relationship; unresolved or mismatched lineage blocks dependent output from being treated as current.
- Re-evaluate affected dependencies and preserve independent data only where independence is established by authoritative dependency information. Unknown impact is not proof of independence.
- Keep prior-target suggestions and delayed prior-run responses historical; they cannot be reused as current for the new target.
- Prior acceptance, explicit execution consent, specialist review, and suggestion eligibility do not automatically transfer; historical decisions remain auditable.
- The section supplies future negative-test objectives but does not modify the S13 fixture, its four assertions, schema, runner, or tests. It does not define version IDs, dependency fields, events, ordering, atomic publication, notification, reconfirmation, rollback, or remediation.

This is a conceptual clarification of existing S13/PO boundaries, not a new PO decision or wire contract. No implementation, pilot, release, or merge authorization is created.

### 6.17 Claim-to-candidate evidence chain — conceptual cross-reference (2026-11-12)

Adapter Contract Draft 0.2 Section 9.21 clarifies the review chain from a bounded material claim, to its exact supporting evidence passage, to the reviewed rule within that evidence scope, and then to the candidate component/rationale that depends on the rule.

- A source reference or document-level status alone does not prove that a particular claim is supported.
- VERIFIED_APPLICABLE supports a rule only within its exact reviewed scope. PARTIALLY_SUPPORTED remains limited to non-prescriptive explanation of the supported portion; it does not activate an operational rule.
- A candidate with an unresolved material dependency is not presumed independent. If a supported component cannot be separated from an unsupported dependency, withhold the candidate.
- The clarification does not define fields, identifiers, graph representation, multi-source aggregation, status-change propagation, fixture assertions, or publication mechanics. Those remain open under Adapter Contract Sections 9.9, 9.10, and 9.14–9.16.

This is not a new PO decision, evidence approval, wire contract, or implementation authorization. No fixture, schema, runner, test, runtime, product behavior, pilot, release, or merge authorization changed.