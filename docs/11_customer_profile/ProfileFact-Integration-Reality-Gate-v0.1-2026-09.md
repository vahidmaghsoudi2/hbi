# ProfileFact — Integration Reality Gate v0.1
Date: 2026-09-23
Repository: vahidmaghsoudi2/hbi
Master merge SHA: f828a249a011af343d1d4b16388f0d5d1a9310fb

## Gate result

**PASS — schema/domain integration boundary verified.**
**POST-MERGE CI/RUNTIME = PENDING EVIDENCE.**
**Recommendation adapter = NOT AUTHORIZED / FUTURE GATE.**

## Evidence

ProfileFact implementation is present on master through the merge above.

The merge from `8223dd151ada8e6d832aa195ebc49af12cbf5652` to
`f828a249a011af343d1d4b16388f0d5d1a9310fb` is one commit ahead and changes only:

- `app/database.py`
- `app/models/__init__.py`
- `app/models/customer.py`
- `app/models/profile_fact.py`
- `app/services/profile_fact_service.py`
- `tests/test_profile_fact.py`

No recommendation-service/router/scoring/evidence file is part of this merge.

## Contract-to-implementation

- Fixed ProfileFact vocabulary: implemented.
- Customer foreign-key ownership: implemented.
- Explicit authorized-customer check on create/supersede/revoke/list: implemented.
- Consent gate for create/supersede/list: implemented.
- Revoke remains available after consent withdrawal: implemented and tested.
- Value-state validation and KNOWN non-empty rule: implemented.
- Provenance/status validation: implemented.
- ACTIVE-only supersession with immutable prior version state: implemented.
- Revoke excludes the fact from active projection: implemented.
- Audit uses existing MutationLogService with target_entity=ProfileFact: implemented and tested.
- Legacy Customer fields remain intact: verified in master.
- Automatic legacy Customer backfill: not introduced.
- Recommendation consumption adapter/projection: not introduced.

## Runtime/CI evidence status

The pre-merge HBI CI run #748 was green on the final PR head before merge.

For the exact merge SHA above, the available workflow query currently returns no associated workflow run. Therefore post-merge CI/runtime verification is **not claimed** by this gate.

## Boundary decision

ProfileFact is now an implemented, audited domain capability.

It is **not yet part of Recommendation input**. Any adapter/projection into Recommendation requires a separate integration contract and runtime evidence showing:

1. only authorized active facts are projected;
2. consent/revocation semantics remain effective;
3. existing Recommendation scoring, eligibility, evidence and safety gates remain unchanged;
4. recommendation output is explainable and regression-tested;
5. no write-back from Recommendation into ProfileFact occurs implicitly.

Until that evidence exists, Recommendation remains frozen with respect to ProfileFact.

## Next gate

**Recommendation Adapter / Projection Reality Gate** — design and prove the read-only boundary before implementation.
