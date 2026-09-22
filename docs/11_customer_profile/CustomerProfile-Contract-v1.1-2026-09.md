# Customer Profile Contract v1.1 — 2026-09

Status: DRAFT FOR PO APPROVAL

Scope: customer-profile vocabulary and behavioral contract only.

This document makes no schema, UI, recommendation, scoring, or migration change.

## 1. Contract objective

Customer Profile v1.1 defines a small, explicit vocabulary for a living customer file.

The file must distinguish:
- what the customer needs today;
- what is a relatively stable profile fact;
- what the customer prefers;
- what may constrain or affect safe product/service handling;
- what happened with a product/service interaction;
- what result was reported;
- what the system derives as a summary.

The five UI boxes remain presentation projections and are not domain entities.

## 2. Canonical vocabulary

### Customer
The person/entity to whom the profile belongs. Identity data remains in the existing Customer core.

### Visit / Consultation Session
A time-bounded customer interaction. Use it for information relevant to the current visit: need today, answers collected for today's consultation, consultation-specific observations, and evidence gaps.

A Case may remain the operational recommendation/case container, but it is not the universal replacement for complete customer-profile history.

### Current Need
The customer's objective for the current Visit/Case.

Examples: hydration, acne/oiliness, pigmentation/dullness, hair/scalp concern, makeup, or specified product purchase.

Rule: Current Need is visit-scoped. It is not automatically a permanent Customer fact.

### Profile Fact
A customer attribute intended to remain useful beyond one visit.

Every future structured Fact should conceptually carry:
- attribute_key
- value
- value_state
- source
- recorded_at
- lifecycle/validity state

Recommended value_state vocabulary:
- KNOWN
- UNKNOWN
- PREFER_NOT_TO_SAY
- NOT_APPLICABLE

null, omission, and UNKNOWN are not interchangeable.

### Preference
A customer preference that can guide service or product presentation.

Examples: preferred texture, fragrance/no-fragrance, brand, shade/color, size/volume, or budget preference.

A Preference is not automatically a safety prohibition. It may be absent, changed, or overridden by the current request.

### Constraint / Safety Signal
A condition or limitation that may affect what can appropriately be recommended, sold, or used.

It must be distinguishable from ordinary Preference.

Conceptually it carries:
- constraint_key
- value
- source
- severity
- recorded_at
- state/validity

Examples include a documented prior reaction or explicitly stated avoidance relevant to safe handling.

The system must not infer medical diagnoses from ordinary profile answers.

### Product Interaction
A recorded relationship between the customer and a product/service event.

Minimum conceptual interaction types:
- VIEWED
- RECOMMENDED
- PURCHASED
- USED
- REPORTED

Purchase alone is evidence of a transaction, not proof of preference, satisfaction, or successful outcome.

### Outcome
A post-interaction result or customer-reported response.

Outcome is separate from Product Interaction.

For MVP, Outcome is included as a data concept and contract, but implementation is gated to a small pilot-ready slice rather than a broad outcome/scoring system.

Minimum conceptual fields:
- interaction reference;
- outcome type;
- customer-reported result;
- safety flag where applicable;
- recorded time;
- source.

### Derived Insight / Smart Summary
A generated projection from structured records.

Rules:
1. It is not source-of-truth.
2. It is not a Profile Fact.
3. It must be regenerable.
4. It must be traceable to underlying records.
5. It must never silently promote an inference into a permanent customer attribute.

## 3. Status and freshness

Freshness is attribute-specific. A single global TTL for the entire profile is rejected.

Proposed status vocabulary:
- ACTIVE — currently usable.
- STALE — potentially useful but requires review before being treated as current.
- SUPERSEDED — replaced by a newer value.
- REVOKED — explicitly withdrawn.
- CONFLICTED — competing values require resolution.
- UNKNOWN — no usable value is established.

Proposed freshness classes:

| Data | Default freshness treatment |
|---|---|
| Identity/contact | stable; change-driven |
| Age/age-range | time-sensitive; review when needed |
| Skin/hair status | review periodically and whenever customer reports change |
| Current Need | expires with Visit/Case |
| Preference | valid until changed/rejected; no arbitrary short TTL |
| Safety Constraint | review on change; stale status must trigger caution |
| Product Interaction | historical event; does not expire |
| Outcome | historical event; does not expire |
| Smart Summary | regenerated from current underlying records |

Freshness controls whether a record is safe/useful to reuse; it does not erase historical records.

## 4. Provenance

For structured profile information, source must be distinguishable.

Proposed source vocabulary:
- CUSTOMER
- SELLER
- SYSTEM
- IMPORTED
- OTHER — reserved for a temporary, explicitly documented source that does not fit the controlled sources; it requires a source description and must be reviewed/normalized before it is treated as a durable provenance category.

SYSTEM may generate a derived value, but a derived value must not be presented as customer-confirmed fact without an explicit confirmation event.

Where two values conflict, the system records the conflict and preserves provenance instead of silently choosing one.

## 5. Promotion rules

Information collected during a Visit does not automatically become a permanent Profile Fact.

Promotion requires:
1. explicit customer confirmation; or
2. explicitly authorized operator action with audit information.

A purchase does not automatically create a Preference.

A recommendation does not automatically create a Preference.

A Smart Summary does not automatically create a Fact.

## 6. Observation versus fact

An operator observation may be useful for the current consultation, but it is not automatically a durable customer fact.

The intended distinction is:
observation -> source/time/context -> optional confirmed fact

This prevents temporary consultation language from becoming permanent customer truth.

## 7. Customer and seller permissions

These are target capabilities for the customer-profile feature. They do not create new roles, bypass existing authorization, or override the application's current authentication/RBAC model.

### Customer
Subject to authentication/capability, customer may:
- view profile information designated customer-visible;
- correct their own profile information;
- withdraw or revise preferences;
- request correction of inaccurate information;
- provide or withdraw consent where applicable.

### Seller / authorized operator
Seller may:
- record consultation information needed for service;
- update operationally relevant profile information within role scope;
- record interactions and outcomes;
- correct data with an auditable reason;
- view only information required for the operational role.

### Manager / QA / authorized reviewer
May:
- review corrections and sensitive records within authorization;
- resolve conflicts;
- inspect audit history;
- perform controlled administrative corrections.

### Audit principle
For material edits, retain:
- actor;
- timestamp;
- old value;
- new value;
- reason/action context.

Deletion follows the system retention/privacy policy; logical withdrawal/supersession is preferred where historical traceability is required.

## 8. Consent rules

Consent handling is jurisdiction- and policy-dependent. This Contract does not assume a particular country's law or prescribe a universal legal consent threshold. The implementation must follow applicable law, regulation, and the organization's privacy/consent policy; where those require consent, the system must support recording it.

Consent must be purpose-specific where data is sensitive.

Ordinary operational profile data can be collected when necessary for the requested retail/consultation service, subject to the application's applicable privacy policy.

Sensitive categories include:
- health-related information;
- prior adverse reaction information;
- medication-related information;
- pregnancy-related information;
- photographs or other biometric/identifying media.

Rules:
1. Collect only when necessary for a legitimate service/safety purpose.
2. Where applicable law or policy requires consent, obtain the required consent before storing sensitive information.
3. Record consent purpose and time when consent is collected.
4. Allow withdrawal where applicable.
5. Withdrawal stops future use according to policy while preserving legally/operationally required audit records.
6. Sensitive data must not be inferred merely because another field suggests it.

The application must never represent a seller's inference as a customer-confirmed medical fact.

## 9. MVP decision

Core now:
- Customer
- Visit/Case context
- Current Need
- Profile Fact vocabulary
- Preference vocabulary
- Constraint/Safety vocabulary
- Product Interaction vocabulary
- Provenance
- Status/freshness semantics
- permission/audit rules
- Consent semantics

Pilot-ready but deliberately narrow:
- Outcome — record information only; it has no effect on scoring, recommendation eligibility, evidence gates, or automatic Promotion.

Derived only:
- Smart Summary / Derived Insight

No scoring, recommendation eligibility, evidence-gate, or automatic Promotion rule changes are part of v1.1. Pilot Outcome records are informational only.

## 10. Five-box projection

| UI box | Contract source |
|---|---|
| Need Today | Current Need + Visit/Case |
| Skin/Hair Status | Profile Facts + current consultation answers |
| Preferences/Constraints | Preferences + Constraints |
| Key Product Experience | Product Interactions + Outcomes |
| Smart Summary | Derived projection |

The boxes are not persisted as five duplicate Customer columns.

## 11. Acceptance gates

Contract v1.1 is ready for implementation only when the PO approves:
- canonical vocabulary;
- status/freshness rules;
- Preference vs Constraint boundary;
- customer/seller permissions;
- Outcome MVP scope;
- sensitive-data Consent rules.

After approval, implementation proceeds additively:
1. contract/data dictionary;
2. minimum structured profile records;
3. audit/timeline;
4. read projection;
5. progressive intake behavior;
6. recommendation adapter, read-only.

Each slice requires tests and CI before the next slice.

## 12. Explicit freeze

Until this Contract is approved:
- no schema migration;
- no Customer model redesign;
- no new profile UI;
- no recommendation/scoring change;
- no automatic profile promotion;
- no Smart Summary persistence as source-of-truth.

PO approval status: PENDING

Suggested decision format:
- APPROVE AS WRITTEN
- APPROVE WITH CHANGES: section
- REJECT: section + reason
