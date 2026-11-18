# HBI Problem Bank V1 — S04 Working Draft

**Status:** S04 WORKING DRAFT — NOT BASELINE
**Scope:** S04 Pigmentation / Color
**Map Source:** Skin Problem Space Map V0.1 — ACCEPTED / FROZEN
**Map Entries:** P17–P23
**Customer Reality:** NOT VERIFIED
**Customer Language:** NOT VERIFIED
**Implementation:** NOT AUTHORIZED

## Execution Boundary

This artifact executes only the S04 entries already present in the frozen Map V0.1:

- P17 Hyperpigmentation / dark spots
- P18 Melasma
- P19 Post-inflammatory hyperpigmentation
- P20 Hypopigmentation
- P21 Vitiligo
- P22 Sun-related pigmentation
- P23 Poikiloderma

No new Map concept is introduced. The Map is not modified.

The governing HBI question used for relevance is limited to whether HBI must recognize a presentation, condition, or context in consultation so it can understand the customer's request, determine whether more information is needed, and distinguish ordinary consultation from clinically significant or referral-sensitive situations. This is an HBI Contract/Consultation inference, not a medical claim.

## Evidence Discipline

For each concept, medical/scientific identity is separated from HBI relevance and HBI classification.

Evidence format:

Source → Exact Supported Claim → Claim Type → What it proves → What it does NOT prove

Medical evidence does not by itself prove HBI relevance, canonical Problem admission, Customer Reality, Customer Language, treatment relevance, or recommendation eligibility.

---

## Concept Register

### P17 — Hyperpigmentation / Dark Spots

- **Map Entry:** P17
- **Canonical / Working Name:** Hyperpigmentation / Dark Spots
- **Concept Identity:** Increased or uneven skin coloration can present as darker spots or patches. Hyperpigmentation is an umbrella presentation with multiple possible causes rather than a single diagnosis.
- **Evidence / Provenance:**
  - DermNet, Skin pigmentation: lists hyperpigmentation/pigmentary disorders and multiple causes/categories of pigmentation change.
    - **Claim Type:** Clinical/scientific identity.
    - **Proves:** Pigmentation change is a recognized skin presentation and can have multiple underlying causes.
    - **Does NOT prove:** HBI relevance, Customer Reality, or that all dark spots share one diagnosis or treatment path.
  - AAD, How to fade dark spots in darker skin tones: describes dark spots/patches as a common dermatology presentation and emphasizes identifying the cause before treatment.
    - **Claim Type:** Clinical/scientific presentation evidence.
    - **Proves:** Dark spots/patches are a meaningful presenting skin concern and may have different causes.
    - **Does NOT prove:** HBI Customer Reality or canonical HBI admission.
- **HBI Relevance:** DIRECTLY_SUPPORTED
  - **Basis:** An altered-color presentation is directly within the governing consultation question: HBI must be able to recognize what the customer is presenting before deciding whether clarification, ordinary consultation, or clinical evaluation/referral is appropriate.
  - **Important boundary:** This relevance statement is an HBI Contract claim, not an inference from prevalence or medical treatment literature.
- **HBI Role:** PROBLEM / PRESENTATION
- **Canonical Status:** CANONICAL_PROBLEM_NOT_PROVEN
  - **Reason:** HBI Relevance is directly supported, but no independent Problem-Bank Contract criterion has been established in this execution that distinguishes P17 from the other umbrella pigmentary presentations and authorizes canonical admission. Therefore HBI Relevance does not imply Canonical Problem admission.
- **Boundary:** Hyperpigmentation / dark spots ≠ Melasma ≠ Post-inflammatory hyperpigmentation ≠ Sun-related pigmentation. The visible color change does not identify its cause.
- **Related / Overlap:** P18, P19, P22; P13 from S03 may overlap when acne is the antecedent cause.
- **Coverage / Capability Gap:** G-S04-01 Cause-vs-Presentation Separation; G-S04-02 Pigmentation Differential/Boundary; G-S04-03 Need for context/history before classification.
- **Disposition:** KEEP
- **Execution Status:** COMPLETED — WORKING DRAFT ONLY

### P18 — Melasma

- **Map Entry:** P18
- **Canonical / Working Name:** Melasma
- **Concept Identity:** Melasma is a recognized pigmentary skin condition characterized by darker patches, commonly on the face/neck. AAD notes that melasma can resemble other conditions and may require clinical assessment to distinguish it.
- **Evidence / Provenance:**
  - AAD, Melasma: Diagnosis and treatment: supports melasma as a skin condition presenting with uneven/darker facial coloration and notes diagnostic differentiation from other conditions.
    - **Claim Type:** Clinical/scientific identity and diagnostic-boundary evidence.
    - **Proves:** Melasma is a distinct clinical condition and darker facial coloration does not automatically establish melasma.
    - **Does NOT prove:** HBI Customer Reality, treatment eligibility, or recommendation eligibility.
  - AAD, Melasma: Self-care: supports melasma as a condition involving increased melanocyte activity and darker spots.
    - **Claim Type:** Clinical/scientific identity.
    - **Proves:** The condition has a distinct clinical identity and pigmentation presentation.
    - **Does NOT prove:** HBI canonical admission by itself.
- **HBI Relevance:** DIRECTLY_SUPPORTED
  - **Basis:** HBI consultation must distinguish a named/possible clinical pigmentation condition from a generic dark-spot presentation because the consultation path may require more information or clinician evaluation rather than treating the label as an ordinary cosmetic descriptor.
  - **Important boundary:** This does not authorize treatment logic or product eligibility.
- **HBI Role:** CLINICAL_CONDITION / CLINICAL_ANCHOR
- **Canonical Status:** CANONICAL_PROBLEM_NOT_PROVEN
- **Boundary:** Melasma ≠ generic hyperpigmentation/dark spots. A dark patch is not sufficient to diagnose melasma. Melasma ≠ post-inflammatory hyperpigmentation.
- **Related / Overlap:** P17; P22 may be a contextual relation because UV exposure can influence pigmentation/melasma.
- **Coverage / Capability Gap:** G-S04-02 Differential boundary; G-S04-04 Clinical-condition recognition vs non-diagnostic presentation.
- **Disposition:** KEEP
- **Execution Status:** COMPLETED — WORKING DRAFT ONLY

### P19 — Post-inflammatory Hyperpigmentation

- **Map Entry:** P19
- **Canonical / Working Name:** Post-inflammatory Hyperpigmentation
- **Concept Identity:** Pigmentation that follows injury or an inflammatory skin disorder. DermNet describes it as pigmentation occurring at the site of the original disease after it has healed.
- **Evidence / Provenance:**
  - DermNet, Postinflammatory hyperpigmentation: supports PIH as pigmentation following injury or inflammatory skin disease and describes it as occurring at the site of the original disorder.
    - **Claim Type:** Clinical/scientific identity and sequela relationship.
    - **Proves:** PIH is a recognized post-inflammatory pigmentation presentation/sequela.
    - **Does NOT prove:** HBI Customer Reality or canonical Problem admission.
- **HBI Relevance:** DIRECTLY_SUPPORTED
  - **Basis:** PIH is a meaningful pigmentation presentation that can be relevant when a customer presents discoloration after a preceding inflammatory/skin event; HBI must distinguish it from generic hyperpigmentation and from an active underlying condition.
  - **Important boundary:** The relevance is to recognition/classification in consultation, not to automatic treatment or recommendation.
- **HBI Role:** SEQUELA / PRESENTATION
- **Canonical Status:** WORKING_CLASSIFICATION_ONLY
- **Boundary:** PIH ≠ generic hyperpigmentation; PIH ≠ active inflammatory disease; PIH ≠ melasma. The pigmentation is a sequela linked to a prior inflammatory/injury event.
- **Related / Overlap:** P17; S03 P13 Acne Aftermath may overlap when acne is the antecedent inflammatory condition.
- **Coverage / Capability Gap:** G-S04-05 Antecedent-condition linkage; G-S04-01 Presentation vs underlying/preceding condition.
- **Disposition:** RECLASSIFY / KEEP AS WORKING CONCEPT
- **Execution Status:** COMPLETED — WORKING DRAFT ONLY

### P20 — Hypopigmentation

- **Map Entry:** P20
- **Canonical / Working Name:** Hypopigmentation
- **Concept Identity:** Reduced skin pigmentation/paler areas are recognized pigmentary presentations with multiple possible causes. DermNet distinguishes hypopigmentation from complete depigmentation and lists inflammatory, infectious, scarring and other causes.
- **Evidence / Provenance:**
  - DermNet, Pigmentation disorders: supports hypopigmentation/pale patches as a recognized presentation with multiple possible causes, including post-inflammatory change, infection and scarring.
    - **Claim Type:** Clinical/scientific identity and differential-boundary evidence.
    - **Proves:** Reduced pigmentation is a meaningful presentation and is not a single diagnosis.
    - **Does NOT prove:** HBI relevance, Customer Reality, or a single treatment path.
- **HBI Relevance:** DIRECTLY_SUPPORTED
  - **Basis:** Altered color in the direction of reduced pigmentation is within the S04 consultation recognition space and may require clarification of cause before any ordinary care path is considered.
- **HBI Role:** PROBLEM / PRESENTATION
- **Canonical Status:** CANONICAL_PROBLEM_NOT_PROVEN
- **Boundary:** Hypopigmentation ≠ Vitiligo ≠ complete depigmentation. A pale patch alone does not establish an autoimmune or other specific condition.
- **Related / Overlap:** P21; P19 where post-inflammatory hypopigmentation is the relevant sequela; P17 as the opposite direction of pigment alteration.
- **Coverage / Capability Gap:** G-S04-06 Hypopigmentation-vs-specific-condition boundary; G-S04-07 Cause differentiation.
- **Disposition:** KEEP
- **Execution Status:** COMPLETED — WORKING DRAFT ONLY

### P21 — Vitiligo

- **Map Entry:** P21
- **Canonical / Working Name:** Vitiligo
- **Concept Identity:** Vitiligo is an autoimmune medical condition in which melanocytes are attacked, causing loss of skin color. AAD explicitly identifies vitiligo as a medical condition and notes increased susceptibility to sunburn in depigmented areas.
- **Evidence / Provenance:**
  - AAD, Is vitiligo a medical condition?: supports vitiligo as an autoimmune medical condition involving melanocyte destruction and loss of skin color.
    - **Claim Type:** Clinical/scientific identity and medical-boundary evidence.
    - **Proves:** Vitiligo has a distinct clinical identity and is not merely a cosmetic descriptor.
    - **Does NOT prove:** HBI Customer Reality, treatment authorization, or product suitability.
  - AAD, Vitiligo: Diagnosis and treatment: supports clinical management and camouflage as distinct from simply describing a pale patch.
    - **Claim Type:** Clinical management context.
    - **Proves:** Vitiligo can require condition-specific clinical management.
    - **Does NOT prove:** any HBI recommendation eligibility.
- **HBI Relevance:** DIRECTLY_SUPPORTED
  - **Basis:** HBI must recognize a clinically significant pigmentation condition when it is presented or suspected so it is not silently collapsed into a generic light-spot category.
- **HBI Role:** CLINICAL_CONDITION / REFERRAL-SENSITIVE CLINICAL_ANCHOR
- **Canonical Status:** CANONICAL_PROBLEM_NOT_PROVEN
- **Boundary:** Vitiligo ≠ generic hypopigmentation. A pale/white patch does not establish vitiligo. Recognition does not equal diagnosis.
- **Related / Overlap:** P20; broader S04 pigmentation presentation.
- **Coverage / Capability Gap:** G-S04-08 Clinical-condition recognition without diagnosis; G-S04-09 Referral-sensitive pigmentation boundary.
- **Disposition:** KEEP
- **Execution Status:** COMPLETED — WORKING DRAFT ONLY

### P22 — Sun-related Pigmentation

- **Map Entry:** P22
- **Canonical / Working Name:** Sun-related Pigmentation
- **Concept Identity:** Pigmentation can be associated with ultraviolet exposure and photoageing. DermNet lists pigmentation changes among photoageing features; AAD notes sunlight can darken melasma and other dark spots.
- **Evidence / Provenance:**
  - DermNet, Skin ageing: supports pigmentation/dyspigmentation as a feature associated with photoageing.
    - **Claim Type:** Clinical/scientific context.
    - **Proves:** UV/photoageing can be associated with pigmentation change.
    - **Does NOT prove:** that every sun-associated dark spot has one diagnosis.
  - AAD, Melasma: Diagnosis and treatment: supports sunlight as a factor that can darken existing melasma and contribute to pigmentary change.
    - **Claim Type:** Clinical/scientific contextual evidence.
    - **Proves:** sunlight can influence pigmentation in at least relevant pigmentary conditions.
    - **Does NOT prove:** HBI Customer Reality or a standalone diagnosis.
- **HBI Relevance:** INDIRECTLY_SUPPORTED
  - **Basis:** Sun/UV exposure is useful consultation context for interpreting pigmentation and distinguishing context from the presenting pigmentation problem.
  - **Important boundary:** The context itself is not automatically a canonical Problem or Need.
- **HBI Role:** CONTEXT / DESCRIPTOR
- **Canonical Status:** WORKING_CLASSIFICATION_ONLY
- **Boundary:** Sun-related context ≠ a specific pigmentation diagnosis. UV exposure ≠ melasma and does not by itself identify the cause of a pigment change.
- **Related / Overlap:** P17, P18, P23; S09 UV-related change.
- **Coverage / Capability Gap:** G-S04-10 Context capture; G-S04-11 Pigmentation-vs-UV-context separation.
- **Disposition:** RECLASSIFY / KEEP AS CONTEXT
- **Execution Status:** COMPLETED — WORKING DRAFT ONLY

### P23 — Poikiloderma

- **Map Entry:** P23
- **Canonical / Working Name:** Poikiloderma / Poikiloderma of Civatte
- **Concept Identity:** Poikiloderma of Civatte is a benign chronic condition characterized by a combination of hyperpigmentation/hypopigmentation, fine telangiectasia and atrophic change, commonly in sun-exposed areas. DermNet places it among pigmentary disorders.
- **Evidence / Provenance:**
  - DermNet, Poikiloderma of Civatte: supports the condition's identity as a benign chronic pigmentary disorder with combined pigmentary, vascular and atrophic features.
    - **Claim Type:** Clinical/scientific identity.
    - **Proves:** P23 has a distinct clinical identity and is not simply synonymous with hyperpigmentation.
    - **Does NOT prove:** HBI relevance, Customer Reality, or canonical Problem admission.
  - DermNet case material also supports the typical sun-exposed distribution and mixed clinical features.
    - **Claim Type:** Clinical/scientific presentation evidence.
    - **Proves:** The presentation overlaps pigmentation and UV-related change.
    - **Does NOT prove:** that HBI should treat or recommend for it.
- **HBI Relevance:** NOT_PROVEN / UNKNOWN
  - **Basis:** The Map itself marked P23 as Parked/Evidence Boundary. The medical identity is supported, but the current evidence and HBI Contract do not independently establish admission as an HBI canonical Problem at this execution stage.
- **HBI Role:** CLINICAL_CONDITION / CROSS-SHELF PRESENTATION
- **Canonical Status:** CANONICAL_PROBLEM_NOT_PROVEN
- **Boundary:** Poikiloderma ≠ simple hyperpigmentation; it combines pigmentary, vascular and atrophic changes. It also overlaps S09 but is not reduced to UV context.
- **Related / Overlap:** P17, P22; S09 UV-related change; vascular/redness concepts outside S04 may be relevant but are not executed here.
- **Coverage / Capability Gap:** G-S04-12 P23 HBI admission boundary; G-S04-13 Pigmentary vs vascular/atrophic mixed presentation.
- **Disposition:** PARK
- **Execution Status:** COMPLETED — WORKING DRAFT ONLY

---

## S04 Coverage / Capability Gap Register

- **G-S04-01 — Presentation vs Cause:** P17 and P20 are presentations/umbrella categories, not single diagnoses.
- **G-S04-02 — Pigmentation Differential Boundary:** P17 must not absorb P18/P19/P21/P23 merely because all can alter skin color.
- **G-S04-03 — Clarification / History:** pigmentation often requires context/history before a more specific classification can be supported.
- **G-S04-04 — Clinical Condition Recognition:** P18/P21 require distinction between recognition of a named condition and making a diagnosis.
- **G-S04-05 — Antecedent Linkage:** P19 depends conceptually on a preceding inflammatory/injury event.
- **G-S04-06 — Hypopigmentation Boundary:** P20 must not be collapsed into P21.
- **G-S04-07 — Cause Differentiation:** pale patches can have multiple causes.
- **G-S04-08 — Non-diagnostic Clinical Recognition:** P21 recognition must not become diagnosis logic.
- **G-S04-09 — Referral-sensitive Boundary:** P21 is clinically significant, but no referral rule is created here.
- **G-S04-10 — Context Capture:** P22 is context, not automatically a Problem.
- **G-S04-11 — UV Context Separation:** sun exposure does not identify a pigmentation diagnosis.
- **G-S04-12 — P23 HBI Admission:** medical identity is proven, HBI relevance remains UNKNOWN.
- **G-S04-13 — Mixed Presentation:** P23 includes pigmentary, vascular and atrophic elements and should not be flattened into pigmentation alone.

No Gap above is converted into a feature, schema, API, UI, rule engine, or implementation requirement.

## S04 Disposition Summary

| Map Entry | Working Classification | HBI Relevance | Canonical Status | Disposition |
|---|---|---|---|---|
| P17 | Problem / Presentation | DIRECTLY_SUPPORTED | CANONICAL_PROBLEM_NOT_PROVEN | KEEP |
| P18 | Clinical Condition / Clinical Anchor | DIRECTLY_SUPPORTED | CANONICAL_PROBLEM_NOT_PROVEN | KEEP |
| P19 | Sequela / Presentation | DIRECTLY_SUPPORTED | WORKING_CLASSIFICATION_ONLY | RECLASSIFY / KEEP AS WORKING CONCEPT |
| P20 | Problem / Presentation | DIRECTLY_SUPPORTED | CANONICAL_PROBLEM_NOT_PROVEN | KEEP |
| P21 | Clinical Condition / Referral-sensitive Clinical Anchor | DIRECTLY_SUPPORTED | CANONICAL_PROBLEM_NOT_PROVEN | KEEP |
| P22 | Context / Descriptor | INDIRECTLY_SUPPORTED | WORKING_CLASSIFICATION_ONLY | RECLASSIFY / KEEP AS CONTEXT |
| P23 | Clinical Condition / Cross-shelf Presentation | NOT_PROVEN / UNKNOWN | CANONICAL_PROBLEM_NOT_PROVEN | PARK |

## Explicitly OPEN / UNKNOWN / NOT_PROVEN

1. P23 HBI operational relevance remains NOT_PROVEN / UNKNOWN.
2. P18/P21 canonical Problem admission is NOT_PROVEN even though medical identity and HBI relevance are supported.
3. P19 remains a working sequela classification; no final canonical decomposition is asserted.
4. P17 remains an umbrella presenting category; underlying-cause decomposition is OPEN.
5. P20 remains an umbrella presentation; specific-cause differentiation is OPEN.
6. P22 remains Context/Descriptor, not an accepted independent Problem.
7. Customer Reality and Customer Language remain NOT VERIFIED.
8. No severity model is created.
9. No treatment, diagnosis, referral, recommendation, product-suitability, or scoring rule is created.

## Concepts Intentionally Not Accepted Beyond the Evidence

- No claim that all pigmentation concepts are independent canonical Problems.
- No claim that P18 Melasma or P21 Vitiligo are HBI canonical Problems merely because they are established medical conditions.
- No claim that P22 Sun-related Pigmentation is a diagnosis or independent Problem.
- No claim that P23 Poikiloderma is HBI-relevant merely because its medical identity is well established.
- No Customer Reality or Customer Language is inferred from medical literature, public webpages, or terminology.

## Self-Critique

### Highest Overclaim Risk
P17 HBI relevance and P21 HBI relevance are the strongest HBI claims. P17 previously carried an unsupported jump from HBI relevance to canonical admission; that claim is corrected here to CANONICAL_PROBLEM_NOT_PROVEN. They are grounded in the governing consultation question, not in medical evidence. They should therefore remain explicitly labeled as HBI Contract claims and not be presented as medical evidence.

### Greatest Classification Ambiguity
P17 is the largest classification ambiguity because dark spots/hyperpigmentation is an umbrella presentation with many causes. P20 has a parallel issue for pale/hypopigmented areas.

### Evidence Interpretation Risk
P23 has strong medical identity evidence but weak evidence for HBI admission. It is therefore deliberately PARKED rather than promoted.

### Boundary Still OPEN
P17 vs P18/P19/P22 and P20 vs P21 require further consultation-boundary work. P23 also crosses pigmentary, vascular and UV-related dimensions.

### Clinical Identity vs HBI Relevance Check
The artifact keeps these separate. Medical identity is recorded under Evidence/Provenance; HBI relevance is separately justified under the consultation question.

### KEEP vs Canonical Check
KEEP is not treated as canonical admission. P17, P18, P20 and P21 remain CANONICAL_PROBLEM_NOT_PROVEN; P19 and P22 are working classifications; P23 is parked.

### Related/Overlap vs Parent/Child Check
No new parent-child hierarchy is asserted. Cross-shelf relationships are recorded as related/overlapping/contextual only.

### Unsupported HBI Requirement Check
No new feature or operational requirement is declared from a Gap. Gaps remain capability/coverage questions only.

## Governance / Execution State

**S04 EXECUTION = COMPLETED AS WORKING DRAFT**
**S04 STATUS = WORKING DRAFT / NOT BASELINE**
**S04 VERIFIED = NOT YET**
**S04 ACCEPTED = NOT YET**
**S04 BASELINE = NOT YET**
**S04 MERGED = NOT YET**
**S04 IMPLEMENTED = NO**

### Exactly What Changed

- Added one repository artifact containing the S04 Working Draft for the seven pre-existing Map entries P17–P23.
- Added claim-level evidence/provenance notes.
- Added separate HBI relevance assessments.
- Added HBI roles, canonical-status distinctions, boundaries, overlaps, gaps, dispositions, execution status, and self-critique.
- Recorded P23 as PARKED because HBI relevance is not proven.
- Preserved P19 as a working sequela concept and P22 as context rather than forcing either into canonical Problem status.

### Exactly What Did Not Change

- Problem Space Map V0.1 was not modified or reopened.
- P01–P16 and the accepted S03 Management Baseline were not modified.
- No new Problem ID was created.
- No Customer Reality or Customer Language was introduced.
- No Need extraction or Need acceptance occurred.
- No Product mapping, Recommendation, Scoring, Product Intelligence, treatment, diagnosis, or referral rule logic was created.
- No schema/API/DB/UI implementation was created.
- No PR was merged.
- No Management Baseline authorization was issued.

## Source Index

1. DermNet — Skin pigmentation: https://dermnetnz.org/topics/skin-pigmentation-problems
2. DermNet — Postinflammatory hyperpigmentation: https://dermnetnz.org/topics/postinflammatory-hyperpigmentation
3. AAD — Melasma: Diagnosis and treatment: https://www.aad.org/public/diseases/a-z/melasma-treatment
4. AAD — Melasma: Self-care: https://www.aad.org/public/diseases/a-z/melasma-self-care
5. DermNet — Pigmentation disorders: https://dermnetnz.org/topics/pigmentation-disorders
6. AAD — Is vitiligo a medical condition?: https://www.aad.org/public/diseases/a-z/vitiligo-medical-condition
7. AAD — Vitiligo: Diagnosis and treatment: https://www.aad.org/public/diseases/a-z/vitiligo-treatment
8. DermNet — Skin ageing: https://dermnetnz.org/topics/ageing-skin
9. DermNet — Poikiloderma of Civatte: https://dermnetnz.org/topics/poikiloderma-of-civatte
10. AAD — How to fade dark spots in darker skin tones: https://www.aad.org/public/everyday-care/skin-care-secrets/routine/fade-dark-spots


## Correction Record — P17 Canonical Status

- **Correction Trigger:** Independent review identified an unsupported inference from DIRECTLY_SUPPORTED HBI Relevance to CANONICAL_PROBLEM_SUPPORTED.
- **Correction:** P17 Canonical Status changed to **CANONICAL_PROBLEM_NOT_PROVEN**.
- **HBI Relevance:** remains **DIRECTLY_SUPPORTED**.
- **Disposition:** remains **KEEP**.
- **Reason:** no independent Problem-Bank Contract criterion was established in this execution that authorizes canonical admission for P17 or distinguishes it from the other umbrella pigmentary presentations.
- **Boundary preserved:** HBI Relevance ≠ Canonical Problem Admission.
- **Scope impact:** P17 only. P18–P23, Map V0.1, S03, and all downstream scopes remain unchanged.
- **Status:** Correction applied; independent verification required. S04 remains WORKING DRAFT / NOT BASELINE.

## Correction Self-Critique — P17

- The original classification overreached by treating strong HBI relevance as sufficient for canonical admission.
- Medical evidence supports P17 identity as a pigmentary presentation, but does not itself establish HBI canonical admission.
- No new evidence was invented to justify the correction.
- The corrected state is intentionally conservative and leaves canonical admission OPEN for a later gate.
