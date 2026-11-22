# Hair Color Intake/Triage — synthetic quickstart

This is the **current safe runtime surface**. It is not a color-recommendation engine.

## Public callable

`app.hair_color.consultation.run_consultation(request)` validates the contract and runs the fail-closed intake gate. The gate never emits color candidates, shade rankings, formulas, product equivalence, chemical/process parameters, or predicted outcomes.

The Persian presentation helper is:

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
