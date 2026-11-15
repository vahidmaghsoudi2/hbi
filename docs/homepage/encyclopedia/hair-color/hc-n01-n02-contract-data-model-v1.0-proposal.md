# HBI Hair Consultation — HC-N01 / HC-N02 Contract and Case Data Model v1.0

- **Status:** consolidated HC-N01/N02 design baseline. Conditional mappings below resolve the approved client-facing behavior without inventing states; no runtime implementation or release authorization is implied.
- **Work items:** HC-N01 (consultation/adapter contract), HC-N02 (case data model and traceability).
- **Input baseline:** current `master` at `103d81d0d59b8a7b025ee51f48d83a447e1665c3`; approved README contract/workflow; Adapter Contract Draft 0.2 and D-01–D-08; synthetic fixture contract S01–S15; current synthetic Adapter and dialogue state machine.
- **Authority:** this document consolidates accepted semantics and proposes the minimum explicit data structures needed to implement them. It does not silently promote unresolved PO decisions.
- **Data policy:** PO-66-09 — synthetic data only in every environment. No real customer data, including local/offline development.
- **Non-authorization:** no production database, real-customer persistence, chemistry/rules activation, client-facing recommendation, pilot, deployment, release, or merge authorization is created by this proposal.

## 1. Executive decision

HC-N01 and HC-N02 must be treated as one boundary: the contract defines what a consultation engine may receive and return; the case model defines which service owns the authoritative facts, versions, decisions, evidence lineage, and workflow history around that exchange.

The engine is a **stateless evaluator**. It does not own the case, create authoritative identifiers, mutate workflow, record client decisions, grant execution permission, or persist service activity. The Orchestrator assembles a versioned request from authoritative sources, the Adapter validates the boundary, and the Orchestrator/Workflow Engine apply the result only after currentness and publication checks.

This proposal deliberately separates:
1. four engine/motor states;
2. five consultation response states;
3. ten case workflow states;
4. diagnostic reason codes;
5. transport/engine failure from a valid consultation result.

No layer is collapsed into a generic `status`.

## 2. Normative authority and ownership

| Concern | Authoritative owner | Engine/Adapter permission |
|---|---|---|
| Case identity and case version | Case Store / Orchestrator | Read-only snapshot |
| Target identity and target version | Case Store / Orchestrator | Read-only snapshot |
| Facts and their provenance | Case Store / trusted intake | Read-only snapshot |
| Evidence, claims, rules and applicability | Evidence/Knowledge services | Read-only references and bounded content |
| Evaluation run correlation | Orchestrator | Echo request correlation; cannot mint authoritative run identity |
| Request-local candidate | Engine | May create within one run only |
| Persistent suggestion and suggestion version | Orchestrator / suggestion ledger | Cannot mint, reactivate, or assert ledger status |
| Client question/rejection/acceptance | Trusted interaction path / decision ledger | Cannot authoritatively record |
| Execution consent | Trusted interaction path / authorization ledger | Cannot infer or create |
| Specialist review | Specialist-review service / ledger | Cannot self-approve |
| Workflow state, stop event, performed steps | Workflow Engine | Read-only context; no mutation |
| Publication decision | Orchestrator publication gate | No authority to publish itself |
| Actual service execution and outcome | Authorized professional/workflow record | Out of engine scope |

**Rule:** an engine response is a candidate result, not an authoritative case update.

## 3. Independent state vocabularies

### 3.1 Engine/motor state — exactly four

| Identifier | Meaning |
|---|---|
| `SUGGESTION_REVIEWABLE` | A reasoned candidate is available for review |
| `CONDITIONAL_SUGGESTION` | A candidate is valid only if explicitly stated conditions are met |
| `NEEDS_MORE_INFORMATION` | Required information or test is missing/unresolved |
| `STOP_OR_REFER_WITH_REASON` | The current run must stop or refer, with a reason |

A conditional suggestion is a motor state, not a sixth consultation response.

### 3.2 Consultation response state — exactly five

| Identifier | Meaning |
|---|---|
| `SYSTEM_REASONED_SUGGESTION` | A reasoned, traceable suggestion can be presented within validated knowledge |
| `NEEDS_INFORMATION_OR_TEST` | Missing information or test prevents a defensible suggestion |
| `NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW` | Remote assessment is insufficient |
| `SAFETY_STOP_NO_EXECUTION_SUGGESTION` | A safety constraint blocks an execution suggestion |
| `OUT_OF_V1_SCOPE` | The request is outside the approved first-version scope |

“Approved for execution” is not a consultation response state.

### 3.3 Case workflow — exactly ten existing states

These are the ten descriptive states already recorded in the approved README. Keep the Persian labels; do not invent numeric or manually assigned codes.

1. پذیرش ناقص
2. در انتظار ارزیابی
3. در انتظار تست
4. متوقف ایمنی
5. آمادهٔ تصمیم متخصص
6. در انتظار تأیید مشتری
7. تأییدشده برای اجرا
8. در حال اجرا
9. نیازمند پیگیری
10. بسته‌شده

Workflow state is owned only by the Workflow Engine. This proposal does not add an eleventh workflow state.

### 3.4 Reason codes — separate diagnostic vocabulary

- `DATA_GAP`: required case data absent, unknown, not asked, or missing from the current snapshot.
- `KNOWLEDGE_GAP`: applicable reliable evidence or a validated rule is unavailable.
- `ENGINE_FAIL`: engine, retrieval, validation, or processing failed.
- `CONFLICTING_DATA`: material records disagree.
- `SAFETY_CONCERN`: a safety constraint blocks the current path.
- `OUT_OF_SCOPE`: the request is outside the approved product scope.
- `STALE_CASE_VERSION`: evaluated snapshot is no longer current.

`OUT_OF_SCOPE` is not interchangeable with `OUT_OF_V1_SCOPE`. A generic evidence gap must not be relabelled as out of scope.

## 4. Knowledge state and provenance model

Every material datum is represented as a value plus an explicit knowledge state and provenance. The six accepted knowledge states remain distinct:

- `KNOWN`
- `UNKNOWN`
- `NOT_ASKED`
- `MISSING`
- `CONFLICT`
- `NOT_APPLICABLE`

A known false value is allowed only when it is explicitly recorded with provenance. False must never stand in for unknown, not asked, or missing.

**Logical Datum record (proposed field names):**

| Field | Type / requirement | Meaning |
|---|---|---|
| `fact_id` | opaque non-empty identifier | Identity of this recorded fact |
| `field_key` | controlled domain key | What the datum describes |
| `value` | typed value or null | Value only when state is `KNOWN`; null otherwise |
| `knowledge_state` | one of six states | Explicit epistemic status |
| `source_class` | controlled source class | `CLIENT_REPORTED`, `OPERATOR_RECORDED`, `SPECIALIST_OBSERVED`, `PRODUCT_DOCUMENT`, `INSTRUMENT_MEASURED`, `SYSTEM_DERIVED` |
| `source_ref` | opaque reference or null | Source record / document / observation |
| `recorded_at` | timestamp | When the fact entered the authoritative record |
| `recorded_by` | actor reference | Trusted recorder |
| `confidence` | qualitative/defined scale only if approved | Never inferred from missing data |
| `supersedes_fact_id` | identifier or null | Explicit correction lineage |
| `conflict_group_ref` | identifier or null | Links records that conflict |

Rules:
- A derived value is marked `SYSTEM_DERIVED`, never as a client report or physical observation.
- A correction appends a new fact and links the superseded fact; it does not silently rewrite history.
- A conflict is represented as conflict, not resolved by choosing whichever value is convenient.
- Image-derived observations must identify the image and limitation; images alone do not establish chemical history, internal pigment, porosity, elasticity, or material compatibility.
- A datum's source class is not proof that the source is correct; verification is a separate assessment.

## 5. Case aggregate and version model

### 5.1 Case

The Case Store owns one case aggregate with:
- `case_id`
- `created_at`, `updated_at`
- `case_version` (positive integer in the current Adapter draft)
- `target_version` (positive integer in the current Adapter draft)
- `current_workflow_state` (one of the ten existing descriptive states)
- `current_target_ref`
- `facts[]`
- references to evidence, claims, rules, specialist reviews, suggestions, decision events, workflow events, runs, and service records.

The aggregate is a logical model, not a decision to use a particular database or physical schema.

### 5.2 Version semantics

- Case Store/Orchestrator, never the engine, assigns versions.
- A material case-data change advances `case_version`.
- A target-colour change advances `target_version` and creates a fresh case evaluation version.
- The request and response must carry the exact same evaluated case/target version pair.
- An output is publishable only if the authoritative current pair still equals the evaluated pair at publication time.
- A retry of the same logical request retains its idempotency identity and does not create a new case version, run, or decision event.
- A new evaluation is not a retry.
- Acceptance, execution consent, and specialist review do not automatically carry to a changed relevant version.
- A changed datum invalidates only outputs that depend on that datum. Unknown dependency impact is treated as unresolved and blocks the affected output; it does not justify global invalidation or assumed independence.

No TTL or time-based expiry is introduced here. Expiry/revalidation by elapsed time remains a separately approved policy question.

## 6. Core logical entities

### 6.1 EvaluationRun

One logical evaluation attempt, distinct from retry delivery and from a fresh evaluation.

Required logical attributes:
- run identity and request correlation;
- operation: `EVALUATE_CASE`, `ANSWER_QUESTION`, or `REEVALUATE`;
- case and target version pair;
- contract and engine version;
- start/completion timestamps;
- run outcome: success or transport/engine failure;
- references to the exact input snapshot, policy snapshot, evidence references, and dependency set;
- result reference or null;
- retry/idempotency correlation.

The engine may echo request/run correlation but cannot authoritatively mint the persistent run identity or alter the version pair.

### 6.2 Candidate and persistent Suggestion

Keep these separate:

**Candidate (run-local):**
- `candidate_key` unique only within the run;
- candidate content/summary;
- motor state and consultation response state;
- conditions and missing information;
- evidence/claim/rule dependency references;
- limitations and next step;
- rank only after hard constraints pass.

**Persistent Suggestion (Orchestrator-owned):**
- `suggestion_ref` opaque durable identifier;
- `suggestion_version` exact immutable revision identifier or version number;
- originating `case_id`, `case_version`, `target_version`, `run_ref`;
- source `candidate_key`;
- lifecycle eligibility derived from authoritative ledger and dependency checks;
- accepted/rejected decision references;
- evidence/rule/dependency snapshot.

The engine cannot set `suggestion_ref`, `suggestion_version`, accepted/rejected status, active status, or display eligibility. A rejected exact suggestion version remains in history and cannot reappear as active. A replacement is a new independently validated candidate and persistent suggestion, never reactivation of the rejected one.

### 6.3 InteractionEvent and ClientDecisionEvent

Event history is append-only at the logical contract level. A current projection may be recomputed, but must not erase the event history. An explanatory interaction is not a client decision.

**Interaction event:**
- `QUESTION_ASKED`: records the question and its context; it never changes acceptance, rejection, or execution consent.

**Client decision events:**
- `SUGGESTION_REJECTED`: rejects the exact persistent suggestion/version.
- `SUGGESTION_ACCEPTED`: accepts the exact suggestion/version; no execution consent is implied.
- `EXECUTION_CONSENT_GIVEN`: explicit consent for the specified service/proposal/version context.

Specialist review, case-version changes, and workflow stop/performed-step records are separate event/entity types; they are not client decision events.

Common event-envelope attributes:
- event identity;
- case and target version context;
- event type;
- actor reference and actor kind;
- trusted interaction/authentication reference;
- event timestamp;
- correlation/idempotency reference;
- exact target suggestion/version when relevant;
- event-specific payload;
- source/interaction reference.

The exact authentication mechanism, deduplication window, ordering/linearization mechanism, and retention policy are not selected by this logical model.

### 6.4 CaseVersionEvent, WorkflowEvent and StopRequest

Case-version and workflow events are separate from client decisions. A target change is a case-version event, not a client decision. Workflow events include:
- client stop request;
- workflow state transition;
- performed-step record;
- service execution start/completion;
- follow-up and closure.

A stop request must be recorded with actor, time, current case/target version, workflow correlation, and reason if supplied. Only steps actually performed may be recorded as performed. Automatic resume is prohibited. A restart request must trigger a fresh evaluation against current case data, target, safety, rules, and evidence.

The engine cannot create, mutate, or replay these events.

### 6.5 Evidence, Claim, Rule, Dependency

The traceability chain for each material proposition is:

`Claim → Evidence passage/source revision → Reviewed Rule → Candidate/Suggestion`

Each edge must be resolvable and scoped. A document-level reference or boolean `evidence_valid` is insufficient.

**Evidence reference** must resolve exact source identity, revision/date, passage or bounded location, subject/product/market/conditions, limitations, verification status, and content digest where available.

**Claim** is a bounded proposition. Broad marketing text is not a claim definition.

**Rule** identifies the reviewed rule/version, scope, conditions, and the claims/evidence it relies on.

**Dependency** links a fact, evidence/claim, or rule version to the exact output components that depend on it.

Dependency impact:
- `EFFECTIVE`: dependent output is invalidated and freshly evaluated.
- `NON_EFFECTIVE`: output may be preserved only when independence is established.
- `UNKNOWN`: dependent output is withheld pending reassessment.

Do not infer independence from an absent dependency edge. If a required relationship cannot be resolved, fail closed for the potentially affected output.

### 6.6 SpecialistReview

A specialist review is a version-bound professional event:
- reviewer identity/reference and verified qualification status;
- exact case/target/suggestion version and run;
- decision: approve, reject, or request revision;
- reason and timestamp;
- evidence/rule context reviewed.

A technical QA role is not a professional qualification. Specialist review is not client acceptance, execution consent, or proof that a service was performed.

### 6.7 ServiceExecutionRecord and Outcome

Only the authorized workflow/professional record may represent execution:
- selected persistent suggestion/version;
- explicit specialist approval reference;
- explicit client acceptance and execution-consent references;
- actual product identity and batch/lot where available;
- actual steps and regions performed;
- actual timestamps and responsible professional;
- deviations and reasons;
- observed outcome by hair region;
- client feedback and follow-up.

Proposed plan and actual execution must never share one field or be treated as equivalent. The engine has no write authority for this entity.

## 7. Adapter request contract v1.0 proposal

The request is assembled by the Orchestrator from authoritative snapshots. The engine receives no direct write capability.

Required envelope:
- `contract_version`
- `request_id`
- `operation`
- `case_ref`
- `case_version`
- `target_version`
- `case_context`
- `question_context` (required only for `ANSWER_QUESTION`; null/absent for other operations under the final schema decision)
- `evidence_context`
- `policy_context`
- `dependency_context`

Request invariants:
1. All identifiers and version pairs come from trusted services.
2. Facts carry their knowledge state and provenance; no boolean shortcut replaces these.
3. Evidence references resolve to authoritative evidence records; model-invented references are rejected.
4. Policy context is versioned and immutable for the run.
5. Decision history and workflow state are read-only context.
6. Client question is not a decision event.
7. No execution formula, oxidant percentage, processing time, or chemical instruction permission is present.
8. Unknown or conflicting mandatory data is not coerced to a known value.
9. Request context is the minimum necessary snapshot for the requested operation.

## 8. Adapter response contract v1.0 proposal

Successful response fields:
- `request_id`, `case_ref`
- `evaluated_case_version`, `evaluated_target_version`
- `engine_state` (four-state vocabulary)
- `consultation_status` (five-state vocabulary)
- `reason_codes[]`
- `summary`
- `options[]` (0–3 validated candidates; request-local keys only)
- `conditions[]`
- `missing_information[]`
- `evidence_refs[]`
- `dependency_refs[]`
- `limitations[]`
- `next_step`

Response invariants:
- Response correlation and version pair exactly match the request.
- Candidate options require traceable evidence and dependency references.
- If a blocking reason or blocking response state exists, options are empty.
- A safety stop always has an empty options list.
- An engine failure is not a successful consultation response.
- The engine cannot return persistent suggestion IDs, decision status, workflow state, stop event, performed steps, execution consent, or execution authorization.
- No option is invented to fill a maximum of three. Return one if exactly one valid option exists; otherwise return only the valid set.
- Candidate rank is based on goal fit and technical validity after hard constraints, not input array order.
- An explanatory response may have zero options when it refers to an existing suggestion; the suggestion must be resolved from the authoritative ledger by the Orchestrator before publication.

## 9. Failure envelope

Transport/Adapter/engine failure is separate from consultation state.

On malformed output, version mismatch, unresolved required identity/dependency, provider exception, or engine failure:
- no candidate from that failed run is published;
- `consultation_result` is null;
- failure reason is `ENGINE_FAIL` or `STALE_CASE_VERSION` as appropriate;
- a correlation reference is returned;
- an earlier successful response is not substituted as the answer to the failed current request;
- historical results may remain available for audit but are not current output.

Retry semantics:
- same logical request → same idempotency identity and no duplicate event/run/version creation;
- fresh evaluation → new run identity and fresh current snapshot;
- retryability is a technical control, not permission to reuse stale results.

## 10. Publication gate

Immediately before any result is exposed as current:
1. Resolve the authoritative case and target version pair.
2. Confirm the run evaluated that exact pair.
3. Resolve the suggestion and suggestion-version relationship, if an existing suggestion is referenced.
4. Confirm exact rejection history does not exclude the suggestion.
5. Re-resolve required evidence, claim, rule, and dependency statuses.
6. Confirm no relevant safety stop or workflow stop blocks the path.
7. Confirm no concurrent case/target update or decision invalidated the result.
8. Publish only the validated current projection; otherwise withhold and request fresh evaluation/reassessment.

This is a compare-and-publish requirement. The physical transaction/locking mechanism is an implementation choice and must be validated before production persistence.

## 11. Dependency invalidation rules

| Change | Required effect |
|---|---|
| Target colour changes | New target version and fresh case evaluation; clear affected active suggestions and do not carry acceptance/consent/review |
| A recorded datum changes | Reassess only outputs that depend on that datum |
| Dependency impact is unknown | Withhold affected output and reassess |
| Evidence source/revision/status changes | Reassess linked claims, rules, and candidates only; do not invalidate unrelated claims by document association alone |
| Rule version/scope changes | Reassess candidates that depend on that rule |
| Exact suggestion rejected | Preserve rejection event; exact suggestion/version is never active again |
| Client asks a question | Answer without changing acceptance/rejection/consent |
| Client accepts suggestion | Record acceptance only |
| Client explicitly consents to execution | Record separate consent bound to exact service/suggestion/version context |
| Client requests stop | Record workflow stop request; no automatic resume; later restart is a fresh evaluation |
| Engine fails | Suppress all output from failed run; do not substitute stale success |

## 12. Explicit non-goals and safety boundaries

This package does not:
- infer hair history, porosity, elasticity, internal pigment, compatibility, or chemical condition from an image alone;
- infer chemistry from brand name, shade number, retailer listing, or similar product codes;
- generate or authorize formula, oxidant percentage, processing time, or chemical execution steps;
- activate Bijourka/Magic Color chemistry or safety rules without exact official product evidence and specialist validation;
- prove scientific validity through passing synthetic tests;
- connect real customer records or enable persistence of real customer data;
- authorize a pilot, deployment, release, or service execution.

The existing 88-row Bijourka snapshot remains identity-only and is not modified by HC-N01/N02.

## 12A. Current implementation scope — do not overstate engine readiness

The current repository contains distinct synthetic slices, not a complete real consultation engine:

- `/hair/catalog-identity/lookup` is guarded by `evaluate_hair_service_scope` and currently accepts only the exact `CATALOG_READY` service kind. Other service kinds, including `COMBINATION_CONSULT`, are returned as out-of-domain by that guard.
- `/hair/dialogue/turn` exercises synthetic dialogue transitions and state integrity. It does not evaluate hair chemistry, feasibility, product-specific rules, or generate real colour recommendations.
- The specialist preview and catalog knowledge bridge are synthetic, computed-only, and identity-scope only.
- The 88-row Bijourka snapshot is a retailer-derived identity artifact. Its HBI content digest identifies the repository artifact; it does not authenticate a manufacturer edition, publisher capture, formula, or safety claim.

Therefore, the operation names in §7 are logical target operations for the eventual consultation boundary, not a statement that the current HTTP API implements them. Extending service scope to actual combination consultation belongs to HC-N06 and must remain blocked until the evidence and rule gates in Package B and the oracle/validation gates in HC-N08 are satisfied.

## 13. Mapping to current implementation and required migration

| Existing implementation | Gap against this proposal | Required treatment |
|---|---|---|
| `app/domain/hair_dialogue_contract.py` | Synthetic dialogue state only; no full case aggregate, event ledger, workflow model, or dependency graph | Retain as narrow dialogue state-machine slice; do not mislabel it the full case model |
| `app/hair_color/adapter.py` | Draft 0.2 envelope; opaque contexts; no explicit question/dependency context; candidate objects opaque | Keep isolated; update only after PO accepts the contract and a separately scoped implementation task is approved |
| `tests/schemas/hair-color-adapter-0.2-draft.schema.json` | Draft structural schema; permissive additional properties; no complete case/fact/event schemas | Preserve as historical draft; do not claim it is v1.0 |
| `app/domain/hair_knowledge_case_bridge.py` | Catalog identity-only, computed-only projection | Keep within its narrow catalog identity scope |
| `app/domain/hair_specialist_contract.py` | Synthetic specialist review gate; no full case store | Reuse relevant concepts; do not conflate internal review with execution authorization |
| API dialogue route | Stateless synthetic transport; no persistence | Retain as test slice; no real-case use |

No migration or destructive rewrite is proposed. The existing tested slices remain intact until a separately reviewed implementation plan replaces or extends them.

## 14. Acceptance criteria for HC-N01 / HC-N02

HC-N01 is ready for PO acceptance when:
- [ ] request/response ownership and boundaries are accepted;
- [ ] the unresolved S06/S08 wire-state mapping is explicitly decided without inventing a sixth response state or overloading `OUT_OF_V1_SCOPE`;
- [ ] four motor and five response states remain separate;
- [ ] all ten workflow states remain owned by Workflow Engine;
- [ ] reason codes and failure envelope remain separate from consultation outcomes;
- [ ] exact version pair and publication-time currentness are explicit;
- [ ] option/evidence/dependency and fail-closed rules are explicit;
- [ ] question, rejection, acceptance, execution consent, and stop remain distinct;
- [ ] no chemical instruction capability is included.

HC-N02 is ready for PO acceptance when:
- [ ] case, datum/provenance, run, candidate, suggestion, decision event, workflow event, evidence/claim/rule/dependency, specialist review, and service record are defined;
- [ ] authoritative ownership is explicit for each entity;
- [ ] versioning and dependency-based invalidation are explicit;
- [ ] historical event facts are distinct from current projections/eligibility;
- [ ] synthetic-only and non-persistence restrictions are explicit;
- [ ] the stop-request mapping in §15 is decided.

## 15. Resolved semantic mappings and workflow-stop control

This section applies the already approved client-facing semantics in D-08 and the exact five response-state vocabulary in D-02. It does not add a sixth response state, change the ten workflow states, or reinterpret a test-fixture label as a wire enum.

### 15.1 S06 — knowledge gap

- Engine state: `STOP_OR_REFER_WITH_REASON`.
- Reason code: `KNOWLEDGE_GAP`.
- Consultation response state: `NEEDS_INFORMATION_OR_TEST` only when a specific missing authoritative document, source revision, applicability record, or other resolvable information can be requested or retrieved.
- The requested information may be product/evidence information; it must not be misrepresented as missing customer data.
- If no reliable applicable evidence can be obtained, withhold every dependent suggestion and state that no reliable answer is available. Do not guess and do not refer to a human merely to disguise the evidence gap. Referral is allowed only when independently justified by the case.
- `OUT_OF_V1_SCOPE` is permitted only if the requested claim/action is actually outside the approved V1 boundary.

### 15.2 S08 — no feasible or verified option

S08 is a test-oracle outcome, not one fixed wire response. The response state is selected from the actual supported cause:
- `NEEDS_INFORMATION_OR_TEST` when a defined missing fact, product document, or verification can resolve the uncertainty;
- `NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW` when physical hair assessment or qualified professional assessment is independently required;
- `SAFETY_STOP_NO_EXECUTION_SUGGESTION` when a safety constraint is the blocking cause;
- `OUT_OF_V1_SCOPE` only when the requested action is demonstrably outside V1.

In every branch, no unsupported option is invented. Return zero options unless a separate fresh evaluation establishes an independently valid alternative that passes every hard constraint. Record the concrete reason and next step. This conditional mapping preserves all five approved response states and avoids mislabelling infeasibility as scope exclusion.

### 15.3 S12 — rejected suggestion

S12 remains an authoritative client-decision/ledger event, not an engine or consultation response state. The exact rejected suggestion/version remains historical and ineligible for active display. An alternative requires a fresh candidate run and independent validation.

### 15.4 Client-requested stop vs ten workflow states

The accepted PO rule requires a customer-requested stop to be recorded, forbids automatic resume, and requires a fresh evaluation before any restart. The existing approved workflow vocabulary contains ten states, including **متوقف ایمنی**, but does not contain a separate **متوقف به درخواست مشتری** state. These meanings must not be conflated: a client stop is not automatically a safety stop.

**Chosen control mapping (no eleventh workflow state):** keep the current workflow state unchanged at the instant the stop request is recorded; append a distinct `CLIENT_STOP_REQUESTED` workflow event and set an authoritative workflow-control flag `resume_blocked=true`. No subsequent workflow transition or execution step is permitted while the block is active. A restart request clears the block only after a fresh evaluation against current case data, target, safety, rules, and evidence, followed by required workflow authorization. The old plan is never resumed. The flag is control metadata, not a workflow state.

The engine cannot set or clear this flag. The Workflow Engine owns the event, block, restart decision, and performed-step history.

## 16. Additional engineering choices — recommended defaults, not product-policy changes

The following are technical recommendations that preserve existing PO semantics; they must be reviewed during implementation design but do not change the ten workflow states or consultation behavior:

1. Use opaque UUID/ULID-style identifiers for case, run, suggestion, event, evidence, claim, rule, and dependency references; never expose database primary keys as domain identity.
2. Use a unique idempotency key scoped to tenant/workspace + operation + request origin, with a stored request digest. A repeated key with a different digest is rejected.
3. Use append-only event records plus derived current projections; no event is overwritten to change history.
4. Use a transactionally consistent compare-and-publish operation over current case/target versions and relevant decision/dependency revisions.
5. Store timestamps in UTC and preserve source-local timestamps only when the source explicitly supplies them.
6. Do not introduce automatic TTL expiry until a domain-specific rule is approved.
7. Do not define real-data retention/deletion mechanics in this synthetic-only phase.

## 17. Evidence and limitations

This is a source-grounded logical contract plus a bounded synthetic in-memory implementation. It is not a database migration, durable event store, specialist validation, or scientific review. Passing synthetic tests cannot prove that hair-colour advice is valid.

**Agent provenance:** GPT-6 in ChatGPT; input `master` SHA `103d81d0d59b8a7b025ee51f48d83a447e1665c3`; source files reviewed include `AGENTS.md`, `docs/01_project_control/HBI_AGENT_EXECUTION_PROTOCOL.md`, the hair-colour README, Adapter Draft 0.2, current dialogue contract/API, specialist contract, knowledge bridge, and synthetic fixtures/tests. This branch adds `app/domain/hair_case_contract.py` and `tests/test_hair_case_contract.py`; GitHub Actions is the required execution evidence. No local test run is claimed.


## 18. Bounded synthetic implementation delivered in this branch

The branch adds a pure in-memory contract module at `app/domain/hair_case_contract.py` and synthetic conformance tests at `tests/test_hair_case_contract.py`.

Implemented contract slices:
- Six explicit knowledge states and six provenance/source classes; `KNOWN=False` remains valid, while non-KNOWN values must be null.
- Synthetic case snapshot with the existing ten workflow labels only; no eleventh workflow state is introduced.
- Exact case/target version-pair currentness for computed runs.
- Explicit dependency comparison: unchanged or explicitly non-effective changes may preserve computation only; effective changes invalidate; missing/unknown impact is unresolved.
- Immutable event values and tuple-append API for in-memory history. Question, rejection, acceptance, execution consent, specialist review, stop, restart and execution events remain distinct.
- Rejection is bound to an exact suggestion version; acceptance does not imply execution consent.
- Execution start requires prior specialist approval, client acceptance and separate explicit consent for the same suggestion version.
- Client stop sets a separate resume block; only explanatory questions and a fresh authorized restart are accepted while blocked. Restart requires a successful evaluation object matching the exact case/target version pair and a separate workflow authorization. Prior acceptance, consent, and specialist review are not carried across restart.
- Event payloads contain bounded synthetic references and controlled tokens, not free-form customer text. Execution steps and completion require a prior execution-start event.

Non-implemented by design:
- No database, ORM, migration, durable event store, customer record link, or storage of real customer data.
- The tuple event history is process-local and is not durable traceability. Durable storage remains DEFERRED under PO-66-09 unless the PO issues a separate explicit authorization.
- No real suggestion generation, chemical rules, formula, recommendation display, or execution capability is enabled.

Acceptance evidence required from CI:
- Run `pytest -q tests/test_hair_case_contract.py`.
- Run the repository's full required CI workflow on the exact PR merge ref.
- Confirm no schema/migration or customer-storage paths are introduced by this package.


### 18.1 Exact PR verification evidence

- PR: [#580](https://github.com/vahidmaghsoudi2/hbi/pull/580), Draft and unmerged.
- Latest verified PR merge ref before this documentation correction: `7369ff0a46050dc764002d69ed9f02b8665de5c1`; branch head: `5ce39cb3b4721cf6476784d2978105c7f45fd4c4`.
- HBI CI run `43758962846`: success; test, governance and isolated smoke jobs all succeeded.
- HBI Auto Tasks run `43758962767`: success; `1046 passed, 801 warnings` in 51.31 seconds.
- HBI Pilot Browser Proof run `43758962736`: success.
- Artifacts: coverage `14179860819`, G8 smoke `14178958333`, G8 regression `14178908458`, browser proof `14179552007`, Auto Tasks evidence `14179596659`.
- All three runs checked out `refs/pull/580/merge` at merge SHA `7369ff0a46050dc764002d69ed9f02b8665de5c1`.
- The earlier test-fixture failure on a previous merge ref was corrected before this successful verification.
- These results establish only synthetic software conformance. They do not approve the logical contract on behalf of the PO, authorize persistence, or validate scientific/product-specific hair-colour rules.
