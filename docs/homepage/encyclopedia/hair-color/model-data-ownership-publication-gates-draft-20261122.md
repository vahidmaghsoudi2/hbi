# Hair Color — مدل مالکیت داده، Lineage و Publication Gate (Draft)

**وضعیت:** پیشنهاد معماری/مدل داده؛ review لازم؛ هیچ تصمیم PO یا مجوز runtime/production ایجاد نمی‌کند.  
**تاریخ:** 2026-11-22  
**دامنه:** طراحی مستقل مشاوره رنگ مو؛ synthetic-only طبق PO-66-09.  
**مراجع:** README Hair Color؛ Adapter Contract Draft 0.2 و D-01…D-08 در commit ثابت PR #535؛ ممیزی H1 همان branch.

## 1. اصل طراحی

Case را به یک blob mutable که موتور همه چیز را از آن بخواند/بنویسد تبدیل نکنیم. مالکیت داده و تصمیم باید مستقل باشد. موتور/مدل فقط یک evaluation request محدود را می‌گیرد و run-local candidate تولید می‌کند؛ authoritative history، persistent suggestion identity، consent و workflow را ایجاد یا تغییر نمی‌دهد.

این سند field names، storage، event protocol، API، schema یا state transition اجرایی را تصویب نمی‌کند. همه identifiers و sequencing پیشنهادهای design-review هستند.

## 2. Ownership matrix

| Domain / record | Authoritative owner | Write authority | Consultation engine access | Immutable/history rule | Version scope |
|---|---|---|---|---|---|
| Case identity | Case Store | Case service | read-only snapshot ref | identity never repurposed | case |
| Case data / observations | Case Store | authorized intake/operator/specialist actor | minimum relevant snapshot | changes append source record; snapshot versioned | case-version |
| Knowledge state + provenance | Case Store | record owner under intake/review process | read-only | each datum preserves source + state | field-record/version |
| Target/goal | Case Store | client/operator through approved event | read-only current snapshot | target change creates new target version | target-version |
| Evidence source record | Evidence Registry | curator/reviewer | refs only | source metadata and review history retained | evidence-version |
| Evidence applicability/review | Evidence Registry / specialist approval | designated reviewer | read-only status/scope | approval/revocation changes create history, not silent overwrite | claim/product/version scope |
| Policy/rule bundle | Policy Registry | authorized policy owner | read-only pinned version | policy revision creates new version | policy-version |
| Evaluation run | Orchestrator/Run Store | orchestration service | engine output returned to caller | run immutable after completion; failed runs retained as failed | run |
| Candidate | Run output / Orchestrator staging | engine only creates request-local candidate | created in current request only | no persistent ID minted by engine; validated before persistence | run-local key |
| Suggestion identity/version | Orchestrator / Case Store | orchestrator after gate | engine cannot author | immutable reference; replacement gets new version/ref | suggestion-version |
| Client question / decision events | Decision Ledger | event service under client action | only minimal read-only context if allowed | append-only; questions separate from decisions | event + suggestion version |
| Execution consent | Decision Ledger | explicit consent event service | not engine authority | separate explicit event; no inferred consent | consent-event |
| Workflow / stop / performed steps | Workflow Engine | workflow service / authorized actor | no mutation; possibly read-only status | stop and performed steps recorded; no auto resume | workflow-version/event |
| Dependency graph | Dependency service / Orchestrator | validated evaluator or trusted dependency registry (ownership needs final review) | engine may propose local dependency links; cannot authorize invalidation | dependency changes versioned; unresolved impact blocks publication | output/dependency version |
| Audit / correlation | Audit service | services emit events; central audit | no direct writes | append-only audit, correlation IDs | event/run |

## 3. Provenance contract (conceptual)

Every material datum must be distinguishable by its epistemic status and origin. Existing approved knowledge-state vocabulary is preserved:
- `KNOWN`
- `UNKNOWN`
- `NOT_ASKED`
- `MISSING`
- `CONFLICT`
- `NOT_APPLICABLE`

### Minimum record relationships
A value/observation should have a relationship to:
- data item/field identity;
- value or bounded representation (no unsafe or unnecessary payload);
- knowledge state;
- source class (client-reported, operator-recorded, specialist-observed, instrument-measured, product-document, system-derived, etc.; final enumeration remains open);
- source/event ref and actor where available;
- recorded time and observed/effective time where distinct;
- case and case-version;
- transformation/derivation ref if computed;
- supersedes/contradicts relation if relevant.

No value may be converted to `false`, zero, or an empty string solely because it is unknown, not asked, missing, or conflicting. Conflicting values retain both provenance paths until authorized resolution. A derived datum cannot masquerade as direct observation.

## 4. Evidence-to-claim relation (not a generic case citation)

Evidence records and consultation claims are separate entities. One source can support only claims within its scope. A source reference alone does not imply applicability, quality, or approval.

| Relation element | Why needed | Gate owner |
|---|---|---|
| Claim/rule reference | exact statement the source is intended to support | rule/consultation design |
| Evidence source/version reference | immutable source identity | Evidence Registry |
| Scope (product/market/line/version/conditions, if relevant) | prevents generalizing across products or markets | Evidence Registry + specialist |
| Evidence status and review metadata | distinguishes retrieved from accepted/reviewed | designated reviewer |
| Candidate/run relationship | prevents source being applied to unrelated output | Orchestrator |
| Dependency link | identifies affected outputs when status/data changes | dependency service |
| Evidence snapshot/validity-at-run | supports later audit of what was used | run/audit store |

The product-specific chemistry/feasibility/safety validation is out of scope here. No source is promoted into a rule by this model proposal.

## 5. Version and identity tuple (proposal)

To avoid mixing target, case, run, and suggestion identity, keep the following distinct:
- `case_ref` — case identity;
- `case_version` — case-data snapshot version;
- `target_ref` + `target_version` — intended goal identity and version;
- `run_ref` — one evaluation attempt (including failure);
- `candidate_key` — temporary key within one run;
- `suggestion_ref` + `suggestion_version` — persistent validated suggestion identity assigned outside engine;
- `event_ref` — question, rejection, acceptance, execution consent, stop, or other explicit event identity;
- `workflow_ref/version` — workflow identity/version;
- `evidence_ref/version`, `policy_ref/version`, `rule_ref/version` — pinned evidence/policy/rule references.

**Proposed lineage for any published suggestion:** case/target versions → run → candidate key → validation result → persistent suggestion ref/version → client event refs → workflow event refs if applicable. The relation is a design target, not approved runtime shape.

## 6. Publication gate — sequential checks

This is a proposed review sequence; the gate must fail closed on unknown or failed material checks.

1. **Request integrity:** required envelope fields; operation-specific inputs; exact case/target versions; request/run correlation.
2. **Snapshot integrity:** case data and provenance snapshot match authoritative store; material conflicts are explicit; required fields do not silently default.
3. **Policy pinning:** applicable policy/rule bundle identified and version-pinned.
4. **Evidence resolution:** every material claim resolves to evidence refs within scope; review/applicability state is known; evidence revision and dependency impact checked.
5. **Engine boundary:** engine only returns run-local candidates; no persistent suggestion/decision/workflow authority; forbidden execution fields absent.
6. **Candidate structural gate:** candidate shape; hard-constraint results; candidate-specific claim/evidence links; no more than three options; ranking deterministic/criteria-based rather than input-order based.
7. **Consultation status gate:** state/reason consistency; data/knowledge gap, conflict, specialist-review, safety stop, out-of-scope and engine-failure boundaries suppress dependent candidates.
8. **Authoritative ledger gate:** if referencing an existing suggestion (question/rejection etc.), exact suggestion ref/version is resolved and current eligibility/decision status read from ledger; never trust engine-authored status.
9. **Freshness/atomicity gate:** re-check current case/target/evidence/workflow versions immediately before publication; if any material dependency changed, suppress stale output and require re-evaluation. Atomicity/locking protocol is unresolved.
10. **Persist and audit:** orchestrator assigns persistent suggestion identity only after validation; records pinned inputs, gate results, evidence/claim links, run outcome, and event correlation. No implicit client decision.
11. **Client display:** publish only validated current output; question answers do not modify acceptance or execution consent.
12. **Workflow:** separate service handles stop, fresh restart, performed steps, and workflow transitions; never auto-resume.

## 7. Dependency invalidation matrix (conceptual)

| Change event | Must re-evaluate | Can remain historical | Cannot assume |
|---|---|---|---|
| Client target/goal changes | outputs dependent on target; create fresh target/case evaluation | prior suggestion/acceptance events | acceptance, consent, specialist review carries forward |
| Material case datum changes | dependent claims/options only; if dependency unknown, withhold affected output | unrelated data and historical events | every output independent, or every output invalid |
| Evidence source/status/scope changes | claims/options linked to affected evidence; unknown dependency impact blocks affected publication | prior run/evidence snapshot and audit | source change automatically decides notice/consent/remediation policy |
| Policy/rule version changes | outputs depending on changed policy/rule | prior run with pinned policy version | silent policy migration |
| Client asks a question | explanation for exact current suggestion, after ledger check | decision snapshot and suggestion history | question equals accept/reject |
| Client rejects a suggestion | exact suggestion version marked rejected by ledger event; fresh alternative evaluation if requested | rejected suggestion ref/history | rejected option can be reactivated or returned as active |
| Client requests stop | workflow stops current path; record only performed steps | performed-step records and stop event | automatic resume |
| Engine/retrieval failure | current run result is failed; suppress its candidate output | prior successful runs for audit only | stale output can be shown as the current run |
| Case or target version mismatch | current request fails or fresh run required | prior version history | mismatch may be silently repaired by engine |

Policy for notification, fresh acceptance, execution consent, remediation of already performed steps, evidence TTL, and automatic revocation remains undecided in the separate PO proposal. This matrix is not a decision.

## 8. Event ordering and concurrency — questions to resolve before persistence

- Which service is authoritative for case-version increments, and how is a concurrent edit detected?
- What is the publication transaction boundary between validation, suggestion persistence, and client display?
- Are run requests idempotent? Which correlation key distinguishes retry from a new evaluation?
- How are client events ordered when a question/rejection arrives while an evaluation is running?
- How does publication re-check ledger status and workflow stop state without race conditions?
- What is retained for audit when an output is suppressed as stale or failed?
- How does a restart after stop establish a new case/target snapshot and avoid carrying over old consent or acceptance?

No TTL, expiry, rollback, compensation, notification, or automatic revocation is proposed here.

## 9. Mapping to existing contract rather than redesign

| Existing contract area | Model-data proposal reuses | Additional detail to review |
|---|---|---|
| Request / trusted context | case snapshot, version, evidence/policy refs | typed sub-schema; question requirement |
| Knowledge-state/provenance | six states + source classes | source record relation, time/derivation and conflict lineage |
| Response/candidate | run-local candidate, options and summary | candidate-specific claims/evidence links |
| Option invariants | hard constraints, max three, ranking independent of input order | test enforcement boundary and per-option pass evidence |
| Version/decision behavior | case/target versions, ledger authority | exact tuple and atomic publication protocol |
| S11–S13 fixture traceability | fixture test-oracle structures | runtime service contracts; test-only oracle not wire payload |
| S14 workflow | stop and performed-step ownership | workflow-version and fresh-restart semantics |
| S15 failure | fail-closed, no consultation result | run-scoped correlation and stale-output handling |

## 10. Decisions needed for later review (not answered here)

1. Operation-specific question shape: string vs typed question/context; requiredness and blank handling.
2. Candidate-specific evidence/claim link representation and whether every candidate requires a structured constraint evaluation record.
3. Exact authoritative version tuple and publication freshness check semantics.
4. Event ordering, idempotency, and atomic publication design.
5. Ownership and mutability of dependency graph (engine proposes vs trusted service records).
6. Wire mapping for S06 and S08.
7. Evidence revision PO policy A–D.
8. Any specialist evidence approval protocol and scope. This is not a scientific validation.

## 11. Next deliverable recommendation

Build a **contract revision proposal**, not runtime implementation:
- typed domain sub-schema sketches for case/policy/evidence and candidate;
- operation-specific request rules;
- candidate → claim → evidence links;
- version/ledger/workflow publication gate;
- S11–S15 boundary tests planned against the relevant service contract;
- decision table listing what is purely technical and what requires PO approval.

Only after this draft is reviewed and PO authorization is explicit should runtime/schema/fixture changes begin. Keep synthetic-only restriction and the no-pilot/no-release gate.
