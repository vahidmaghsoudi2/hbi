# Perfume Intelligence — Research Domain Foundation v0.1

## Document status

```text
Status: RESEARCH / DOMAIN FOUNDATION
Architecture: NOT ACCEPTED
Contract: NOT AUTHORIZED
Implementation: NOT AUTHORIZED
Repository Claims: UNVERIFIED UNLESS SEPARATELY AUDITED
```

## Purpose

Preserves domain concepts, risks and proposed boundaries for a future HBI perfume/fragrance capability.

Not architecture. Not data contract. Not implementation specification.

## Vision

Support human operator and customer with attributable product information, preferences, context, evidence, uncertainty and outcomes into an explainable shortlist.

Must not claim: “This is the best perfume for you.”

Intended future output: candidates for review and testing based on stated preference, context, available information and visible uncertainty.

## Domain distinctions

```text
Product Fact ≠ Manufacturer Claim ≠ Olfactory Interpretation
≠ Performance Observation ≠ Customer Preference ≠ Customer Outcome ≠ AI Inference
```

## Proposed conceptual layers

```text
Product Identity → Product Facts → Olfactory Knowledge → Performance Evidence
→ Customer Taste → Usage Context → Eligibility → Compatibility
→ Explainable Shortlist → Sampling / Human Review → Observed Outcome
```

## Product identity concepts (candidates only)

Brand, Official Product Name, Variant/Flanker, Concentration, Volume, GTIN/Barcode, Market/Region, Packaging Version, Batch, Product Form, Authenticity Status, Inventory Status, Lifecycle Status.

Not confirmed HBI fields or entities.

## Olfactory knowledge candidates

Fragrance Family, Subfamily, Accord, Note, Note Role, Top/Heart/Base, Descriptor, Derived Olfactory Profile.

Descriptor examples (require domain approval before use): Sweet, Fresh, Clean, Warm, Dry, Spicy, Smoky, Powdery, Musky, Woody, Floral, Green, Aquatic, Fruity, Creamy, Resinous, Earthy, Leather-like.

## Performance boundaries

```text
Longevity ≠ Projection ≠ Sillage ≠ Intensity
Concentration ≠ Performance
```

Context candidates (not mandatory V1): Skin/Clothing/Blotter, Indoor/Outdoor, Temperature, Humidity, Spray Count, Observation Window, Observer, Date, Source Type.

## Context / marketing-gender boundary

Season, Occasion, Environment, Time of Day, Weather, Formality, Personal Use/Gift = Context Signals or preferences — not universal product facts, not automatic hard filters.

Manufacturer Marketing Gender ≠ Customer Identity ≠ Preference ≠ Olfactory Compatibility. Metadata only candidate; not automatic exclusion.

## Customer taste / history (candidates)

Preferences, avoidances, deal-breakers, intensity/projection/longevity desires, budget, reference perfumes, occasion/environment, gift/self.

Events must stay distinct: Recommended, Sampled, Purchased, Used, Liked, Disliked, Satisfied, Unsatisfied, Repurchased, Returned, Discomfort Reported; Liked Opening ≠ Liked Dry-down; Purchased ≠ Liked.

## Safety boundary

May handle documented ingredients, warnings, allergen declarations, restrictions, customer-reported discomfort, sampling consent, escalation.

Must not: medical diagnosis, allergy diagnosis, medical clearance, pregnancy medical advice, universal safety guarantee.

## Evidence boundary

```text
AI Research → Assertion → Evidence → Review → Knowledge
Not: AI → Truth
```

Unknown ≠ Negative. Conflict ≠ Low Confidence. Documentation ≠ Behavior.

## Eligibility / recommendation boundary

```text
Product Eligibility ≠ Customer Decision Readiness ≠ Customer × Product Compatibility
```

Path: Eligibility → Compatibility → Shortlist → Explanation → Human Review/Sampling → Outcome.

At Foundation stage: numeric scoring deferred; automatic ranking/recommendation/learning not authorized.

## Similarity

Deferred until stable taxonomy, verified identity, structured profile, definition, constraints, evidence, explainability, pilot outcomes.

## Scope limitation

This Foundation is not proof that current HBI has, lacks or requires any particular model, table, schema, API, lifecycle, contract or runtime behavior.
