# ProfileFact → Recommendation Adapter Reality Gate v0.1 — 2026-09

## Gate purpose

Determine, from the current HBI master code, whether Recommendation now has a proven need for a ProfileFact read-only adapter/projection.

This gate is an integration reality audit. It authorizes neither a recommendation rewrite nor a scoring change.

## Evidence inspected

Master at:

- `099ff8c4c57c15d2ee01d2e230b0212cadb3a453`

Relevant runtime components:

- `app/services/customer_service.py`
- `app/api/routers/recommendations.py`
- `app/services/recommendation_service.py`
- `app/models/customer.py`
- `app/models/profile_fact.py`

## Current reality

### 1. Recommendation already receives a Customer projection

`CustomerService.build_recommendation_profile()` currently projects exactly these persisted Customer fields:

- `skin_profile`
- `hair_profile`
- `scalp_profile`
- `age_range`
- `concerns`

The recommendation router then merges this saved Customer context with the current request and sends the merged profile to `RecommendationFacade.generate()`.

### 2. ProfileFact v0.1 currently covers the same five attribute keys

ProfileFact v0.1 fixes its first-slice vocabulary to:

- `skin_profile`
- `hair_profile`
- `scalp_profile`
- `age_range`
- `concerns`

Therefore, at this gate, ProfileFact does not introduce a new recommendation input dimension.

### 3. RecommendationService has no ProfileFact consumer

`RecommendationService.generate_recommendations()` consumes the supplied `customer_profile` dictionary. It does not query ProfileFact and contains no ProfileFact adapter/projection.

### 4. Existing recommendation gates are independent of ProfileFact

The current recommendation path retains its existing decision logic, including:

- Case ownership
- Need normalization
- medical-context hard gate
- product identity/active filtering
- inventory requirement
- evidence QA filtering
- claim-boundary handling
- HIGH/CRITICAL conflict handling
- existing scoring and eligibility mapping

No ProfileFact data currently enters these gates.

## Adapter necessity decision

**RESULT: ADAPTER NOT YET PROVEN NECESSARY.**

Reason:

1. The current ProfileFact vocabulary is exactly the same five dimensions already projected from Customer.
2. The existing Recommendation path has a working Customer projection boundary.
3. Introducing an adapter now would require defining precedence between legacy Customer values and versioned ProfileFact values without a proven consumer requirement.
4. It would also require defining behavior for multiple active facts, provenance differences, STALE/CONFLICTED states, and revocation in recommendation context.
5. None of those policies is currently required by an identified Recommendation consumer in the repository.

This is a capability-preservation decision, not a rejection of ProfileFact. ProfileFact remains available for future consumers that demonstrate a concrete need for versioning, provenance, lifecycle, or revocation semantics.

## Required future trigger for an adapter

An adapter becomes justified only when a concrete consumer requirement demonstrates that the current Customer projection cannot safely represent the required behavior.

At that point, a separate contract must define at minimum:

1. **Source precedence** between Customer and ProfileFact.
2. **Active selection** and deterministic behavior when multiple active facts exist.
3. **Revocation semantics** — revoked facts must never enter recommendation context.
4. **STALE/CONFLICTED semantics** — neither may silently become an ordinary trusted input.
5. **Consent enforcement** consistent with ProfileFact lifecycle rules.
6. **Provenance visibility** where it materially affects explainability.
7. **No write-back** from Recommendation into ProfileFact.
8. **Regression invariants** proving unchanged scoring, product eligibility, evidence gates, and safety/medical hard gates.

## Explicitly unchanged

This gate authorizes no changes to:

- Recommendation scoring
- Need normalization
- product eligibility
- evidence gates
- safety/medical handling
- Recommendation schema
- Customer legacy fields
- ProfileFact schema
- migration/backfill
- frontend/UI

## Gate outcome

```text
ProfileFact Contract              = MERGED
ProfileFact Implementation        = MERGED
ProfileFact Integration Gate      = MERGED
Recommendation Adapter Need       = NOT PROVEN
Recommendation Adapter            = NOT AUTHORIZED
Recommendation                   = FROZEN
Scoring                          = FROZEN
Evidence Gates                   = FROZEN
```

## Next architectural gate

The next useful step is not an adapter implementation.

The next gate is a **Consumer Profile UX / write-boundary reality audit**: verify how the real customer-intake workflow can create or update ProfileFact through the existing Customer workflow while preserving consent, ownership, auditability, and the fast gallery intake experience.

Any future recommendation adapter must remain behind a new explicit contract and evidence gate.
