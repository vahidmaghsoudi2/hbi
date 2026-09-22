# Customer Profile — Profile Fact Schema Contract v0.1
Date: 2026-09-23
Status: DRAFT — SCHEMA GATE, NO IMPLEMENTATION AUTHORIZED

## 1. Purpose

This document converts the one proven Consumer Audit capability gap into a field-by-field contract for reusable customer Profile Facts.

It is intentionally narrower than Customer Profile Contract v1.1:
- Profile Fact only.
- No Preference, Safety Signal, Outcome, Follow-up, Visit, or generic Record model.
- No database table, ORM model, migration, API, UI, or recommendation implementation is authorized.

Central test:

> Can the required provenance/lifecycle/freshness behavior be represented safely in the existing Customer row without semantic overload or loss of history?

Current repository evidence says no for the required reusable-fact behavior. Customer currently stores single mutable strings such as skin_profile, hair_profile, scalp_profile, and concerns, while the approved contract requires controlled provenance, lifecycle/freshness, explicit promotion, conflict handling, and historical traceability. Replacing one string with another would not provide those behaviors.

Therefore this contract defines the minimum structured Profile Fact capability for the next implementation gate. It still does not authorize implementation.

## 2. Consumer proof

### Consumer
1. Customer profile retrieval/update.
2. Recommendation profile construction as a read-only consumer.
3. Seller workflow that must distinguish reusable profile truth from today's consultation input.

### Required behavior
A reusable fact must:
- belong to one Customer;
- identify exactly what attribute it represents;
- carry a meaningful value state;
- identify provenance;
- retain when it was recorded;
- support lifecycle/freshness review;
- support supersession/conflict without silently overwriting history;
- be explicitly confirmed/promoted rather than inferred from a visit, purchase, recommendation, or summary;
- be auditable when materially changed;
- be readable without changing recommendation scoring or eligibility.

### Why existing Customer alone is insufficient
Current Customer stores one current value per several profile dimensions. It cannot safely represent, for the same customer:
- two competing historical values with provenance;
- a newer value superseding an older value while preserving history;
- a fact requiring review because it is stale;
- a conflicted value awaiting resolution;
- origin Case/context for a recorded fact;
- controlled promotion from consultation information to reusable fact.

Adding more free-form columns would reproduce the same limitation and increase semantic overload.

## 3. Minimum field contract

| Field | Required | Type/shape | Written by | Consumed by | Allowed semantics | Why it exists | Explicitly not for |
|---|---|---|---|---|---|---|---|
| fact_id | yes | opaque string PK | system | all fact consumers/audit | immutable unique identifier | stable identity for one fact | customer ID or attribute key |
| customer_id | yes | FK/reference to Customer | system | profile retrieval/recommendation | identifies owning Customer | establishes root ownership | Case ownership |
| attribute_key | yes | controlled string | authorized recording flow | profile/recommendation/UI | identifies the fact type | prevents meaning living only in free-form columns | arbitrary JSON field names |
| value | conditional | attribute-defined typed/serialized value | authorized actor | profile/recommendation | actual fact value when value_state=KNOWN | stores reusable value | diagnosis inference or operator essay |
| value_state | yes | enum | authorized actor/system | all fact consumers | KNOWN / UNKNOWN / PREFER_NOT_TO_SAY / NOT_APPLICABLE | distinguishes established value from meaningful non-value states | lifecycle/status |
| source | yes | enum | system from recording context | audit/profile consumers | CUSTOMER / SELLER / SYSTEM / IMPORTED / OTHER | controlled provenance | authorization role |
| source_description | conditional | short text | authorized recorder | audit/review | required when source=OTHER | controls temporary OTHER provenance | durable provenance category |
| recorded_at | yes | datetime | system | freshness/history | time fact was recorded | establishes temporal history | unknown business event time |
| status | yes | enum | authorized lifecycle operation | profile/recommendation | ACTIVE / STALE / SUPERSEDED / REVOKED / CONFLICTED / UNKNOWN | explicit validity/reusability | candidate/confirmed lifecycle |
| review_due_at | conditional | datetime | policy/system | profile/review workflow | next review point when policy requires | attribute-specific freshness | automatic deletion date |
| origin_case_id | no | Case reference | system when available | audit/history | links consultation origin without changing ownership | traceability | replacing customer_id |
| supersedes_fact_id | no | Profile Fact reference | lifecycle operation | history/audit | points to fact replaced by this fact | preserves replacement chain | deleting old fact |
| conflict_group_id | no | opaque group identifier | lifecycle operation | conflict-resolution workflow | groups competing facts | preserves conflict without silent choice | score/ranking |
| created_at | yes | datetime | system | audit/history | immutable creation timestamp | technical history | customer confirmation proof |
| updated_at | yes | datetime | system | audit/history | last metadata/state update | operational traceability | complete audit trail |

## 4. Field semantics

### 4.1 fact_id
Immutable system identity. No business meaning is encoded into the identifier.

### 4.2 customer_id
The only ownership root. A Profile Fact is never owned by a Case, Recommendation, Sale, or Feedback record.

### 4.3 attribute_key
Must come from an approved attribute dictionary. The first implementation slice should begin only with attributes that have a real consumer, such as skin_profile, hair_profile, scalp_profile, and age_range where reusable age information is actually required.

This is a contract candidate, not permission to add all fields. Each attribute must pass the same consumer test.

concerns is deliberately excluded from automatic conversion to Profile Fact because the current repository uses it as both persistent customer context and explicit current consultation input. Its semantics must be resolved separately before promotion into a durable fact.

### 4.4 value
Carries the attribute value. The value format is attribute-specific and must be defined by the Data Dictionary before implementation.

It must not encode source, lifecycle, audit history, or an inferred medical diagnosis.

### 4.5 value_state
Canonical vocabulary:
- KNOWN
- UNKNOWN
- PREFER_NOT_TO_SAY
- NOT_APPLICABLE

KNOWN means a usable value has been established through the approved promotion/recording process. The other states are meaningful and must not be collapsed into null.

### 4.6 source
Canonical provenance:
- CUSTOMER
- SELLER
- SYSTEM
- IMPORTED
- OTHER

OTHER is temporary and controlled: it requires source_description and later review/normalization. It is not a permanent catch-all.

Source is provenance, not permission.

### 4.7 recorded_at
System-generated timestamp for when the fact record was recorded. Historical facts remain traceable after they become STALE, SUPERSEDED, REVOKED, or CONFLICTED.

### 4.8 status
Canonical lifecycle/status:
- ACTIVE — currently usable.
- STALE — potentially useful but requires review before treating as current.
- SUPERSEDED — replaced by a newer fact.
- REVOKED — explicitly withdrawn.
- CONFLICTED — competing values require resolution.
- UNKNOWN — no usable value is established.

CANDIDATE and CONFIRMED are intentionally absent. Confirmation/promotion is an authorization decision/event, not a second lifecycle vocabulary.

### 4.9 review_due_at
Optional and policy-driven. It exists only when an attribute's freshness policy requires a review point. No universal TTL is defined here.

### 4.10 origin_case_id
Optional traceability to the Case that supplied the information. It does not make a Case the owner of the fact and does not turn Current Need into Profile Fact automatically.

### 4.11 supersedes_fact_id
Optional link from a newer fact to the prior fact it replaces. The prior record remains historical and becomes SUPERSEDED through an explicit lifecycle operation.

### 4.12 conflict_group_id
Optional grouping for competing values. Conflict must be visible and resolvable; the system must not silently choose a value merely because it was recorded later.

### 4.13 created_at / updated_at
Technical record timestamps. Material changes require audit information; these fields alone are not the audit trail.

## 5. Write rules

### Allowed creation
A Profile Fact may be created only when:
1. the information is intended to remain useful beyond the current Visit/Case; and
2. the value has been explicitly confirmed by the customer or recorded by an authorized operator under the approved promotion rule.

### Not sufficient for creation
The following do not by themselves create a Profile Fact:
- today's Current Need;
- an unconfirmed observation;
- a purchase;
- a recommendation;
- a Smart Summary;
- an inferred medical condition;
- a generic operator note.

### Updates
A material change must preserve the prior historical state. The implementation must not silently overwrite the old fact in a way that destroys provenance or lifecycle history.

### Conflict
When two values compete and resolution is unavailable:
- preserve both records;
- mark the relevant facts CONFLICTED;
- preserve provenance;
- require authorized resolution before treating one as the current reusable value.

### Revocation
Revocation changes usability state; it does not erase the historical audit requirement.

## 6. Read rules

### Customer profile
The profile view may expose current ACTIVE facts and relevant STALE facts with a review indicator. It must surface unresolved conflict rather than present a conflicted or revoked fact as current truth.

### Recommendation
Recommendation may consume only an approved read projection of eligible Profile Facts.

The adapter must be read-only, deterministic with respect to selected facts, explainable, and non-mutating.

This contract changes no scoring formula, ranking formula, eligibility rule, evidence gate, or hard gate.

### Smart Summary
Smart Summary may summarize Profile Facts but remains derived and cannot promote itself into a Profile Fact.

## 7. Edit / delete / audit behavior

The fact record itself is not the complete audit system.

A later audit/timeline slice must record material actions with actor, timestamp, old value/state, new value/state, and reason/action context.

Logical lifecycle operations such as SUPERSEDED or REVOKED are preferred when historical traceability is required.

Physical deletion is governed by applicable retention/privacy policy and is not a shortcut for ordinary editing.

## 8. Relationships deliberately excluded

This contract does not define Preference, Constraint/Safety Signal, Product Interaction, Outcome, Follow-up, generic Record, Visit/Consultation entity, Smart Summary storage, or recommendation/scoring/evidence changes.

Those concepts remain governed by their existing evidence status.

## 9. Migration boundary

No migration is authorized.

Before any migration design, the implementation review must answer:
1. Which existing Customer fields can be safely mapped to Profile Facts?
2. Which values lack sufficient provenance and therefore remain legacy/unpromoted?
3. How will historical values be preserved?
4. How will current concerns remain distinguishable from Current Need?
5. What happens to null/empty legacy values?
6. How will recommendation behavior remain equivalent before and after the adapter is introduced?

No automatic backfill may manufacture confirmation or provenance that the repository does not possess.

## 10. Acceptance tests required before implementation approval

The next implementation gate must prove at minimum:
1. create a known Profile Fact for a Customer;
2. reject/handle invalid value_state/source according to contract;
3. record source and recorded_at;
4. preserve an older fact when a newer fact supersedes it;
5. represent an unresolved conflict without silent winner selection;
6. represent STALE without deleting history;
7. revoke a fact without erasing its history;
8. require confirmation/authorized promotion rather than auto-promoting Current Need;
9. ensure purchase/recommendation/Smart Summary do not create facts;
10. read only eligible facts into Recommendation context;
11. demonstrate no scoring/eligibility/evidence-gate regression;
12. enforce existing authentication/RBAC rather than creating bypass roles.

These are acceptance criteria for the future implementation; they are not tests to be coded in this gate.

## 11. Gate

PROFILE FACT SCHEMA CONTRACT = DRAFT

Current conclusion:
- Proven capability gap: YES
- Minimum structured capability: Profile Fact only
- Exact fields: defined above for review
- New Preference/Safety/Outcome/Follow-up model: not justified
- Migration: BLOCKED
- Code: BLOCKED
- UI: BLOCKED
- Recommendation/Scoring/Evidence Gates: FROZEN

Approval required before implementation:
- APPROVE AS WRITTEN
- APPROVE WITH CHANGES: section/field
- REJECT: section + reason