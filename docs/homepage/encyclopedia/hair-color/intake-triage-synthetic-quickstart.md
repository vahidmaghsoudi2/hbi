# Hair Color Intake/Triage — synthetic quickstart

This is the **current safe runtime surface**. It is not a color-recommendation engine.

## Public callable

`app.hair_color.consultation.run_consultation(request)` validates the contract and runs the fail-closed intake gate. The gate never emits color candidates, shade rankings, formulas, product equivalence, chemical/process parameters, or predicted outcomes.

For a UI caller, the combined public callable is \`run_consultation_persian(request)\`; it returns the validated consultation result and a Persian presentation object, and hardcodes execution authorization to false.\n\nThe standalone Persian presentation helper is:

`app.hair_color.persian_response_renderer.render_persian_response(response)`

It returns a small UI-safe object: title, explanatory message, missing field identifiers, generic next step, an empty options list, and `execution_authorized=False`.

## Response routing

| Status | User-facing meaning | Candidate options |
|---|---|---|
| `SAFETY_STOP_NO_EXECUTION_SUGGESTION` | Stop and qualified review | None |
| `OUT_OF_V1_SCOPE` | Outside current scope | None |
| `NEEDS_INFORMATION_OR_TEST` | Clarify missing/conflicting intake data | None |
| `NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW` | Evidence/knowledge gap; specialist review | None |
| `SYSTEM_REASONED_SUGGESTION` | Reserved contract state; renderer still does not present execution advice | None |

## Synthetic test

Run the narrow test suite in a repository environment:

```bash
pytest -q tests/test_hair_color_policy_gate_engine.py tests/test_hair_color_persian_response_renderer.py
```

The test data must remain synthetic. Passing these tests proves only the intake/triage and rendering contract—not specialist validity, real product chemistry, runtime integration, consultation readiness, or release acceptance.

## Activation gate for domain knowledge

Any knowledge bundle must remain inactive unless it has exact source/product identity, version/market and applicability metadata, claim-level evidence links, a recorded specialist approval, and publication-gate checks. This document does not authorize or define operational hair-color chemistry.

## Guarded case workflow (synthetic)

The separate `workflow_state_machine` module models the ten case states and rejects illegal shortcuts. Transition calls require a traceable event ID and matching case/target versions. The transition to `APPROVED_FOR_EXECUTION` requires both client acceptance and explicit execution consent. A safety-stopped case cannot resume; the restart helper creates a distinct case reference with incremented versions and returns it to incomplete intake.

Run the transition invariants:

```bash
pytest -q tests/test_hair_color_workflow_state_machine.py
```

This state model is not wired to a database, UI, or real execution service. The approval state is an abstract contract state only; no actual hair-color service is enabled.

## Knowledge-bundle provenance metadata validator (synthetic)

`app.hair_color.knowledge_bundle_provenance.validate_knowledge_bundle` checks exact product identity fields, source metadata, unique source/claim IDs, and claim-to-source links. It reports metadata readiness only. Even a synthetic bundle with an approval record remains `publishable=False` and `activation_allowed=False`; the validator has no activation/publication function and does not assess evidence quality or scientific validity.

Run its tests:

```bash
pytest -q tests/test_hair_color_knowledge_bundle_provenance.py
```
