# HBI Consultation Minimal Contract v0.1

| Field | Value |
|-------|--------|
| Status | **DRAFT — REWORKED AFTER INDEPENDENT REVIEW — AWAITING RE-REVIEW** |
| Type | Conceptual / Vocabulary Contract |
| Implementation | **NOT AUTHORIZED** |
| Schema / API / UI / Home redesign | **NOT AUTHORIZED** |
| Recommendation scoring change | **NOT AUTHORIZED** |
| Parent Framework | Issue #208 |
| Phase 0 Reality Baseline | Issue #209 · SHA `487632c3051b4b5280ad4ea79730792437151dfd` |
| Contract authored against | `origin/master` @ `487632c3051b4b5280ad4ea79730792437151dfd` |
| Docs commit lineage | Initial draft + review fixes for PR #210 |
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
| `origin/master` SHA | `487632c3051b4b5280ad4ea79730792437151dfd` | `git rev-parse` / Issue #209 baseline |
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

## 1A. Problem / Assessment / Factor — explicit Reality status

Operational directive chain (Framework / team language):

`Customer → Case → Problem → Assessment → Factor → Evidence/Unknown/Conflict`

| Concept | Status on baseline | Evidence | Must not be confused with |
|---------|-------------------|----------|---------------------------|
| **Problem** (domain object / persisted entity) | **NOT VERIFIED** as a distinct domain model | No `Problem` model/table under `app/models` on baseline | Informal “customer concern” text |
| **Assessment** (domain object / persisted entity) | **NOT VERIFIED** as a distinct domain model | No `Assessment` model/table on baseline | In-memory `decision_status` / eligibility narrative |
| **Factor** (runtime structure inside decision_state) | **PARTIAL** | `RecommendationService._build_decision_state` builds `factors` as `{"name": "concern", "value": <concern>, "source": "customer_input", "validity": "DECLARED"}` from **raw concern strings** in `customer_profile` | A full Problem→Assessment→Factor domain chain |
| **Factor** (first-class persisted entity) | **NOT VERIFIED** | No Factor table | — |

**FACT — how factors are actually produced today:**

```text
customer_profile["concerns"]
    → split / normalize strings
    → factors[]  (name=concern, source=customer_input)
    → normalize_needs_from_factors(factors)
    → canonical Needs
```

**CONTRACT:** Claiming that HBI already implements the full domain chain `Problem → Assessment → Factor` as first-class consultation entities is **false** on this baseline. What exists is a **PARTIAL** runtime factor list derived from concerns, plus computed decision_state fields.

**PROPOSED (vocabulary only, no schema):** Future contracts may map Framework “Problem/Assessment” onto explicit objects; until then those words must not be reported as EXISTS.

**OPEN:** Whether V1 ever requires persisted Problem/Assessment entities, or remains concern→factor→need only.

---

## 2. Concept matrix (core of the Minimal Contract)

| Concept | Current Reality | Contract Decision | Required for V1? | Source / Evidence | Open Question |
|---------|-----------------|-------------------|------------------|-------------------|---------------|
| **Customer (identity root)** | Persisted identity, consent, legacy profile fields, relations to Case | Customer remains the only identity/root account entity | **Yes** | `app/models/customer.py` | — |
| **Legacy profile fields on Customer** | `skin_profile`, `hair_profile`, `scalp_profile`, `concerns`, `observations`, `answers`, notes | Remain valid **legacy consultation inputs**; not deleted by this contract | **Yes (read/use)** | same | When/whether to stop writing legacy fields (**OPEN**) |
| **ProfileFact** | Versioned facts with value_state, provenance, lifecycle; customer-authorized writes | Durable, consent-gated, audited reusable knowledge; **does not replace Customer** | **Yes as capability; not required as Rec input in V1** | ProfileFact model/service | Promotion of intake answers → ProfileFact (**OPEN**) |
| **Case** | Visit/work unit owned by customer; fields include `identified_needs`, `evidence_gaps`, `confidence`, `reasoning_status` | Case is the **consultation episode** boundary for recommendation generation | **Yes** | `app/models/case.py`; cases router ownership | Whether need/gap **columns** are populated in live flows (**see §2A**) |
| **Case context vs Profile** | Generate merges persisted customer context + current consultation payload | **CONTRACT:** Profile = durable; Case context = current visit signals; merge rule stays as today unless a later contract changes it | **Yes** | Recommendation generate path; customers intake `open_case` behavior | Precedence ProfileFact vs legacy Customer fields (**OPEN** — Rec does not read ProfileFact) |
| **Problem** | Not a verified domain entity | Must be labeled **NOT VERIFIED** until implemented under a later authorization | **No (entity)** | §1A | — |
| **Assessment** | Not a verified domain entity; only computed decision signals | **NOT VERIFIED** as entity; do not equate to “Assessment” domain step | **No (entity)** | §1A | — |
| **Factor** | In-memory list from concerns in `_build_decision_state` | **PARTIAL** runtime only; not a persisted Factor domain | **Yes as runtime input to need normalization** | `recommendation_service.py` | — |
| **Need** | Canonical needs via GAP-05 normalization; Case stores `identified_needs` string; no Need table | **CONTRACT V1:** Need is a **normalized decision concept**, not a required new table | **Yes (concept)** | `need_normalization.py`, `product_compatibility.py` | Persist structured Need rows? **DEFERRED** |
| **Decision Context** | Built in `_build_decision_state` — not a separate table | **CONTRACT V1:** ephemeral/computed reasoning bundle for a generate call (+ existing Case columns if used). No new DecisionContext entity for V1 | **Yes as behavior; No as new entity** | `_build_decision_state` | Persist full decision_state snapshot (**OPEN**) |
| **Evidence (product)** | Product-linked Evidence with QA/conflict | Unchanged product-side evidence authority | **Yes** | `app/models/evidence.py` | — |
| **Evidence Gap (concept)** | Decision-level idea of missing info | See **§2A** — concept may be contracted without claiming persistence | **Yes (concept)** | §2A | Writer/timing/structure (**OPEN**) |
| **Evidence Gap (persistence)** | `Case.evidence_gaps` column exists; decision_state initializes `evidence_gaps: []` | See **§2A** — **NOT** the same as the concept | **No proven V1 capability** | `case.py`; `_build_decision_state` | — |
| **Unknown** | value_state / decision unknowns / unmapped needs | **CONTRACT:** Unknown = explicitly not known (not guessed). Unmapped/ambiguous needs must not be silently invented (GAP-05) | **Yes** | ProfileFact value_state; need_normalization; decision_state | — |
| **Conflict** | Evidence.conflict_status; decision conflicts; CONFLICTED ProfileFact status | **CONTRACT:** Conflict must not be auto-resolved into false certainty for ranking | **Yes** | Evidence service; ProfileFact statuses | ProfileFact CONFLICTED as Rec input (**DEFERRED**) |
| **Next Question / Action** | No dedicated question engine verified | **PROPOSED (conceptual only):** A conceptual Evidence Gap *may* imply a next human question or operator action; V1 does **not** require a Questionnaire subsystem | **No (engine)** | — | Priority rules (**OPEN** / DEFERRED engine) |
| **Progressive Profiling** | Home collects concerns/skin; merge with saved profile; ProfileFact optional path exists | **CONTRACT:** Ask only when the answer can change eligibility, safety posture, or ranking rationale for *this* Case | **Yes (rule)** | NewHomePage; ProfileFact write boundary | Automated question selection (**DEFERRED**) |
| **Recommendation** | Case-owned generate; eligibility path; scores and reasons stored | Remains the product suggestion artifact for the Case | **Yes** | recommendation model/service | ProfileFact as input (**NOT authorized**) |
| **Follow-up / Outcome (V1 min)** | Feedback linked to Case and optional Recommendation; `outcome`, `rating`, `comment`, `follow_up_at` | **CONTRACT V1 min:** simple outcome/feedback; not full Outcome Assessment domain | **Yes (min)** | `feedback.py`, specialist router | Rich outcome model (**DEFERRED**) |
| **Questionnaire** | Customer.answers only | Not a consultation system | **No** | customer.py | — |
| **Image / Before-After** | Not verified | Out of V1 | **No** | — | — |

---

## 2A. Evidence Gap — Concept ≠ Persistence (review correction)

These must **not** be collapsed into one claim.

### A) Evidence Gap — **concept** (CONTRACT-level idea)

**Meaning:** Missing information that **materially blocks or weakens** a trustworthy recommendation *for this Case* (as distinct from a missing product Evidence row alone).

| Question | Status |
|----------|--------|
| Is the *idea* useful for Vertical Slice discussion? | **PROPOSED / CONTRACT candidate** |
| Is a dedicated Evidence Gap engine implemented? | **NOT VERIFIED** |

### B) Evidence Gap — **persistence capability** (Reality)

| Question | Reality on baseline | Evidence |
|----------|---------------------|----------|
| Does `Case.evidence_gaps` column exist? | **YES (schema FACT)** | `app/models/case.py` |
| Who writes `Case.evidence_gaps` in application code? | **NOT VERIFIED** — no assignment/write sites found under `app/` besides the column definition | repo search `evidence_gaps` |
| When is it written in consultation flow? | **NOT VERIFIED** | — |
| What structure/format is stored? | **NOT VERIFIED** (nullable String; no contract enforced in service layer found) | `Case.evidence_gaps` |
| Does generate persist gaps onto Case? | **NOT FACT** | `_build_decision_state` sets in-memory `"evidence_gaps": []` only |
| In-memory decision_state.evidence_gaps | Initialized empty; not proven as durable Case write | `recommendation_service.py` |

**CONTRACT:**

```text
Evidence Gap concept  ≠  Evidence Gap persistence capability
```

- Accepting the *concept* does **not** assert that `Case.evidence_gaps` is populated, structured, or authoritative in production consultation flows.
- Any implementation that claims “Evidence Gaps are persisted on Case” requires a separate Reality proof (writer + timing + format + tests).

**OPEN (persistence):**

| ID | Question |
|----|----------|
| G1 | Who is allowed to write decision-level gaps (system generate, operator, both)? |
| G2 | At what lifecycle point (pre-generate, post-generate, on INSUFFICIENT)? |
| G3 | Structure (free text, JSON list, codes)? |
| G4 | Is durable Case persistence required for V1, or is in-memory decision_state enough? |

---

## 3. LOCKED (Framework direction ∩ Reality — safe to treat as baseline)

1. **Customer is root identity**; Case is owned by Customer.  
2. **Recommendation is generated in a Case context**, not product-first browsing as the decision authority.  
3. **Eligibility / gating exists** in RecommendationService before treating a product as a successful recommendation path.  
4. **Product-side Evidence and ProductKnowledge remain the catalog authority**; consultation must not invent product claims.  
5. **GAP-05:** Customer need normalization is bounded; Product match surface is `ProductKnowledge.known_use_cases`.  
6. **ProfileFact is real and separate from Customer**; it is **not** currently a Recommendation input.  
7. **No parallel profile/case stack** may be introduced under this contract.  
8. **Unknown must not be coerced into false Known** for need mapping.  
9. **Problem / Assessment are not verified domain entities** on this baseline; Factor runtime list ≠ full domain chain.  
10. **Evidence Gap concept ≠ Case.evidence_gaps persistence** until a writer/format/timing is proven.  
11. **Implementation, migration, API, UI, Home redesign, scoring changes are not authorized by accepting vocabulary alone.**

---

## 4. PROPOSED (minimal glue — not implemented by this PR)

1. Vocabulary: *Profile (legacy Customer fields)* vs *ProfileFact* vs *Case context (visit)*.  
2. Evidence Gap as a **decision-level concept** only, until persistence is proven or authorized.  
3. Next Action as a human-readable implication of a gap (ask / defer / refer / no recommendation) — documentation only.  
4. Progressive Profiling as a process rule — no questionnaire module.  

---

## 5. OPEN (PO decisions required before implementation work)

| ID | Decision |
|----|----------|
| O1 | When both legacy Customer profile fields and ProfileFact exist, what is the **read precedence** for consultation (today Rec ignores ProfileFact)? |
| O2 | Is **writing** consultation answers into ProfileFact in-scope for first Vertical Slice, or remains manual/optional? |
| O3 | Must `Case.identified_needs` be **durably updated** on every generate, or is in-memory decision_state sufficient for V1? |
| O4 | Minimum **Follow-up** success criteria (feedback row only vs required `follow_up_at`)? |
| O5 | Any change toward Case/Need-first **Home IA** requires a separate UI authorization — confirm still deferred. |
| G1–G4 | Evidence Gap **persistence** questions in §2A |
| P1 | Are persisted Problem/Assessment entities ever required, or is concern→factor→need enough for V1? |

---

## 6. DEFERRED (explicitly out of V1)

- Questionnaire engine / progressive question planner  
- Image / before-after artifacts  
- AI extraction for profile or product  
- New Need entity table  
- New DecisionContext / Problem / Assessment tables (unless later authorized)  
- Full Outcome / Product Usage domain beyond existing Feedback  
- ProfileFact → Recommendation adapter  
- Product intake redesign; catalog AI  
- Scoring / weight / threshold changes  

---

## 7. Vertical Slice conceptual test (corrected order & honesty)

### 7.1 Framework-oriented chain (status per node)

| Step | Status on baseline |
|------|---------------------|
| Customer | **EXISTS** |
| Case | **EXISTS** |
| Problem (domain) | **NOT VERIFIED** |
| Assessment (domain) | **NOT VERIFIED** |
| Factor (runtime from concerns) | **PARTIAL** |
| Factor (persisted entity) | **NOT VERIFIED** |
| Evidence / Unknown / Conflict (product + decision signals) | **PARTIAL** (product Evidence EXISTS; decision gaps persistence NOT VERIFIED) |

### 7.2 Runtime path that actually runs today (FACT)

```text
Customer
  → Existing Profile/Context (Customer fields ± ProfileFact unused by Rec)
  → Interaction (Home / intake APIs)
  → Case
  → concerns → factors[] (in-memory)
  → Need normalization (GAP-05)
  → decision_state (computed; evidence_gaps list starts empty)
  → Eligible Products (eligibility path)
  → Recommendation + Reason
  → Customer Choice (PARTIAL UX)
  → Simple Follow-up (Feedback EXISTS)
```

| Step | Status |
|------|--------|
| Customer | **EXISTS** |
| Existing Profile/Context | **PARTIAL** (Rec does not use ProfileFact) |
| Interaction | **EXISTS** |
| Case | **EXISTS** |
| Problem → Assessment → Factor domain chain | **NOT VERIFIED** (replaced in runtime by concerns→factors) |
| Need | **PARTIAL** |
| Minimum Relevant Information / progressive engine | **PARTIAL** / **NOT VERIFIED** as engine |
| Assessment/reasoning as domain Assessment | **NOT VERIFIED**; computed decision_state = **PARTIAL** |
| Eligible Products | **EXISTS** |
| Recommendation + Reason | **EXISTS** |
| Customer Choice | **PARTIAL** |
| Simple Follow-up | **EXISTS** |

**Correction vs prior draft:** The slice must **not** imply `Case → Need → Assessment` as if Assessment were a verified domain stage after Need. Runtime builds **factors from concerns, then Needs**; Assessment-as-entity is **NOT VERIFIED**.

---

## 8. Reality → Contract traceability

| Contract statement | Reality anchor |
|--------------------|----------------|
| Customer root | `Customer` model |
| Case episode | `Case` model + ownership on cases API |
| Legacy profile fields | columns on `Customer` |
| ProfileFact durable facts | `ProfileFact` + `ProfileFactService` |
| Runtime factors from concerns | `_build_decision_state` |
| Need as normalized concept | `need_normalization`, `product_compatibility` |
| Decision context computed | `_build_decision_state` |
| Problem/Assessment entities | **absent** as models |
| Evidence Gap column | `Case.evidence_gaps` |
| Evidence Gap writers | **not found** in `app/` |
| Product evidence authority | `Evidence`, readiness/D3 on product lifecycle |
| Follow-up min | `Feedback.outcome/rating/follow_up_at` |
| Home mixed surface | `NewHomePage.tsx` panels |
| No ProfileFact in Rec | absence of usages in recommendation service |

---

## 9. Acceptance criteria for *this Contract* (documentation)

1. Baseline SHA recorded and matches the SHA used for evidence.  
2. Problem / Assessment / Factor each have explicit EXISTS / PARTIAL / NOT VERIFIED / PROPOSED status.  
3. Evidence Gap **concept** and **persistence** are separate subsections with distinct claims.  
4. No schema/API/UI/code change in the delivering PR.  
5. LOCKED vs PROPOSED vs OPEN vs DEFERRED are separable by a reviewer.  
6. Vertical Slice does not invent a Problem→Assessment domain chain.  
7. PO acceptance of this doc ≠ implementation authorization.  

---

## 10. Smallest next implementation unit (recommendation only — not executed)

After PO accepts this contract and resolves relevant OPEN items:

**Smallest unit:** A single consultation pass using *existing* APIs only (Case → generate → show reasons → optional Feedback), with honest documentation of what decision_state contains — **without** claiming Problem/Assessment entities or Case.evidence_gaps persistence until proven.

Still **out of scope** unless separately authorized: ProfileFact→Rec adapter, Home redesign, new tables, Evidence Gap writer design beyond contract.

---

## 11. Unauthorized changes checklist

| Change type | Authorized by this document? |
|-------------|------------------------------|
| Code / migration / API / UI | **No** |
| Recommendation formula | **No** |
| Home redesign | **No** |
| Merge of this PR without PO | **No** |

---

## 12. Review response log

| Finding (Mission Manager) | Response |
|---------------------------|----------|
| Vertical Slice obscured Problem→Assessment→Factor vs Need-first narrative | **Accepted.** §1A + §7 rewritten; domain chain statuses explicit; runtime path documented as concerns→factors→needs. |
| Evidence Gap concept conflated with persistence | **Accepted.** §2A splits concept vs `Case.evidence_gaps` capability; writers/timing/structure marked NOT VERIFIED / OPEN. |

*End of Minimal Consultation Contract v0.1 (rework)*
