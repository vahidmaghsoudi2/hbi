# HBI Consultation Minimal Contract v0.1

| Field | Value |
|-------|--------|
| Status | **DRAFT — AWAITING PO ACCEPTANCE** |
| Type | Conceptual / Vocabulary Contract |
| Implementation | **NOT AUTHORIZED** |
| Schema / API / UI / Home redesign | **NOT AUTHORIZED** |
| Recommendation scoring change | **NOT AUTHORIZED** |
| Parent Framework | Issue #208 |
| Phase 0 Reality Baseline | Issue #209 · SHA `487632c3051b4b5280ad4ea79730792437151dfd` |
| Contract authored against | `origin/master` @ `487632c3051b4b5280ad4ea79730792437151dfd` |
| Author role | Phase 1 Execution (Grok) — Independent of implementation |

---

## 0. Purpose and non-goals

### Purpose
Reconcile **existing HBI runtime reality** with the Consultation Framework direction (#208) so that the first Vertical Slice can be discussed without inventing parallel Customer/Case/Profile systems.

### Non-goals (explicit)
- No new persisted entities unless an OPEN decision later authorizes them.
- No Questionnaire engine, image pipeline, AI intake, or Product Master redesign.
- No Home information-architecture redesign (Case/Need-first is **direction**, not current UI obligation).
- No change to Recommendation weights, thresholds, or eligibility formulas.

### Classification vocabulary used in this document
| Tag | Meaning |
|-----|---------|
| **FACT** | Observed in code/tests on the baseline SHA |
| **CONTRACT** | Binding rule for V1 discussion once PO accepts this draft |
| **PROPOSED** | Minimal design glue required for Vertical Slice coherence; not implemented |
| **OPEN** | Requires explicit PO decision before any implementation |
| **UNKNOWN** | Not verified on baseline |
| **CONFLICT** | Framework wording vs repository reality (must not be papered over) |

---

## 1. Reality re-verification (entry)

| Check | Result | Evidence |
|-------|--------|----------|
| `origin/master` SHA | `487632c3051b4b5280ad4ea79730792437151dfd` | `git rev-parse HEAD` after clone |
| Matches Phase 0 baseline in #209 | **YES** | Issue #209 body |
| PROJECT_RULES present | **YES** | `docs/01_project_control/PROJECT_RULES.md` |
| Customer model | **FACT** | `app/models/customer.py` |
| Case model | **FACT** | `app/models/case.py` |
| ProfileFact model + service | **FACT** | `app/models/profile_fact.py`, `app/services/profile_fact_service.py` |
| Recommendation + generate path | **FACT** | `app/models/recommendation.py`, `app/services/recommendation_service.py` |
| Decision state in memory during generate | **FACT** | `RecommendationService._build_decision_state` |
| ProfileFact consumed by Recommendation | **NOT FACT** | No ProfileFact reference in recommendation service/router on baseline |
| Feedback / follow_up_at | **FACT** | `app/models/feedback.py`, `app/api/routers/specialist.py` |
| Home consultation + product intake panels | **FACT** | `frontend/src/pages/NewHomePage.tsx`, `ProductIntakePanel.tsx` |

**CONFLICT (managed, not hidden):** Framework #208 prefers Case/Need-first Home. Runtime Home is a **mixed operational surface** (consult + catalog + intake + sales). Contract treats Case/Need-first Home as **DEFERRED UI direction**, not V1 obligation.

---

## 2. Concept matrix (core of the Minimal Contract)

| Concept | Current Reality | Contract Decision | Required for V1? | Source / Evidence | Open Question |
|---------|-----------------|-------------------|------------------|-------------------|---------------|
| **Customer (identity root)** | Persisted identity, consent, legacy profile fields, relations to Case | Customer remains the only identity/root account entity | **Yes** | `app/models/customer.py` | — |
| **Legacy profile fields on Customer** | `skin_profile`, `hair_profile`, `scalp_profile`, `concerns`, `observations`, `answers`, notes | Remain valid **legacy consultation inputs**; not deleted by this contract | **Yes (read/use)** | same | When/whether to stop writing legacy fields (**OPEN**) |
| **ProfileFact** | Versioned facts with value_state, provenance, lifecycle; customer-authorized writes | Durable, consent-gated, audited reusable knowledge; **does not replace Customer** | **Yes as capability; not required as Rec input in V1** | ProfileFact model/service; Write Contract lineage on #201 | Promotion of intake answers → ProfileFact (**OPEN**) |
| **Case** | Visit/work unit owned by customer; fields include `identified_needs`, `evidence_gaps`, `confidence`, `reasoning_status` | Case is the **consultation episode** boundary for recommendation generation | **Yes** | `app/models/case.py`; cases router ownership | Whether `identified_needs` / `evidence_gaps` columns are written consistently (**PARTIAL / OPEN** operationally) |
| **Case context vs Profile** | Generate merges persisted customer context + current consultation payload | **CONTRACT:** Profile = durable; Case context = current visit signals; merge rule stays as today unless a later contract changes it | **Yes** | Recommendation generate path; customers intake `open_case` behavior | Formal precedence ProfileFact vs legacy Customer fields when both exist (**OPEN** — today Rec does not read ProfileFact) |
| **Need** | Canonical needs via GAP-05 normalization; Case stores `identified_needs` string; no Need table | **CONTRACT V1:** Need is a **normalized decision concept**, not a required new table. Representation may remain Case fields + in-memory decision_state + recommendation scores | **Yes (concept)** | `need_normalization.py`, `product_compatibility.py`, Case.identified_needs | Persist structured Need rows? **DEFERRED / not required for V1** |
| **Decision Context** | Built in `RecommendationService._build_decision_state` (factors, gaps, unknowns, conflicts, status) — not a separate table | **CONTRACT V1:** Decision Context is the **ephemeral/computed reasoning bundle** for a generate call (and whatever Case fields already store). No new DecisionContext entity required for V1 | **Yes as behavior; No as new entity** | `_build_decision_state` | Whether to persist full decision_state snapshot (**OPEN**, not required to start) |
| **Evidence (product)** | Product-linked Evidence with QA/conflict | Unchanged product-side evidence authority | **Yes** | `app/models/evidence.py` | — |
| **Evidence Gap (case/decision)** | `Case.evidence_gaps`; decision_state `evidence_gaps` / unknowns; gating via eligibility | **CONTRACT:** Evidence Gap = missing information that **materially blocks or weakens** a trustworthy recommendation *for this Case*. Distinct from product Evidence row absence alone | **Yes (concept)** | Case model; recommendation_service | Who writes Case.evidence_gaps and in what format (**OPEN**) |
| **Unknown** | value_state / decision unknowns / unmapped needs | **CONTRACT:** Unknown = explicitly not known (not guessed). Unmapped/ambiguous needs must not be silently invented (GAP-05) | **Yes** | ProfileFact value_state; need_normalization; decision_state | — |
| **Conflict** | Evidence.conflict_status; decision conflicts; CONFLICTED ProfileFact status | **CONTRACT:** Conflict = incompatible claims/facts; must not be auto-resolved into a false certainty for ranking | **Yes** | Evidence service; ProfileFact statuses | Consumer rules when ProfileFact CONFLICTED if later wired to Rec (**DEFERRED**) |
| **Next Question / Action** | No dedicated question engine verified | **PROPOSED (conceptual only):** An Evidence Gap *may* imply a next human question or operator action; V1 does **not** require a Questionnaire subsystem | **No (engine)** | — | Priority rules for next question (**OPEN** / DEFERRED engine) |
| **Progressive Profiling** | Home collects concerns/skin; merge with saved profile; ProfileFact optional path exists | **CONTRACT:** Ask only when the answer can change eligibility, safety posture, or ranking rationale for *this* Case. No mandatory full questionnaire | **Yes (rule)** | NewHomePage consultation capture; ProfileFact write boundary | Automated question selection (**NOT VERIFIED** → DEFERRED) |
| **Recommendation** | Case-owned generate; eligibility before effective recommendation path; scores and reasons stored | Remains the product suggestion artifact for the Case | **Yes** | recommendation model/service | ProfileFact as input (**NOT authorized** without separate gate) |
| **Follow-up / Outcome (V1 min)** | Feedback linked to Case and optional Recommendation; `outcome`, `rating`, `comment`, `follow_up_at`; specialist override exists | **CONTRACT V1 min:** Record simple outcome/feedback against Case/Recommendation; do not require full Outcome Assessment domain | **Yes (min)** | `feedback.py`, specialist router | Rich Product Usage / Observed Outcome model (**DEFERRED**) |
| **Questionnaire** | Customer.answers only | Not a consultation system | **No** | customer.py | — |
| **Image / Before-After** | Not verified as domain | Out of V1 | **No** | — | — |

---

## 3. LOCKED (Framework direction ∩ Reality — safe to treat as baseline)

1. **Customer is root identity**; Case is owned by Customer.  
2. **Recommendation is generated in a Case context**, not product-first browsing as the decision authority.  
3. **Eligibility / gating exists before treating a product as a successful recommendation path** (runtime behavior in RecommendationService).  
4. **Product-side Evidence and ProductKnowledge remain the catalog authority**; consultation must not invent product claims.  
5. **GAP-05:** Customer need normalization is bounded; Product match surface is `ProductKnowledge.known_use_cases` (product vocabulary independent).  
6. **ProfileFact is real and separate from Customer**; it is **not** currently a Recommendation input.  
7. **No parallel profile/case stack** may be introduced under this contract.  
8. **Unknown must not be coerced into false Known** for need mapping.  
9. **Implementation, migration, API, UI, Home redesign, scoring changes are not authorized by accepting vocabulary alone.**

---

## 4. PROPOSED (minimal glue for Vertical Slice coherence — not implemented by this PR)

1. **Vocabulary labels** for operators/docs:  
   - *Profile (legacy Customer fields)* vs *ProfileFact (versioned)* vs *Case context (visit)*.  
2. **Evidence Gap (decision-level)** as a first-class *concept* mapped onto existing `Case.evidence_gaps` + decision_state lists — without new tables.  
3. **Next Action** as a human-readable implication of a gap (ask / defer / refer / no recommendation) — documentation only.  
4. **Progressive Profiling rule** as process constraint on future UX work — no questionnaire module.

---

## 5. OPEN (PO decisions required before implementation work)

| ID | Decision |
|----|----------|
| O1 | When both legacy Customer profile fields and ProfileFact exist, what is the **read precedence** for consultation (today Rec ignores ProfileFact)? |
| O2 | Is **writing** consultation answers into ProfileFact in-scope for first Vertical Slice, or remains manual/optional? |
| O3 | Must `Case.identified_needs` / `Case.evidence_gaps` be **durably updated** on every generate, or is in-memory decision_state sufficient for V1? |
| O4 | Minimum **Follow-up** success criteria (e.g. feedback row only vs required `follow_up_at`)? |
| O5 | Any change toward Case/Need-first **Home IA** requires a separate UI authorization — confirm still deferred. |

---

## 6. DEFERRED (explicitly out of V1)

- Questionnaire engine / progressive question planner  
- Image / before-after artifacts  
- AI extraction for profile or product  
- New Need entity table  
- New DecisionContext table  
- Full Outcome / Product Usage domain beyond existing Feedback  
- ProfileFact → Recommendation adapter (requires separate Reality Gate; historically documented as not wired)  
- Product intake redesign; catalog AI  
- Scoring / weight / threshold changes  

---

## 7. Vertical Slice conceptual test

Path:

`Customer → Existing Profile/Context → Interaction → Case → Need → Minimum Relevant Information → Assessment/reasoning state → Eligible Products → Recommendation + Reason → Customer Choice → Simple Follow-up`

| Step | Status on baseline |
|------|---------------------|
| Customer | **EXISTS** |
| Existing Profile/Context | **PARTIAL** (Customer fields + optional ProfileFact; Rec uses customer/consultation merge, not ProfileFact) |
| Interaction | **EXISTS** (Home consultation capture / intake APIs) |
| Case | **EXISTS** |
| Need | **PARTIAL** (normalization + scores; no Need entity; Case.identified_needs string) |
| Minimum Relevant Information | **PARTIAL** (progressive rule not enforced as engine) |
| Assessment / reasoning state | **PARTIAL** (computed decision_state; limited Case field persistence) |
| Eligible Products | **EXISTS** (eligibility path in RecommendationService + product ACTIVE/gates upstream) |
| Recommendation + Reason | **EXISTS** |
| Customer Choice | **PARTIAL** (sales can link recommendation_id; full choice UX varies) |
| Simple Follow-up | **EXISTS** (Feedback + follow_up_at) |

---

## 8. Reality → Contract traceability

| Contract statement | Reality anchor |
|--------------------|----------------|
| Customer root | `Customer` model |
| Case episode | `Case` model + ownership on cases API |
| Legacy profile fields | columns on `Customer` |
| ProfileFact durable facts | `ProfileFact` + `ProfileFactService` |
| Need as normalized concept | `need_normalization`, `product_compatibility`, need_match on Recommendation |
| Decision context computed | `_build_decision_state` |
| Evidence gap fields | `Case.evidence_gaps`; decision_state gaps/unknowns |
| Product evidence authority | `Evidence`, readiness/D3 on product lifecycle |
| Follow-up min | `Feedback.outcome/rating/follow_up_at` |
| Home mixed surface | `NewHomePage.tsx` panels |
| No ProfileFact in Rec | absence of imports/usages in recommendation service |

---

## 9. Acceptance criteria for *this Contract* (documentation)

1. Baseline SHA recorded and matches the SHA used for evidence.  
2. Every core concept is tagged FACT / CONTRACT / PROPOSED / OPEN / DEFERRED / CONFLICT as applicable.  
3. No schema/API/UI/code change in the delivering PR.  
4. LOCKED vs PROPOSED vs OPEN vs DEFERRED are separable by a reviewer.  
5. Vertical Slice table completed without claiming non-existent engines.  
6. Explicit statement that PO acceptance of this doc ≠ implementation authorization.  

---

## 10. Smallest next implementation unit (recommendation only — not executed)

After PO accepts this contract and resolves O1–O4 as needed:

**Smallest unit:** Define and test a **single consultation pass** that uses *existing* APIs only: ensure Case exists → generate recommendations → persist/display reasons → optional Feedback — plus documentation of Evidence Gap handling using existing fields.  

Still **out of scope** unless separately authorized: ProfileFact→Rec adapter, Home redesign, new tables.

---

## 11. Unauthorized changes checklist

| Change type | Authorized by this document? |
|-------------|------------------------------|
| Code / migration / API / UI | **No** |
| Recommendation formula | **No** |
| Home redesign | **No** |
| Merge of this PR without PO | **No** |

---

*End of Minimal Consultation Contract v0.1*
