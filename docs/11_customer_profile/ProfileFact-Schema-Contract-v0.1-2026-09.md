# Profile Fact — Schema Contract v0.1

**Date:** 2026-09-23  
**Status:** DRAFT — SCHEMA GATE ONLY  
**Scope:** proven Profile Fact capability gap only.  
**Implementation authorization:** NONE.

## 1. Gate decision

Consumer Audit is closed.

The only currently proven persistent capability gap is a reusable customer-owned fact that can carry controlled provenance and lifecycle semantics across visits without overwriting or confusing it with the current Case.

This contract therefore evaluates **ProfileFact only**.

It does not authorize:
- Preference / PreferenceSignal
- ConstraintSafetySignal / persistent Safety entity
- Outcome / Follow-up entity
- Customer rewrite
- Recommendation/scoring changes
- Evidence-gate changes
- UI rewrite
- migration/backfill
- model creation

Customer remains the identity/root. Case remains the visit/current-need boundary.

## 2. Repository reality gate

The current repository was inspected before defining this revision.

### Confirmed facts

1. CustomerService.build_recommendation_profile() currently projects Customer fields (concerns, skin_profile, hair_profile, scalp_profile, age_range) into Recommendation context.
2. The Recommendation router merges saved Customer context with the current request and enforces Case ownership.
3. RecommendationService performs the existing need normalization, scoring, eligibility, inventory, conflict, medical-context, and evidence behavior. There is currently no ProfileFact consumer/adapter.
4. The existing audit implementation is ProductMutationLog + MutationLogService, and is currently Product-oriented rather than a generic ProfileFact audit subsystem.
5. Existing Customer fields are undifferentiated strings and do not provide the required fact-level provenance/lifecycle/version semantics.

Therefore this schema must be a **domain model**, not an audit log embedded inside each fact row.

## 3. Contract test

A ProfileFact is justified only if the implementation can demonstrate all of these behaviors:

1. reusable across visits;
2. distinct from Case Current Need;
3. attributable to a controlled source;
4. able to become stale without deletion;
5. able to be superseded or conflicted without silent overwrite;
6. explicitly confirmable/promotable;
7. auditable for material changes;
8. projectable into Recommendation without changing Recommendation rules.

Fields that do not support these behaviors require separate evidence.

## 4. Minimum domain entity

Logical entity: ProfileFact

Ownership:

ProfileFact.customer_id -> Customer.customer_id

### 4.1 Proposed minimum fields

| Field | Type / allowed values | Required | Purpose |
|---|---|---:|---|
| profile_fact_id | string PK | yes | Stable identity of one fact/version |
| customer_id | FK Customer | yes | Customer ownership |
| attribute_key | controlled identifier | yes | Identifies the fact attribute |
| value | attribute-defined value; initial implementation may use text-compatible representation | conditional | Actual fact value |
| value_state | KNOWN / UNKNOWN / PREFER_NOT_TO_SAY / NOT_APPLICABLE | yes | Explicit knowledge/response state |
| provenance | CUSTOMER / SELLER / SYSTEM / IMPORTED | yes | Assertion source |
| status | ACTIVE / STALE / SUPERSEDED / REVOKED / CONFLICTED | yes | Lifecycle state |
| supersedes_fact_id | nullable FK ProfileFact | no | Explicit replacement lineage |
| created_at | datetime | yes | Fact creation/recording time |
| updated_at | datetime | yes | System-managed last metadata/state update |

### 4.2 Intentionally removed from the entity

The following are **not ProfileFact columns** in this revision:

- recorded_at — redundant with created_at;
- mutation_reason — belongs to the audit event, not the current fact row;
- confirmed_at, confirmed_by_type, confirmed_by_id — confirmation is an auditable event; confirmation does not require a second copy of actor metadata in the fact row;
- revoked_by_type — revocation actor belongs to the audit event;
- revoked_at — remains representable through the lifecycle/audit implementation; a dedicated column requires implementation-level proof;
- freshness_policy_key — no repository policy registry/consumer is currently proven;
- provenance=OTHER — removed because a controlled source vocabulary must not have an unbounded catch-all.

## 5. State semantics

value_state answers **what is known or declared**.

status answers **where the fact is in its lifecycle**.

They are intentionally separate.

### Value state

- KNOWN — a concrete value is available.
- UNKNOWN — explicitly not known.
- PREFER_NOT_TO_SAY — customer explicitly declines.
- NOT_APPLICABLE — attribute does not apply.

empty != FALSE != UNKNOWN.

### Lifecycle status

- ACTIVE — reusable current fact.
- STALE — retained historical fact requiring review before current use when policy requires it.
- SUPERSEDED — replaced by a newer fact.
- REVOKED — explicitly withdrawn and not usable as active context.
- CONFLICTED — incompatible assertions exist; no silent latest-wins behavior.

There is deliberately **no status=UNKNOWN** because value_state=UNKNOWN already represents unknown content. An unresolved lifecycle condition must be represented by an explicit lifecycle state or implementation-level error, not by duplicating the value-state vocabulary.

## 6. Attribute control

attribute_key is not a free-form user string.

**Round-3 repository proof:** the current Recommendation projection consumes exactly these persisted Customer fields:

- `skin_profile`
- `hair_profile`
- `scalp_profile`
- `age_range`
- `concerns`

Therefore the initial canonical ProfileFact attribute set is limited to these five keys. No additional key is authorized by this contract.

`concerns` has a strict boundary: a ProfileFact under this key means a reusable customer concern; the current Case/request concern remains Case-scoped and is not silently promoted into ProfileFact.

The implementation must validate `attribute_key` against this fixed initial set at the ProfileFact write boundary. A separate attribute-registry table is not justified for this first slice.

Each key must have an explicit value representation/validation rule before model implementation; the initial repository stores the legacy values as strings, so the first implementation may preserve text-compatible values without inventing a generic JSON attribute system.

## 7. Provenance and promotion

Allowed provenance values are controlled:

- CUSTOMER
- SELLER
- SYSTEM
- IMPORTED

SYSTEM does not mean “AI guessed it”. A system-created fact must have an explicit rule or source.

Promotion from consultation information to reusable ProfileFact is not automatic.

Allowed promotion requires:
1. explicit customer confirmation; or
2. authorized seller/operator action permitted by policy, with provenance and an auditable mutation event.

The following do not automatically become ProfileFacts:
- Case Current Need;
- purchase history;
- recommendation output;
- Smart Summary;
- unconfirmed observation.

## 8. Lifecycle and versioning

Material value changes must preserve history.

### Edit

A materially different fact creates a new ProfileFact version and explicitly supersedes the previous fact.

### Supersession

supersedes_fact_id identifies the previous fact.

### Conflict

If two assertions cannot safely be treated as one current value, the system records a conflict rather than selecting a winner silently.

Conflict grouping is **not part of this first schema**. The current repository does not prove a concrete conflict consumer/workflow. If conflict handling later becomes necessary, it requires a separate schema gate rather than an implicit nullable column.

### Revoke

A fact may be withdrawn through an explicit lifecycle operation. The operation must be auditable and must prevent the revoked fact from being projected as active context.

Physical deletion is not the default operational behavior.

## 9. Freshness

Freshness is attribute-specific, but the current repository proves no persisted ProfileFact freshness/review consumer or policy registry. Therefore this first slice stores **no reviewed_at, review_due_at, or universal TTL fields**.

A later freshness workflow may be added only through a new evidence gate tied to a concrete consumer and policy.

No fixed rule such as “skin expires after six months” is part of the schema.

## 10. Audit contract

Auditability is a **separate event concern**, not duplicated state inside ProfileFact.

Every material ProfileFact mutation must produce an auditable event containing, as applicable:

- actor type;
- actor identifier where permitted;
- action;
- target entity/id;
- old state/value reference;
- new state/value reference;
- reason;
- timestamp;
- correlation/reference identifier where required.

The current repository's `ProductMutationLog` storage already contains `target_entity` and `target_id`, while `MutationLogService.append()` already accepts an explicit `target_entity` parameter. This proves that the smallest operational audit extension is **reuse of the existing append-only log path with `target_entity="ProfileFact"`**, rather than introducing a second audit table.

The existing model/service names remain Product-oriented, so implementation must add ProfileFact-specific tests for target isolation, actor/time/reason, old/new references, and append-only behavior before writes are authorized. A table rename or new audit subsystem is not part of this gate.

## 11. Recommendation boundary

Recommendation may consume ProfileFact only through a read-only projection/adapter.

The adapter may expose only facts that satisfy:

- correct Customer ownership;
- status usable under the applicable freshness rule;
- value_state=KNOWN;
- provenance/promotion requirements satisfied.

The adapter must not:

- alter scoring formulas;
- alter product eligibility;
- alter Evidence Gates;
- infer new safety rules;
- write ProfileFact;
- automatically promote consultation input.

Current Recommendation behavior remains frozen.

## 12. Legacy Customer mapping

Current Customer fields include:

- skin_profile
- hair_profile
- scalp_profile
- age_range
- concerns
- observations
- answers
- case_history
- operator_notes

No automatic backfill is authorized.

Each legacy field requires a separate disposition before migration:

| Legacy field | Disposition |
|---|---|
| skin_profile | candidate source only after provenance/value semantics are established |
| hair_profile | candidate source only after provenance/value semantics are established |
| scalp_profile | candidate source only after provenance/value semantics are established |
| age_range | candidate source; explicit freshness/promotion rules required |
| concerns | ambiguous persistent profile vs current need; no blind backfill |
| observations | not automatically promoted |
| answers | not automatically promoted |
| case_history | remains historical Customer data unless a separate proven consumer requires transformation |
| operator_notes | not automatically promoted |

## 13. Acceptance tests before implementation

The contract cannot advance until the following are demonstrably testable:

1. create a ProfileFact owned by a Customer;
2. reject cross-customer ownership;
3. represent all four value states;
4. enforce canonical provenance;
5. enforce canonical lifecycle status;
6. confirm/promote a fact through an auditable operation without creating a new lifecycle vocabulary;
7. supersede a fact without destroying history;
8. represent a conflict without silent winner selection, if conflict is retained;
9. revoke a fact and prevent active projection;
10. produce an audit event containing actor/time/reason and old/new state/value references;
11. apply freshness/review metadata only where a real policy consumer exists;
12. project eligible ProfileFacts into Recommendation context;
13. prove Recommendation/Scoring/Evidence behavior is unchanged;
14. prove legacy Customer behavior remains compatible until an explicit migration decision.

## 14. Gate status

Consumer Audit                 = COMPLETE
Repository Reality Review      = COMPLETE
Canonical Attribute Set        = PROVEN (5 legacy Recommendation-consumed keys)
Audit Mechanism                 = PROVEN AS REUSABLE EXISTING APPEND-ONLY PATH
Schema Contract                = REVIEW ROUND 4
Minimum domain model           = MINIMIZED / PENDING FINAL GATE
Model implementation           = BLOCKED
Migration / Backfill           = BLOCKED
UI                             = BLOCKED
Recommendation / Scoring       = FROZEN
Evidence Gates                 = FROZEN
Preference                     = NOT JUSTIFIED
Constraint/Safety Signal       = NOT JUSTIFIED
Outcome / Follow-up Entity     = NOT JUSTIFIED

**Next gate:** final schema review is now limited to implementation safety: ownership, value/provenance/status constraints, supersession lineage, consent behavior, and reuse of the existing append-only audit path. No unproven freshness, conflict, or source-tracking columns enter the first model.

No model, migration, or UI code is authorized by this document.
