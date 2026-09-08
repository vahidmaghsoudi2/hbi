# HBI — Independent Recommendation Factor Discovery

**Meeting / consultation record**  
**Date:** 2026-09-08  
**Mission:** Identify factors that should influence product Recommendation ranking inside the **current HBI Gallery / Inventory** (offline scope).  
**Rules for this stage:** No formula · No weight · No percentage · No implementation · Independent opinions · Do not close Issue #37 from this file.

**Related governance:**
- Issue #37 — Recommendation Parameter Weighting (OPEN / NOT AUTHORIZED)
- ADR-REC-INPUT-001 — input semantics (separate track)
- PR #36 — HOLD / DO NOT MERGE (not a precedent for factors or weights)

**Scope constraint (shared):**

```
Customer Need
      ↓
Available Products in HBI Gallery / Inventory
      ↓
Eligibility / Suitability
      ↓
Recommendation
```

Not a global market search engine in the current phase.

---

## How to append other team members

Add a new section below using the same format (max 20 numbered factors, most important first). Do not edit another member’s list without labeling it as a later revision.

---

## Member: Grok (xAI) — Independent contribution

**Stance:** Clinical-safety and evidence-first recommender for an offline gallery, not a popularity or advertising ranker. Commercial signals are secondary and must not override safety or suitability.

1. **Safety / contraindication fit** — product must not conflict with customer risks, allergies, or stated constraints; non-negotiable eligibility before ranking quality.
2. **Need–indication suitability** — match between customer need/condition and the product’s legitimate use context (dermatology / use-case fit).
3. **Active ingredients & formulation relevance** — presence and appropriateness of actives/vehicle for that need (not marketing claims alone).
4. **Strength of relevant verified evidence** — quality of evidence supporting benefits that matter for *this* need (not generic “has some evidence”).
5. **Product record trust (identity / QA)** — only products with trustworthy identity and acceptable QA status should rank as recommendable.
6. **Customer profile constraints** — skin/hair/scalp (and similar) profile limits that change suitability even when the headline need matches.
7. **Completeness of Product Knowledge for counselling** — enough structured knowledge to justify and explain the recommendation operationally.
8. **Sellable availability in HBI inventory** — offline gallery reality: cannot responsibly rank what cannot be fulfilled now (availability as eligibility/access, not “popularity”).
9. **Unresolved evidence conflict / unsafe claim boundary** — open conflicts or disallowed claim promotions should suppress or block confidence in ranking.
10. **Known adverse / exclusion signals in knowledge** — contraindications and exclusion reasons already captured in product knowledge.
11. **Operator / seller observed outcomes (local)** — structured experience with similar customers in *this* gallery context (signal, not substitute for evidence).
12. **Historical sales–return pattern for similar profiles** — if reliable local outcome data exists; weak or biased data must not dominate.
13. **Economic accessibility for the customer context** — price as a practical constraint on “best available,” not as a quality score.
14. **Regulatory / brand credibility only where it informs safety or authenticity** — brand prestige alone is not ranking value.
15. **Consumer satisfaction feedback (if governed and local)** — offline-governed feedback only; noisy external ratings stay low priority.
16. **Repeat-purchase or adherence proxy (local, if any)** — weak secondary signal of real-world acceptability.
17. **Market popularity / trend velocity** — commercial interest, not clinical priority for HBI’s core mission.
18. **Social / consumer web signals** — high noise; optional later signal, not a primary ranking basis offline.
19. **Out-of-gallery exception supply** — possible future *exception process*, not a current ranking factor among gallery candidates.
20. **Novelty or campaign-driven promotion** — lowest; must not outrank safety, suitability, ingredients, or verified evidence.

**Notes (non-weight):**
- Several items above may later be classified as Gate / Filter / Constraint rather than Score factors (especially 1, 5, 8, 9).
- This list is **not** a weight policy and does **not** authorize percentages.
- Independent of PO candidate priority order on Issue #37; comparison is deferred to a later synthesis round.

---

## Member: _pending_

*(PO will supply other team members’ independent lists; append below without overwriting Grok’s section.)*

---

## Synthesis status

**Not started.** Multi-member comparison, gap detection, and role classification (Weight vs Gate vs Filter vs Signal) are future steps. Issue #37 remains OPEN.
