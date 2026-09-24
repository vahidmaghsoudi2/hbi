# HBI Consultation Next Question Vertical Slice 001 — Evidence

## Baseline Reality

Master baseline: `d1895be588de510c04471232dc7a89350749c60f`.

Verified repository facts:
- `RecommendationService` derives canonical Needs from consultation factors and calculates need-match against `ProductKnowledge.known_use_cases`.
- Canonical customer Needs include `hydration` and `sun_protection`.
- `ProfileFactContextService` applies current consultation > trusted ACTIVE ProfileFact > legacy Customer precedence.
- UNKNOWN-family ProfileFacts are preserved and do not fall back to legacy values.
- Multiple ACTIVE ProfileFacts for one key become an explicit conflict projection.
- `Case.evidence_gaps` already exists as a nullable String.
- `ReasoningEngine` returns computed-only reasoning and was not changed.
- `MatchScoringEngine` owns the frozen score formula and was not changed.

Therefore the smallest real Skin factor is the existing `concerns` input surface, mapped deterministically to canonical Needs.

## Implemented Slice

```
Owned Case
  -> ProfileFactContextService
  -> missing/UNKNOWN/CONFLICTED concerns
  -> one deterministic bounded question
  -> answer stored in Case.evidence_gaps
  -> Case answer projected as current consultation input
  -> existing /recommendations/generate
  -> existing Need normalization
  -> existing eligibility/ranking/scoring
```

Question:
- id: `skin.primary_need.v1`
- factor: `concerns`
- options: `hydration`, `sun_protection`
- mode: `MISSING_INPUT` or `CLARIFICATION`
- no LLM generation.

The Evidence Gap is case-traceable by `case_id + question_id` and records a RESOLVED state when the answer is captured.

## Decision Effect

The acceptance fixture uses two verified/active products with approved evidence:
- one with canonical use case `hydration`
- one with canonical use case `sun protection`

Answer `hydration` makes the hydration product the eligible recommendation.
Answer `sun_protection` makes the sunscreen product the eligible recommendation.

Both runs call the same existing recommendation endpoint and the same frozen scoring/ranking/eligibility path. The only decision input changed is the current Case consultation answer.

## Required Boundaries

- No new database table, column, or migration.
- No scoring formula change.
- No ranking formula change.
- No eligibility logic change.
- No evidence scoring change.
- No ReasoningEngine redesign.
- No automatic ProfileFact write.
- No questionnaire engine.
- No AI question generation.
- No Home/UI redesign.
- No unrelated domain changes.

## Test Coverage

`tests/test_consultation_next_question_vertical_slice_001.py` covers:
1. missing input -> one bounded question
2. known input -> no question
3. bounded answer validation
4. answer persisted in Case
5. A/B -> different existing recommendation outcome
6. current consultation > ProfileFact
7. UNKNOWN -> clarification without legacy fallback
8. duplicate ACTIVE -> clarification boundary
9. no automatic ProfileFact write
10. frozen scoring formula

Targeted command:

```
pytest tests/test_consultation_next_question_vertical_slice_001.py -q
```

Full regression:

```
pytest -q
```
