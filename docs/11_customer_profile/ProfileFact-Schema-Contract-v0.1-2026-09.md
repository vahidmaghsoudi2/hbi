# Profile Fact — Schema Contract v0.1

**Date:** 2026-09-23  
**Status:** DRAFT — SCHEMA GATE ONLY  
**Scope:** proven Profile Fact capability gap only.  
**Implementation authorization:** NONE.

## 1. Gate decision

Consumer Audit is closed.

Only one persistent capability gap is currently proven:

> A reusable customer profile fact needs provenance, lifecycle/status, freshness/review semantics, explicit confirmation/promotion, conflict handling, and auditable change behavior that cannot be represented safely by today's undifferentiated Customer string fields.

This contract therefore evaluates **Profile Fact only**.

It does **not** authorize:
- Preference / PreferenceSignal
- ConstraintSafetySignal / persistent customer Safety entity
- Outcome / Follow-up entity
- Customer rewrite
- Recommendation or scoring changes
- Evidence-gate changes
- UI rewrite
- Migration or backfill

The existing Customer remains the identity/root and Case remains the visit/current-need boundary.

## 2. Contract test

A Profile Fact structure is justified only if all of the following are required by an executable consumer:

1. reusable across visits;
2. distinguishable from today's Case-scoped Current Need;
3. attributable to a controlled source;
4. able to become stale without being silently deleted;
5. able to be superseded or conflicted without silent overwrite;
6. explicitly promotable/confirmable;
7. auditable when edited, revoked, or deleted;
8. safely projectable into Recommendation without changing Recommendation rules.

If a proposed field does not serve one of these behaviors, it is not part of this schema.

## 3. Minimum entity

Proposed logical entity name: ProfileFact

Ownership:

ProfileFact.customer_id → Customer.customer_id

A ProfileFact is **customer-owned reusable context**. It is not a visit, recommendation, purchase, feedback record, or derived summary.

### 3.1 Field-by-field contract

| Field | Type / allowed values | Required | Why it exists | Writer | Consumer | Lifecycle rules |
|---|---|---:|---|---|---|---|
| profile_fact_id | string PK | yes | Stable identity for one fact/version | system | profile operations, audit | immutable |
| customer_id | FK → Customer | yes | Ownership/root relation | system | customer profile retrieval | immutable |
| attribute_key | controlled string | yes | Identifies the profile attribute | customer/seller flow under contract | profile retrieval, recommendation adapter | immutable for a fact |
| value | typed/serialized value; initial slice may use text-compatible values | yes when value_state=KNOWN | Actual reusable fact value | customer or authorized seller | profile/recommendation projection | never silently overwritten |
| value_state | KNOWN / UNKNOWN / PREFER_NOT_TO_SAY / NOT_APPLICABLE | yes | Separates explicit state from absence | customer/seller/system according to source | profile consumers | state changes are auditable |
| provenance | CUSTOMER / SELLER / SYSTEM / IMPORTED / OTHER | yes | Identifies assertion source | system from controlled operation | trust/promotion/review logic | OTHER requires documented normalization/review |
| status | ACTIVE / STALE / SUPERSEDED / REVOKED / CONFLICTED / UNKNOWN | yes | Lifecycle without a second state vocabulary | system/authorized operation | profile retrieval and review | transitions explicit and auditable |
| source_case_id | nullable FK → Case | no | Links an observation/promotion to originating consultation when one exists | system | audit/provenance | nullable; never makes fact Case-scoped |
| observed_at | datetime nullable | no | When underlying fact was observed/declared | system/operator flow | freshness policy | historical; not silently changed |
| recorded_at | datetime | yes | When HBI recorded the fact | system | audit | immutable |
| reviewed_at | datetime nullable | no | Last explicit freshness/review check | authorized operation | freshness/review flow | updated only by review |
| review_due_at | datetime nullable | no | Policy-derived review boundary | system/policy layer | review queue | never a universal TTL |
| freshness_policy_key | controlled policy identifier, nullable initially | no | Records governing attribute-specific policy | system | audit/review | policy semantics live outside entity |
| confirmed_at | datetime nullable | no | Explicit confirmation without a new lifecycle state | customer/authorized seller | promotion/audit | only set by explicit confirmation |
| confirmed_by_type | CUSTOMER / SELLER / null | no | Confirmation actor category | system | audit | paired with confirmation metadata |
| confirmed_by_id | string nullable | no | Identifies actor where permitted | system | audit | immutable once recorded |
| supersedes_fact_id | nullable FK → ProfileFact | no | Makes replacement explicit | system | history/audit | immutable link |
| conflict_group_id | nullable string | no | Groups mutually inconsistent facts | system/authorized conflict operation | review UI/service | set when conflict established |
| revoked_at | datetime nullable | no | Records explicit revocation | authorized operation | audit | required when status=REVOKED |
| revoked_by_type | CUSTOMER / SELLER / null | no | Records revoking actor category | system | audit | paired with revoked_at |
| created_at | datetime | yes | System creation time | system | audit | immutable |
| updated_at | datetime | yes | Last metadata/state update | system | audit | system-managed |
| mutation_reason | string | required for material state/value mutation | Explains why the mutation occurred | authorized operation | audit/review | immutable per mutation |

### 3.2 Fields deliberately excluded

The entity must not contain:

- today's Current Need as a replacement for Case;
- recommendation score, ranking, eligibility, or evidence;
- product purchase history;
- generic operator notes as a fact substitute;
- derived Smart Summary text;
- medical diagnosis;
- a universal TTL;
- CANDIDATE or CONFIRMED as lifecycle/status values;
- automatic Preference creation;
- automatic Safety Signal creation.

## 4. Value semantics

### KNOWN
A concrete value is available and usable subject to status, freshness, provenance, and applicable safety rules.

### UNKNOWN
The attribute is explicitly not known. This is not equivalent to null/absence.

### PREFER_NOT_TO_SAY
The customer explicitly declines to provide the value. It must not be inferred or replaced silently.

### NOT_APPLICABLE
The attribute does not apply to this customer/context.

The contract preserves:

> empty ≠ FALSE ≠ UNKNOWN.

## 5. Confirmation and promotion

Promotion from consultation information to reusable ProfileFact is **not automatic**.

Permitted promotion requires one of:

1. explicit customer confirmation; or
2. authorized seller/operator action allowed by policy, recorded with provenance and audit.

The following do **not** automatically promote to ProfileFact:

- Case Current Need;
- purchase;
- recommendation;
- Smart Summary;
- unconfirmed observation.

confirmed_at and confirmation actor metadata express confirmation. They do not create a parallel lifecycle vocabulary.

## 6. Lifecycle and conflict rules

### ACTIVE
Current reusable fact.

### STALE
Fact remains historical but requires review before being treated as current reusable context when governing freshness policy requires review.

### SUPERSEDED
Replaced by a newer explicit fact. The previous fact remains historical.

### REVOKED
Explicitly withdrawn. It must not be projected as active context.

### CONFLICTED
Two or more assertions cannot safely be treated as one current value. Conflict must be visible; the system must not silently choose the latest value.

### UNKNOWN
Fact state is explicitly unresolved/unknown.

### Required invariants

- No silent overwrite of a previous fact.
- Supersession is explicit through supersedes_fact_id.
- Conflict is explicit through conflict_group_id.
- Revocation is explicit and auditable.
- Historical facts remain queryable.
- Status transitions require actor, reason, and timestamp in the audit trail.

## 7. Freshness contract

Freshness is **attribute-specific**.

The entity stores review metadata; it does not encode a universal expiration rule.

Examples:

- Current Need → Case-scoped; not a ProfileFact.
- Identity/contact → reviewed when changed.
- Skin/hair/scalp attributes → review driven by policy and meaningful change.
- Preferences → remain until changed/rejected; no invented fixed TTL.
- Safety-related customer context → reviewed when relevant information changes; this contract does not create a Safety entity.
- Historical interaction/outcome → does not expire merely because time passed.
- Derived summaries → regenerated; not persisted as ProfileFact.

No fixed values such as "6 months for skin" or "12 months for texture/scent" are schema rules.

## 8. Edit / delete / revoke

A ProfileFact is not updated in place in a way that destroys history.

### Edit
A materially different fact creates a new version/fact and explicitly supersedes the previous one.

### Revoke
Sets the old fact to REVOKED with actor, timestamp, and reason. Revocation does not erase audit history.

### Delete
Physical deletion is not the default behavior for a fact with operational/audit significance. Any legally required deletion must follow organizational retention/privacy policy and preserve only what is legally permitted.

### Audit minimum

Every material mutation must be attributable by:

- actor type;
- actor identifier where permitted;
- action;
- old state/value reference;
- new state/value reference;
- reason;
- timestamp;
- mutation_reason for every material state/value mutation.

This contract does not assume a new audit table until the repository's existing audit capability is inspected and a separate implementation slice is approved.

## 9. Customer and Case relationship

### Customer
Customer remains the identity/root record.

ProfileFact adds reusable, structured context without turning Customer into a generic event store.

### Case
Case remains the current consultation/need boundary.

A ProfileFact may optionally reference source_case_id for provenance, but that reference does not make the fact Case-scoped.

Therefore:

Current Need → Case

Reusable Profile Fact → ProfileFact → Customer

## 10. Recommendation boundary

The Recommendation system may consume ProfileFact only through a **read-only projection/adapter**.

The adapter may select only facts satisfying the existing contract:

- customer ownership matches;
- status is usable under freshness policy;
- value_state is KNOWN;
- provenance/confirmation requirements are satisfied where applicable.

The adapter must not:

- alter recommendation scoring;
- alter product eligibility;
- alter Evidence Gates;
- infer new safety rules;
- write ProfileFact;
- promote consultation input automatically.

Recommendation/Scoring/Evidence Gates remain frozen.

## 11. Legacy Customer mapping

Current Customer fields include:

- skin_profile
- hair_profile
- scalp_profile
- age_range
- concerns
- observations
- answers
- operator_notes

No automatic backfill is authorized by this contract.

Before migration, each legacy field must receive a field-level disposition:

| Legacy field | Initial disposition |
|---|---|
| skin_profile | candidate source only after provenance/value semantics are established |
| hair_profile | candidate source only after provenance/value semantics are established |
| scalp_profile | candidate source only after provenance/value semantics are established |
| age_range | candidate source; explicit freshness/promotion rules required |
| concerns | ambiguous between persistent profile and current need; no blind backfill |
| observations | not automatically promoted |
| answers | not automatically promoted |
| operator_notes | not automatically promoted |

Migration/backfill requires a separate approved gate.

## 12. Acceptance tests for this contract

The schema cannot advance to implementation until the following are testable:

1. create a ProfileFact owned by Customer;
2. reject cross-customer ownership;
3. represent all four value states;
4. enforce canonical provenance;
5. enforce canonical lifecycle/status;
6. confirm a fact without introducing a new lifecycle value;
7. supersede a fact without destroying its history;
8. represent a conflict without silent winner selection;
9. revoke a fact with auditable actor/time/reason;
10. require a mutation reason for material state/value changes;
11. represent freshness review metadata without a universal TTL;
12. project only eligible ProfileFacts into Recommendation context;
13. prove Recommendation/Scoring/Evidence behavior is unchanged;
14. prove legacy Customer fields remain behaviorally compatible until an explicit migration decision.

## 13. Gate status

```
Consumer Audit                 = COMPLETE
Architecture Boundary          = D-plus / ProfileFact-only
ProfileFact Schema Contract    = DRAFT — THIS DOCUMENT
Schema Implementation          = BLOCKED
Migration / Backfill           = BLOCKED
UI                             = BLOCKED
Recommendation / Scoring       = FROZEN
Evidence Gates                 = FROZEN
Preference                     = NOT JUSTIFIED
Constraint/Safety Signal       = NOT JUSTIFIED
Outcome / Follow-up Entity     = NOT JUSTIFIED
```

**Next gate:** independent review of this field-by-field contract.

Only after acceptance may a minimal implementation proposal be written. No model, migration, or UI code is authorized by this document.
