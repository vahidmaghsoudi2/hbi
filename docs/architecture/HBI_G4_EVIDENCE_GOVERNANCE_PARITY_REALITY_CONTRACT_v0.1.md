# HBI G4 — Evidence Governance Parity — Reality Contract v0.1

**Status:** Implementation candidate on branch `gpt2/evidence-truth-g2-g4`  
**Baseline:** `master @ e110d2c46dfa966009118a0aee6d040ee932ea28`  
**Authority:** P4 Governance Contract v1

## 1. Reality confirmed

Evidence mutation endpoints already enforce role authorization, but the Evidence domain did not have an audit surface equivalent to ProductMutationLog.

The gap was therefore governance parity, not a missing Evidence lifecycle.

## 2. V1 decision

Add one append-only Evidence mutation log with the same audit dimensions already established for Product mutations.

Each record carries:

- actor_id
- actor_role
- timestamp
- action
- target_entity
- target evidence_id
- product_id
- before_state
- after_state
- diff
- reason where applicable
- resulting_state
- correlation_id

## 3. Audited mutations

The V1 implementation records:

- CREATE
- RESEARCH_DRAFT_CREATE
- VERIFY
- RESOLVE_CONFLICT

Internal/system-created Evidence is attributed to `system` when no authenticated actor exists.

## 4. Permission boundary

Mutation routes remain protected by the existing roles:

- Reviewer/QA
- PO
- Admin

Audit read endpoints are protected by the same governance roles.

Unauthorized requests continue to resolve through the existing authentication/authorization boundary.

## 5. Integrity rules

- Evidence QA remains distinct from Product QA.
- Evidence readiness remains the Product approval/activation gate.
- Product lifecycle fields remain untouched.
- Conflict resolution remains explicit and reason-bearing.
- No physical Evidence deletion is introduced.
- Recommendation scoring remains untouched.
- Product A–D remain untouched.

## 6. Audit visibility

Two read surfaces are provided:

- audit for one Evidence record
- audit for all Evidence mutations belonging to one Product

This does not replace ProductMutationLog. The logs remain domain-specific and can later be correlated through `correlation_id`.

## 7. Acceptance matrix

| Case | Expected result |
|---|---|
| Evidence create | CREATE audit row |
| Research Draft assertion | RESEARCH_DRAFT_CREATE audit row |
| Evidence verify | VERIFY audit row with before/after |
| Conflict resolution | RESOLVE_CONFLICT audit row with reason |
| unauthorized mutation | 401/403 |
| audit read without governance role | 403 |
| audit record | actor + role + target + product + timestamp |
| state mutation | before/after captured |
| resolution | explicit reason captured |
| Product status | unchanged |
| Product QA | unchanged |
| Recommendation scoring | unchanged |

## 8. Boundary

EvidenceMutationLog is an audit trail, not a second governance machine.

P4 remains the authority for Product approval and activation.

**NO ASSUMPTION / NO INVENTED DATA.**
