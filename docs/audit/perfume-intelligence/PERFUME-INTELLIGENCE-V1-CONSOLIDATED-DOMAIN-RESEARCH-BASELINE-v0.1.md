# PERFUME INTELLIGENCE V1 — CONSOLIDATED DOMAIN & RESEARCH BASELINE

## Document Control

Status: RESEARCH / CONSOLIDATED DOMAIN BASELINE
Authority: NON-AUTHORITATIVE FOR IMPLEMENTATION
Architecture: NOT DECIDED
Contract: NOT AUTHORIZED
Schema: NOT AUTHORIZED
Implementation: NOT AUTHORIZED
Automatic Recommendation: NOT AUTHORIZED
Automatic Scoring: DEFERRED
Automatic Learning: DEFERRED
Live Customer Pilot: NOT AUTHORIZED BY THIS DOCUMENT

This document consolidates the current Perfume / Fragrance Intelligence research direction, domain boundaries, risks, deferred items, pilot direction, and governance constraints.

It is a research baseline. It is not a Contract, Architecture Decision, Schema, API specification, implementation specification, or proof of current runtime behavior.

---

# 1. Purpose

Perfume Intelligence is the fragrance-domain intelligence line of HBI.

Its purpose is to determine, through evidence-aware and human-reviewable research, how HBI could support real perfume/fragrance consultation without relying on assumptions, unsupported claims, hidden scoring, or premature automation.

The immediate objective is not to identify "the best perfume."

The immediate objective is to establish whether a fragrance consultation can be:

- captured accurately;
- investigated with attributable information;
- separated into facts, claims, observations, preferences, unknowns and conflicts;
- explained to an operator and customer;
- tested through manual sampling;
- evaluated through documented outcomes;
- bounded safely;
- and later formalized without turning research assumptions into system truth.

Core HBI principle:

> NO ASSUMPTION / NO INVENTED DATA.

---

# 2. Relationship to HBI

Perfume Intelligence is a domain-specific line within HBI. It is independent at the domain level, but it remains subject to HBI-wide governance, evidence, provenance, identity, inventory, authorization and decision-trace principles.

The domain must not create parallel versions of HBI core capabilities without a verified gap and an explicit architecture decision.

Conceptually:

HBI
- Shared governance
- Shared product identity principles
- Shared evidence / provenance principles
- Shared inventory reality
- Shared audit and verification principles
- Perfume / Fragrance Intelligence domain

The fragrance line may reuse HBI capabilities. It may extend them when a verified domain need exists. A new parallel Product Master, Evidence engine, ProductKnowledge engine, or lifecycle engine is deferred until reuse / extend / new analysis proves a gap.

---

# 3. Three Distinct Layers

A central boundary for the fragrance line is:

1. Gallery / Navigation
2. Perfume Product Information
3. Perfume Intelligence

## Gallery / Navigation

The customer or operator path used to discover and access perfume products.

A PERFUME gallery/category does not by itself prove that a fragrance intelligence engine exists.

## Perfume Product Information

The information associated with an exact fragrance product, including identity, official information, availability and attributable evidence.

## Perfume Intelligence

The future domain capability concerned with customer taste, context, evidence evaluation, candidate consideration, explanation, sampling and outcome interpretation.

These layers may interact, but they are not the same capability.

Therefore:

Gallery PERFUME
!= Perfume Intelligence
!= HBI Core

---

# 4. Current Governance State

The intended progression is:

Foundation
→ Scope Lock
→ Risk Register
→ Deferred Register
→ Audit Direction
→ Manual Pilot Workbook
→ Simulated Cases / Findings
→ Independent Verification
→ PO Review
→ Future Contract Discussion
→ Future Architecture Discussion
→ Future Implementation

The existence of this baseline does not authorize the later stages.

The current Independent Verification blocker remains a governance issue and is not silently converted into a positive result.

Audit Author != Independent Verifier.

---

# 5. Domain Truth Boundaries

The following distinctions are foundational:

Product Fact
!= Manufacturer Claim
!= Olfactory Interpretation
!= Performance Observation
!= Customer Preference
!= Customer Outcome
!= AI Inference

Similarly:

Manufacturer Claim != Universal Fact
Customer Report != General Product Fact
AI Inference != Verified Knowledge
Unknown != Negative
Conflict != Low Confidence
Documentation != Behavior Proof

These distinctions must survive future design.

---

# 6. Product Identity

Product identity is a prerequisite for trustworthy product-level information.

Research-level identity candidates include:

- Brand
- Official Product Name
- Variant / Flanker
- Concentration
- Volume
- GTIN / Barcode where available
- Market / Region
- Packaging Version where relevant
- Batch where relevant
- Product Form
- Authenticity Status
- Inventory Status
- Lifecycle Status

These are research candidates, not approved HBI fields or entities.

A major identity risk is accidental merging of a flanker, reformulation, concentration or market version with another product.

Therefore:

> Identity must be conservative until verified.

Before Schema design, real perfume examples should be examined to determine which differences represent distinct products and which are attributes of one product.

---

# 7. Olfactory Knowledge

Research-level olfactory information may include:

- Fragrance Family
- Subfamily
- Accord
- Note
- Note Role
- Top / Heart / Base
- Descriptor
- Derived Olfactory Profile

Candidate families include:

Floral, Woody, Ambery, Fresh, Citrus, Fruity, Gourmand, Chypre, Leather, Aromatic, Aquatic, Green, Musky, Other / Requires Review.

Candidate descriptors include:

Sweet, Fresh, Clean, Warm, Dry, Spicy, Smoky, Powdery, Musky, Woody, Floral, Green, Aquatic, Fruity, Creamy, Resinous, Earthy, Leather-like, Aromatic, Mineral, Soapy, Citrusy, Balsamic, Herbal.

None of these becomes a controlled HBI value until separately reviewed and approved.

A note must retain its source.

A derived olfactory profile must remain distinguishable from an official product fact.

---

# 8. Performance

Performance must be treated as a separate evidence domain.

At research level:

Longevity
!= Projection
!= Sillage
!= Intensity

Concentration
!= Performance

Potential performance observations include:

- longevity;
- projection;
- sillage;
- intensity;
- opening behavior;
- dry-down behavior;
- context dependence;
- observation window;
- observer;
- date;
- application context.

Performance can vary with person, skin, clothing, environment, temperature, application and perception.

Therefore a single observation must not automatically become a universal product fact.

---

# 9. Context

Potential context signals include:

- Season
- Occasion
- Environment
- Time of Day
- Weather
- Formality
- Indoor / Outdoor
- Shared Environment
- Personal Use / Gift
- Budget
- Customer-stated constraints

These are context or preference signals, not universal hard filters.

Examples:

Season != mandatory fragrance family
Occasion != product fact
Environment != gender rule

Context must help understand a request, not create stereotypes disguised as intelligence.

---

# 10. Marketing Gender Boundary

Manufacturer marketing labels such as:

- For Men
- For Women
- Unisex

are product metadata.

They do not independently establish:

- customer identity;
- customer preference;
- customer compatibility;
- customer suitability.

Marketing gender must not silently become an automatic exclusion rule.

---

# 11. Customer Taste

Customer taste is captured from the customer's own wording and consultation context.

Potential research information includes:

- preferences;
- avoidances;
- explicit deal-breakers;
- desired intensity;
- desired projection/presence;
- importance of longevity;
- previously liked fragrances;
- previously disliked fragrances;
- occasion;
- environment;
- gift/self;
- budget where relevant.

Customer wording should remain recoverable.

Customer wording != system interpretation.

If a customer says:

"I do not want something that fills the whole room."

the system may investigate whether this expresses a lower projection preference, but must not silently convert the statement into a permanent numerical preference.

---

# 12. Minimum Consultation Questions

The current research candidate set includes:

1. What is the fragrance for?
2. Is it for the customer or a gift?
3. What smells or fragrance characteristics do they like?
4. What smells or characteristics do they want to avoid?
5. Is there a fragrance they previously liked or disliked?
6. What level of fragrance presence do they prefer?
7. How important is longevity?
8. Will the fragrance be used in a shared environment?
9. Is there another customer-stated constraint relevant to the request?
10. Budget, when relevant to the consultation.

The Pilot must determine which questions are truly necessary at the beginning and which should be asked only when needed.

A customer declining to answer a question must not automatically be interpreted as a negative preference.

---

# 13. Evidence and Provenance

Evidence must be evaluated per attribute.

A source appropriate for identity is not automatically appropriate for performance.

Candidate source types include:

- Official Product Page
- Official Label
- Manufacturer Documentation
- Regulatory Source
- Independent Expert Review
- Internal Documented Test
- Community Report
- Customer Report
- Unattributed Source
- AI Inference

Candidate assertion classes include:

- FACT
- MANUFACTURER_CLAIM
- OBSERVATION
- CUSTOMER_REPORT
- INFERENCE
- UNKNOWN
- CONFLICT

These are conceptual candidates only.

The core research chain is:

AI Research
→ Assertion
→ Evidence
→ Review
→ Knowledge

Not:

AI
→ Truth

Manufacturer marketing can be useful evidence about what the manufacturer claims, while remaining a manufacturer claim rather than an independently verified universal fact.

---

# 14. Unknown and Conflict

Unknown information must remain visible.

Unknown != Negative.

Examples:

- ingredient detail unavailable != ingredient absent;
- projection not established != low projection;
- longevity not established != poor longevity;
- source unavailable != claim false.

Conflicting information must also remain visible.

Conflict != Low Confidence.

If two sources disagree, the disagreement should remain traceable until an authorized resolution process exists.

The system must not silently choose one source merely to produce a cleaner answer.

---

# 15. Eligibility, Compatibility and Decision Support

These concepts must remain distinct:

Product Eligibility
!= Customer Decision Readiness
!= Customer × Product Compatibility

A future conceptual path may be:

Eligibility
→ Compatibility
→ Candidate Shortlist
→ Explanation
→ Human Review / Sampling
→ Outcome

At the current stage, no automatic compatibility formula is authorized.

A candidate is not automatically a recommendation.

---

# 16. Candidate vs Recommendation

The distinction is mandatory:

Candidate
!= Recommendation
!= Sampling
!= Purchase
!= Outcome

A Candidate is a product considered for human review.

A future Recommendation would require an authorized decision framework.

Sampling is a customer experience event.

Purchase is a commercial event.

Outcome is a later observed or customer-reported event.

No one of these events automatically proves another.

Examples:

Sampled != Liked
Liked opening != Liked dry-down
Purchased != Satisfied
Satisfied != Universally Suitable

---

# 17. Sampling

Sampling is important because fragrance perception can change between opening and later development.

Research flow:

Blotter
→ Opening Observation
→ Optional Skin Sampling with Consent
→ Dry-down Observation when observed
→ Customer Response

Sampling is an observation process, not a guarantee mechanism.

A customer's reaction remains a customer-specific outcome unless independently supported as broader evidence.

---

# 18. Safety Boundary

Perfume Intelligence is not a medical diagnosis system.

Potential research inputs:

- documented ingredients;
- official warnings;
- documented allergen declarations;
- usage restrictions;
- customer-reported discomfort;
- sampling consent;
- escalation boundary.

Mandatory distinctions:

Documented allergen declaration
!= medical clearance

No disclosed allergen data
!= no risk

Customer discomfort
!= diagnosed allergy

Customer headache
!= migraine diagnosis

Medical diagnosis, allergy diagnosis, medical clearance, pregnancy-related medical advice and universal safety guarantees are outside the current domain scope.

If significant discomfort is reported during sampling:

Stop
→ Record the customer's report
→ Do not diagnose
→ Follow an approved escalation policy when one exists

External regulatory or standards material may inform later research, but remains external context until specifically reviewed for the relevant product, market and claim.

Current research references include the IFRA Standards Library and EU fragrance-allergen labelling context. These references do not by themselves constitute HBI architecture, contract or product-specific facts.

---

# 19. Risk Register Consolidation

Key risks currently identified:

PI-R-001 — AI invents notes, families or facts.
Control: source required and review before knowledge.

PI-R-002 — Marketing claim becomes fact.
Control: preserve manufacturer-claim status.

PI-R-003 — Concentration is interpreted as performance.
Control: keep concentration and performance separate.

PI-R-004 — Fabricated performance score.
Control: no numeric scoring before sufficient pilot evidence and policy.

PI-R-005 — Gender becomes a hard filter.
Control: marketing metadata only unless separately authorized.

PI-R-006 — Season becomes a hard filter.
Control: context signal only.

PI-R-007 — Unknown becomes negative.
Control: explicit Unknown handling.

PI-R-008 — Conflict becomes hidden.
Control: visible conflict and traceable sources.

PI-R-009 — Flanker is merged with original.
Control: conservative identity policy.

PI-R-010 — Purchase becomes satisfaction.
Control: event distinction.

PI-R-011 — Discomfort becomes diagnosis.
Control: report-only safety boundary.

PI-R-012 — Derived profile becomes product fact.
Control: derived label and provenance/versioning.

PI-R-013 — Similarity is introduced too early.
Control: deferred until taxonomy, identity, evidence and explainability are stable.

PI-R-014 — Audit becomes architecture.
Control: maintain Audit / Architecture separation.

PI-R-015 — Documentation becomes behavior proof.
Control: documentation != runtime evidence.

PI-R-016 — Audit author verifies own audit.
Control: independent verifier.

PI-R-017 — V1 scope expands.
Control: Scope Lock and Deferred Register.

PI-R-018 — Parallel masters or engines are created.
Control: Reuse / Extend / New analysis after verified gap.

---

# 20. Deferred Register

The following remain intentionally deferred:

- Similarity
- Numeric scoring
- Automatic ranking
- Automatic recommendation
- Automatic learning
- Derived olfactory profile engine
- Performance normalization
- Advanced weather/season model
- Cross-market equivalence
- Advanced customer-event ledger
- New Product Master
- New Evidence engine
- New ProductKnowledge engine
- New lifecycle engine

Re-entry requires evidence and governance appropriate to the item.

Deferral is an intentional control, not an unfinished implementation.

---

# 21. What This Baseline Does Not Authorize

This document must not be used as justification to:

- create a separate perfume Product Master;
- replace HBI's shared Product model;
- create a separate Evidence engine;
- create a separate ProductKnowledge engine;
- create a separate lifecycle engine;
- change the existing Recommendation system;
- create new production enums;
- create mandatory database fields from research candidates;
- introduce automatic scoring;
- introduce automatic ranking;
- introduce automatic recommendation;
- introduce automatic learning;
- change API behavior;
- change runtime behavior;
- start a live customer pilot.

Any such transition requires its own evidence, contract/architecture governance and PO authorization.

---

# 22. Manual Pilot Direction

The next research artifact should be a Manual Pilot Workbook.

Its role is to test the consultation process before implementation.

The Workbook should test:

- customer wording capture;
- minimum questioning;
- preference / avoidance separation;
- context capture;
- product identity;
- availability;
- evidence and provenance;
- Unknown handling;
- Conflict handling;
- candidate explanation;
- sampling;
- customer response;
- outcome events;
- safety boundaries.

Pilot terminology must not silently become HBI production enums.

---

# 23. Simulated vs Real Pilot

Research exercises may use SIMULATED cases.

Simulated data must remain visibly separate from Runtime evidence.

A future REAL customer pilot requires separate authorization and appropriate privacy/safety controls.

The Workbook itself does not authorize a live pilot.

---

# 24. Pilot Completion Criteria

The pilot should not be judged primarily by sales or purchase count.

Research evaluation should ask:

- Was customer wording captured without distortion?
- Were preference and avoidance separated?
- Was sufficient context captured?
- Were unknowns preserved?
- Were conflicts exposed?
- Was product identity clear?
- Was availability actually known?
- Could the operator explain why each candidate was considered?
- Could the customer distinguish a candidate from a guarantee?
- Was sampling consent handled correctly?
- Were opening and dry-down reactions kept separate?
- Were purchase and satisfaction kept separate?
- Were unsupported assumptions introduced?
- Were operators asking too many or too few questions?
- Which information gaps repeatedly prevented responsible consideration?

Pilot findings should be recorded before any move toward formal Contract or Architecture.

---

# 25. Future Evidence Required Before Formalization

Before moving from research to formal system design, the project should establish evidence for:

1. Product identity granularity.
2. Product availability requirements.
3. Minimum consultation information.
4. Reliable olfactory taxonomy.
5. Treatment of manufacturer claims.
6. Treatment of performance observations.
7. Conflict resolution.
8. Unknown handling.
9. Human-review boundaries.
10. Sampling workflow.
11. Customer outcome representation.
12. Safety boundaries.
13. Decision explanation requirements.
14. Whether scoring is actually necessary.
15. Whether ranking is actually necessary.
16. Whether automatic recommendation is justified.
17. Whether automatic learning is justified.
18. Whether existing HBI core capabilities can be reused or extended.

These are research questions, not implementation requirements.

---

# 26. Current Readiness Position

Research Foundation:
Established

Foundation Critique:
Established

Scope Lock:
Established

Risk Register:
Established

Deferred Register:
Established

Audit Direction:
Established

Manual Pilot:
Ready for research drafting / simulated exploration

Live Customer Pilot:
Separate authorization required

Architecture:
Not decided

Contract:
Not authorized

Implementation:
Not authorized

Automatic Recommendation:
Not authorized

Independent Verification:
Must remain independent and explicit

---

# 27. Operating Philosophy

The intended progression is:

Observe
→ Capture
→ Verify
→ Expose Unknowns
→ Resolve or preserve Conflict
→ Human Review
→ Pilot
→ Learn from evidence
→ Formalize only what survives validation

Not:

Assume
→ Encode
→ Score
→ Recommend
→ Treat the result as truth

A useful fragrance intelligence capability is not one that always produces an answer.

It is one that can distinguish:

KNOWN
UNKNOWN
CONFLICTED
CLAIMED
OBSERVED
CONSIDERED
SAMPLED
PURCHASED
OUTCOME

without silently changing one into another.

---

# 28. Final V1 Position

Perfume Intelligence V1 is currently a research and decision-support exploration.

Its immediate value is to establish a trustworthy manual process for fragrance consultation while preserving the integrity of HBI's shared core.

The domain should remain:

- evidence-aware;
- source-attributable;
- uncertainty-preserving;
- human-reviewable;
- safety-bounded;
- conservative about identity;
- conservative about inference;
- explicit about conflicts;
- explicit about unknowns;
- separate from Gallery navigation;
- separate from Product Information;
- separate from future automatic Recommendation logic.

The most important rule is:

> If the evidence is insufficient, the system must be able to say that the evidence is insufficient.

That is not a failure state. It is a correctness state.

---

# 29. Change Control

This baseline is a research artifact.

Future changes to Contract, Architecture, Schema, API, Runtime, Recommendation Logic, Scoring or Learning require separate governance.

No future implementation may cite this document alone as authorization.

---

# 30. Agent Provenance

Agent: ChatGPT / GPT-5.6 Luna
Execution surface: GitHub connector
Input repository snapshot: 1d148449be7fc724a63b48eff92d665d6bfe4b00
Operation requested by: PO / Vahid Maghsoudi
Scope of this change: Documentation only
Code / Schema / Contract / Architecture / Runtime: unchanged

End of Research Baseline.
