# HBI ProfileFact Write Contract v0.2

**Status:** Documentation Contract — implementation not authorized  
**Baseline Master:** `032e14ad031007616dfea6c678a559bf2f48c040`

## Decision Matrix

| ID | Current Reality | Contract Decision | Status | Evidence | V1 Consequence |
|---|---|---|---|---|---|
| W1 | `ProfileFactService.create` creates ACTIVE facts after ownership + storage-consent checks. | Durable save means an explicit ProfileFact CREATE action for one supported key, with valid state, provenance, actor/audit context. | LOCKED | `app/services/profile_fact_service.py` | Durable save is explicit. |
| W2 | CREATE/SUPERSEDE/REVOKE accept authorized customer identity and actor/audit fields; service does not independently enforce an actor-role matrix. | Ownership is mandatory. Exact actor-role policy remains an API/application boundary decision. | LOCKED | ProfileFactService | No unsupported role claims. |
| W3 | CREATE, SUPERSEDE and LIST_ACTIVE require customer storage consent; REVOKE does not. | Preserve these existing consent semantics. | LOCKED | ProfileFactService | Consent remains explicit. |
| W4 | States are KNOWN, UNKNOWN, PREFER_NOT_TO_SAY, NOT_APPLICABLE; KNOWN requires non-empty value. | All four are first-class states. | LOCKED | model + service constraints | No forced answer. |
| W5 | SUPERSEDE creates a new ACTIVE row, links supersedes_fact_id, marks prior row SUPERSEDED. | Edit means versioning, not overwrite. | LOCKED | ProfileFactService | History retained. |
| W6 | REVOKE marks the row REVOKED and writes mutation audit. | Revoke is lifecycle action, not deletion. | LOCKED | ProfileFactService | Historical record retained. |
| W7 | Mutations append MutationLog with actor/action/target/before/after/reason/resulting state. | Durable mutations require audit evidence. | LOCKED | MutationLogService calls | No silent writes. |
| W8 | Five keys exist: skin_profile, hair_profile, scalp_profile, age_range, concerns. | V1 permits only these keys. | LOCKED | PROFILE_FACT_KEYS + DB constraint | No new ontology. |
| W9 | Customer has legacy profile/context fields; ProfileFact is separate and no sync/precedence contract is proven. | Coexistence without automatic synchronization, migration, or precedence. | LOCKED | current models + Phase 0/1 reality | Legacy behavior unchanged. |
| W10 | Quick intake captures today's concerns/optional skin profile and may create a Case; no automatic ProfileFact write path is proven. | Today's need remains Case data unless explicit durable-fact action occurs. | LOCKED | current intake boundary | Fast intake preserved. |
| W11 | LIST_ACTIVE returns owned ACTIVE facts after consent. | Read only; no recommendation implication. | LOCKED | ProfileFactService | No recommendation change. |
| W12 | No ProfileFact→Recommendation adapter is proven. | Recommendation consumption is deferred. | DEFERRED | Phase 0/1 reality | No scoring/recommendation change. |
| W13 | No automatic intake→ProfileFact mapping/write is proven. | Automatic promotion is deferred. | DEFERRED | current runtime | No hidden writes. |

## Write Boundary

A durable write requires: identified Customer → authorized caller for that Customer → required consent → one supported key → valid value state → appropriate provenance → CREATE or SUPERSEDE through the existing service → mutation audit.

A Case's current need is not automatically a durable ProfileFact.

## Actions

- **CREATE:** new ACTIVE fact; ownership + storage consent required.
- **SUPERSEDE:** new ACTIVE version; prior ACTIVE fact becomes SUPERSEDED; history retained.
- **REVOKE:** selected fact becomes REVOKED; ownership required; no physical deletion; current service does not require fresh consent.
- **LIST_ACTIVE:** returns ACTIVE facts for an owned customer after consent; no mutation.

## Consent / Ownership

Target ownership is a hard boundary: authorized customer identity must equal target customer identity.

Storage consent gates CREATE, SUPERSEDE and LIST_ACTIVE.

`provenance=SELLER` or `SYSTEM` does not itself prove an authorization policy. A future API/application contract must define actor-role permissions explicitly.

## Value State

| State | Meaning |
|---|---|
| KNOWN | Supported fact with non-empty value. |
| UNKNOWN | Currently not known. |
| PREFER_NOT_TO_SAY | Customer chooses not to provide it. |
| NOT_APPLICABLE | Fact does not apply. |

## Customer vs Case

**Case/current need:** today's consultation context, immediate goal and temporary concern.

**Durable ProfileFact:** information intentionally retained for reuse in future interactions.

Automatic promotion, synchronization and read precedence are outside V1.

## Five-Key Mapping

- `skin_profile` — durable skin profile information explicitly retained.
- `hair_profile` — durable hair profile information explicitly retained.
- `scalp_profile` — durable scalp profile information explicitly retained.
- `age_range` — durable age-range information explicitly retained.
- `concerns` — durable recurring concern explicitly identified as reusable profile information.

A today's-only concern remains Case data unless explicitly retained as a durable fact.

## Legacy Coexistence

This contract does not migrate, backfill, synchronize, or declare precedence between legacy Customer fields and ProfileFact. Conflict/read-precedence requires a separate evidence-backed contract.

## Audit

Durable mutations must preserve existing MutationLog evidence: actor_id, actor_role when available, action, target, before/after snapshots, reason when supplied, and resulting state.

## Deferred

ProfileFact→Recommendation; automatic intake→ProfileFact; legacy migration/backfill/sync; read precedence/conflict resolution; new keys/entities/tables; UI; questionnaire; seller workflow; recommendation/scoring/eligibility/evidence changes; expanded actor-role policy.

## Future Smallest Implementation Slice

If separately authorized: one explicit authenticated durable-profile action using existing ProfileFactService + MutationLogService, with tests for owned+consent CREATE, foreign customer rejection, missing consent, invalid KNOWN, SUPERSEDE versioning, REVOKE lifecycle/audit, and LIST_ACTIVE filtering.

**This document is not implementation authorization.**

## Evidence

Baseline implementation: `app/services/profile_fact_service.py`, `app/models/profile_fact.py` at Master `032e14ad031007616dfea6c678a559bf2f48c040`.

PR #204 merged as `09a7e0325a3f92c875ffa275ca6c579f3eed7877`; HBI CI #779 / `35916695369` and Auto Tasks #149 / `35916695523` succeeded on that merge SHA.

**Contract status: READY FOR INDEPENDENT REVIEW AND PO DECISION.**
