# Customer → ProfileFact Write-Boundary & Intake UX Reality Gate v0.1 — 2026-09

## Gate purpose

Audit the real customer-intake path in HBI and determine whether the existing workflow can safely become the write boundary for ProfileFact without slowing the gallery intake or weakening consent, ownership, and audit controls.

## Master evidence

Audited master after PR #199:

- `752738db90a96151106838e7ea5801e5cdabe357`

Relevant path:

- `POST /api/v1/customers/guest`
- `POST /api/v1/customers/intake`
- `GET /api/v1/customers/recommendation-profile`
- `CustomerService.record_intake()`
- `CustomerService.build_recommendation_profile()`
- `ProfileFactService`

## Current intake reality

### Fast intake exists

The existing `/customers/intake` endpoint is explicitly designed for gallery quick intake and accepts:

- name
- optional mobile
- today's concerns
- consent
- optional skin profile
- guest flag
- optional case creation

It can reuse the authenticated customer identity and can create a Case for the visit.

### Important boundary already exists

The current code deliberately treats the consultation payload as today's case-scoped input when a Case is opened. It does not overwrite persistent Customer profile fields in that path.

This is a sound boundary for the gallery workflow: today's need can feed Recommendation without silently becoming permanent customer history.

### Current persistence gap

When `open_case=True`, `concerns` and `skin_profile` are passed to the recommendation profile but are not persisted as ProfileFact.

Therefore the existing intake flow is **not yet a safe ProfileFact write boundary** merely by adding a direct call to `ProfileFactService`.

Doing so would require deciding which intake fields represent durable customer facts versus temporary consultation context.

## Write-boundary decision

**RESULT: PROFILEFACT WRITE VIA CURRENT INTAKE IS NOT YET AUTHORIZED.**

The current workflow proves the correct UX entry point, but it does not yet prove the semantic write rule.

### Required semantic split

1. **Visit/current need**
   - remains Case-scoped
   - can feed Recommendation for the current Case
   - must not automatically become a durable ProfileFact

2. **Durable customer fact**
   - requires explicit user/customer or authorized seller action at the profile boundary
   - must pass ProfileFact consent and ownership checks
   - must be versioned/superseded rather than silently overwritten
   - must remain auditable

3. **Unknown / prefer not to say / not applicable**
   - are explicit ProfileFact states when a durable fact is intentionally recorded
   - are not inferred from an omitted quick-intake field

## UX implication

The gallery MVP should retain a two-speed workflow:

### Speed path

`New Customer → Today's Need → Case → Recommendation`

No durable ProfileFact write is implied by omission or by today's consultation input.

### Profile enrichment path

`Customer Profile → explicit fact → consent → ProfileFact write → audit`

This can be progressive and conditional. It should not turn the first visit into a long questionnaire.

## Authorization requirements for future write integration

Before code changes, a dedicated implementation contract must define:

- exact UI/action that means “save as customer fact”
- actor authorization mapping
- customer ownership binding
- consent behavior when consent is absent/withdrawn
- mapping from UI fields to the five ProfileFact attribute keys
- treatment of edits as supersession
- treatment of revoke
- audit event expectations
- whether a seller-entered fact is immediately ACTIVE or requires explicit customer confirmation
- how the existing Customer fields and ProfileFact coexist during migration-free operation
- regression proof that Case/current-need Recommendation behavior remains unchanged

## Explicitly preserved

- quick intake UX
- Case as current-need boundary
- existing Recommendation flow
- existing Customer projection
- ProfileFact contract
- ProfileFact service invariants
- scoring
- eligibility
- evidence gates
- safety/medical gates
- no automatic backfill
- no automatic conversion of today's consultation into durable profile history

## Gate outcome

```text
PR #199 Adapter Reality Gate      = MERGED
Recommendation Adapter            = NOT AUTHORIZED
Quick Intake Entry Point          = PROVEN
ProfileFact Direct Intake Write   = NOT YET AUTHORIZED
Case / Current Need Boundary      = PRESERVED
Recommendation                    = FROZEN
Scoring                           = FROZEN
Evidence Gates                    = FROZEN
```

## Next gate

Define the **ProfileFact Write Contract v0.1**: the smallest explicit customer-profile action that can create, supersede, or revoke a durable fact while preserving the fast gallery workflow.

No implementation is authorized until that write contract is accepted.
