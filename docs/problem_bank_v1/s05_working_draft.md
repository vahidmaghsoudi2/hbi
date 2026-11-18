# HBI Problem Bank V1 — S05 Working Draft

**S05 WORKING DRAFT — NOT BASELINE**

**Scope:** S05 — Redness / Inflammation / Rash  
**Map Source:** Skin Problem Space Map V0.1 — ACCEPTED / FROZEN  
**Map Entries:** P24–P33 only  
**Customer Reality:** NOT VERIFIED  
**Customer Language:** NOT VERIFIED  
**Implementation:** NOT AUTHORIZED  
**Need Extraction:** OUT OF SCOPE  
**Need Acceptance:** OUT OF SCOPE  
**Product Mapping:** OUT OF SCOPE  
**Recommendation:** OUT OF SCOPE  

## Execution Boundary

This artifact executes only the ten pre-existing S05 entries from the frozen Map V0.1:

- P24 Persistent redness
- P25 Flushing
- P26 Rosacea
- P27 Eczema / Dermatitis
- P28 Atopic dermatitis
- P29 Allergic contact dermatitis
- P30 Seborrhoeic dermatitis
- P31 Psoriasis
- P32 Hives / Urticaria
- P33 Unspecified rash

No new Map concept is introduced. Map V0.1 is not modified or reopened. S01–S04 are not modified.

The governing HBI relevance question is limited to whether HBI must recognize a presentation, condition, symptom, or context in consultation so the operator can understand what is being presented, identify what information is missing, distinguish ordinary consultation from clinically significant situations, and avoid silently treating a presentation as a diagnosis. This is HBI consultation logic, not a medical claim.

## Evidence Discipline

Evidence is recorded at claim level:

**Source → Exact Supported Claim → Claim Type → What it proves → What it does NOT prove**

Medical/scientific evidence establishes clinical identity or presentation only. It does not by itself establish HBI canonical Problem admission, Customer Reality, Customer Language, Need acceptance, treatment eligibility, product suitability, or recommendation eligibility.

Customer Reality and Customer Language are intentionally not inferred from medical sources, public webpages, prevalence, or terminology.

---

## Concept Register

### P24 — Persistent redness

- **Problem ID:** P24
- **Canonical / Working Name:** Persistent redness
- **Concept Identity:** A visible, ongoing change in skin colour that can occur as a presentation of several underlying conditions. AAD describes persistent facial redness as a sign that may occur in rosacea and distinguishes it from transient flushing.
- **Evidence / Provenance:**
  - AAD, “Is rosacea causing your red, irritated face?” supports persistent/longer-lasting facial redness as a recognizable presentation and describes it as one of the signs that can occur with rosacea.
    - **Claim Type:** Clinical/scientific presentation evidence.
    - **Proves:** Persistent facial redness is a recognizable skin presentation and can be associated with rosacea.
    - **Does NOT prove:** that persistent redness is itself a diagnosis, that every case is rosacea, HBI Customer Reality, or canonical HBI admission.
  - AAD, “Rosacea: Diagnosis and treatment” supports persistent ongoing facial colour as a clinical sign for which medical assessment/treatment may be considered in rosacea.
    - **Claim Type:** Clinical/scientific clinical-management context.
    - **Proves:** Persistent redness can be clinically meaningful.
    - **Does NOT prove:** HBI canonical admission or product/recommendation eligibility.
- **HBI Relevance:** DIRECTLY_SUPPORTED
  - **Basis:** A persistent visible redness presentation is relevant to consultation because HBI must distinguish an observed presentation from a possible underlying condition and determine whether clarification or clinical evaluation is needed.
  - **Boundary of HBI claim:** This relevance is derived from the consultation role, not from prevalence or treatment evidence.
- **HBI Role:** PROBLEM / PRESENTATION
- **Canonical Status:** CANONICAL_PROBLEM_NOT_PROVEN
- **What it must NOT mean:** It must not mean rosacea, dermatitis, allergy, infection, or any other diagnosis without appropriate clinical assessment.
- **Boundary:** Persistent redness ≠ flushing ≠ rosacea. The visible colour change does not identify its cause.
- **Related / Overlap:** P25 Flushing; P26 Rosacea; P27 Eczema / Dermatitis; P29 Contact dermatitis; P30 Seborrhoeic dermatitis.
- **Coverage / Capability Gap:** G-S05-01 presentation-vs-condition separation; G-S05-02 persistent-vs-transient redness distinction; G-S05-03 cause clarification.
- **Disposition:** KEEP
- **Execution Status:** COMPLETED — WORKING DRAFT ONLY

### P25 — Flushing

- **Problem ID:** P25
- **Canonical / Working Name:** Flushing
- **Concept Identity:** A transient skin colour change associated with cutaneous vasodilation. DermNet describes flushing as occurring because skin blood vessels dilate and lists multiple possible causes.
- **Evidence / Provenance:**
  - DermNet, “Flushing” supports flushing as a recognized phenomenon caused by cutaneous vasodilation and notes multiple possible causes.
    - **Claim Type:** Clinical/scientific identity.
    - **Proves:** Flushing is a recognized manifestation/phenomenon with multiple possible causes.
    - **Does NOT prove:** a single diagnosis, HBI Customer Reality, or canonical Problem admission.
  - AAD, “Is rosacea causing your red, irritated face?” supports flushing/blushing as an early sign that can occur with rosacea.
    - **Claim Type:** Clinical/scientific association.
    - **Proves:** Flushing can occur in rosacea.
    - **Does NOT prove:** that flushing establishes rosacea.
- **HBI Relevance:** DIRECTLY_SUPPORTED
  - **Basis:** A transient redness/flushing presentation can be important consultation information because its pattern and context may materially affect how the operator understands the presentation and whether additional clinical clarification is required.
- **HBI Role:** SYMPTOM / MANIFESTATION / DISCOVERY SIGNAL
- **Canonical Status:** WORKING_CLASSIFICATION_ONLY
- **What it must NOT mean:** Flushing must not be treated as a diagnosis and must not be equated with rosacea.
- **Boundary:** Symptom/manifestation ≠ diagnosis. Flushing ≠ rosacea. Flushing ≠ persistent redness.
- **Related / Overlap:** P24 Persistent redness; P26 Rosacea.
- **Coverage / Capability Gap:** G-S05-04 transient symptom vs underlying condition; G-S05-05 trigger/context capture.
- **Disposition:** KEEP
- **Execution Status:** COMPLETED — WORKING DRAFT ONLY

### P26 — Rosacea

- **Problem ID:** P26
- **Canonical / Working Name:** Rosacea
- **Concept Identity:** A recognized inflammatory skin condition that commonly affects the face and may involve flushing, persistent colour change, visible vessels, acne-like breakouts, burning/stinging, and other signs. AAD explicitly treats rosacea as a skin condition requiring appropriate diagnosis.
- **Evidence / Provenance:**
  - AAD, “Rosacea: Signs and symptoms” supports rosacea as a clinical condition with multiple possible signs including flushing and persistent colour change.
    - **Claim Type:** Clinical/scientific identity and presentation.
    - **Proves:** Rosacea has a distinct clinical identity and can present through multiple manifestations.
    - **Does NOT prove:** HBI canonical Problem admission or Customer Reality.
  - AAD, “Rosacea: Diagnosis and treatment” supports clinical diagnosis and condition-specific management.
    - **Claim Type:** Clinical-management evidence.
    - **Proves:** Rosacea is clinically significant and may require condition-specific evaluation.
    - **Does NOT prove:** any HBI product or recommendation eligibility.
- **HBI Relevance:** DIRECTLY_SUPPORTED
  - **Basis:** HBI consultation must be able to recognize a possible named clinical condition so that it is not silently collapsed into generic redness, sensitivity, or acne-like presentation.
- **HBI Role:** CLINICAL_CONDITION / CLINICAL_ANCHOR
- **Canonical Status:** CANONICAL_PROBLEM_NOT_PROVEN
- **What it must NOT mean:** Recognition of the concept must not become diagnosis-by-rule or a claim that a customer has rosacea.
- **Boundary:** Rosacea ≠ persistent redness alone; rosacea ≠ flushing alone; rosacea ≠ acne. A presentation can overlap with other conditions.
- **Related / Overlap:** P24 Persistent redness; P25 Flushing; P27 Eczema / Dermatitis; P29 Contact dermatitis; P30 Seborrhoeic dermatitis.
- **Coverage / Capability Gap:** G-S05-06 condition-recognition vs diagnosis; G-S05-07 rosacea-vs-overlapping presentations.
- **Disposition:** KEEP
- **Execution Status:** COMPLETED — WORKING DRAFT ONLY

### P27 — Eczema / Dermatitis

- **Problem ID:** P27
- **Canonical / Working Name:** Eczema / Dermatitis
- **Concept Identity:** A broad clinical family involving inflammatory skin reactions/conditions. AAD explains that eczema refers to a group of conditions that cause rashes, itchiness, and excessively dry skin, while dermatitis can have different causes.
- **Evidence / Provenance:**
  - AAD, “Atopic dermatitis overview” supports eczema as a group of conditions causing rashes, itchiness, and dry skin and identifies atopic dermatitis as one type.
    - **Claim Type:** Clinical/scientific taxonomy and identity.
    - **Proves:** Eczema is an umbrella family rather than a single diagnosis.
    - **Does NOT prove:** that every dermatitis presentation is atopic dermatitis, HBI canonical admission, or Customer Reality.
  - AAD, “Contact dermatitis overview” supports contact dermatitis as a specific form of dermatitis caused by irritant or allergic reactions.
    - **Claim Type:** Clinical/scientific subtype boundary.
    - **Proves:** dermatitis contains clinically distinguishable subtypes.
    - **Does NOT prove:** HBI canonical admission.
- **HBI Relevance:** DIRECTLY_SUPPORTED
  - **Basis:** HBI must recognize an inflammatory/dermatitic presentation without prematurely collapsing an umbrella term into a specific diagnosis.
- **HBI Role:** CLINICAL FAMILY / UMBRELLA CONDITION
- **Canonical Status:** CANONICAL_PROBLEM_NOT_PROVEN
- **What it must NOT mean:** “Eczema/dermatitis” must not be treated as a single specific diagnosis or as equivalent to atopic dermatitis.
- **Boundary:** Eczema/dermatitis ≠ atopic dermatitis ≠ contact dermatitis ≠ seborrhoeic dermatitis. These can overlap clinically but are not interchangeable labels.
- **Related / Overlap:** P28 Atopic dermatitis; P29 Allergic contact dermatitis; P30 Seborrhoeic dermatitis; P31 Psoriasis; P33 Unspecified rash.
- **Coverage / Capability Gap:** G-S05-08 umbrella-vs-subtype granularity; G-S05-09 dermatitis differential boundary.
- **Disposition:** RECLASSIFY
- **Execution Status:** COMPLETED — WORKING DRAFT ONLY

### P28 — Atopic dermatitis

- **Problem ID:** P28
- **Canonical / Working Name:** Atopic dermatitis
- **Concept Identity:** A specific type of eczema/dermatitis with a distinct clinical identity. AAD identifies atopic dermatitis as one type of eczema and describes characteristic rash, itch, and dry-skin manifestations.
- **Evidence / Provenance:**
  - AAD, “Atopic dermatitis overview” supports atopic dermatitis as a distinct type of eczema and describes its clinical presentation.
    - **Claim Type:** Clinical/scientific identity.
    - **Proves:** Atopic dermatitis is a specific clinical condition within the broader eczema family.
    - **Does NOT prove:** HBI canonical Problem admission or Customer Reality.
- **HBI Relevance:** DIRECTLY_SUPPORTED
  - **Basis:** HBI must recognize a specific clinically significant dermatitis condition when it is presented or suspected so that it is not reduced to generic dryness, sensitivity, or rash.
- **HBI Role:** CLINICAL_CONDITION / CLINICAL_ANCHOR
- **Canonical Status:** CANONICAL_PROBLEM_NOT_PROVEN
- **What it must NOT mean:** Recognition is not diagnosis and does not establish that an individual customer has atopic dermatitis.
- **Boundary:** Atopic dermatitis ≠ generic eczema/rash; atopic dermatitis ≠ contact dermatitis; clinical overlap does not establish identity.
- **Related / Overlap:** P27 Eczema / Dermatitis; P29 Allergic contact dermatitis; P33 Unspecified rash.
- **Coverage / Capability Gap:** G-S05-10 specific-condition recognition; G-S05-11 non-diagnostic framing.
- **Disposition:** KEEP
- **Execution Status:** COMPLETED — WORKING DRAFT ONLY

### P29 — Allergic contact dermatitis

- **Problem ID:** P29
- **Canonical / Working Name:** Allergic contact dermatitis
- **Concept Identity:** A form of contact dermatitis caused by an allergic reaction to something contacting the skin. AAD distinguishes allergic contact dermatitis from irritant contact dermatitis and notes that contact dermatitis can produce rash, itch, burning/stinging, and swelling.
- **Evidence / Provenance:**
  - AAD, “Contact dermatitis overview” supports contact dermatitis as a skin disease caused by irritation or an allergic skin reaction and distinguishes these mechanisms.
    - **Claim Type:** Clinical/scientific identity and boundary.
    - **Proves:** Allergic contact dermatitis is a distinct clinical subtype of contact dermatitis.
    - **Does NOT prove:** HBI canonical admission, Customer Reality, or a specific allergen in an individual case.
  - AAD, “Contact dermatitis signs and symptoms” supports rash, itch, burning/stinging and other manifestations.
    - **Claim Type:** Clinical/scientific presentation evidence.
    - **Proves:** The condition can present with several manifestations relevant to consultation.
    - **Does NOT prove:** individual diagnosis or product causality.
- **HBI Relevance:** DIRECTLY_SUPPORTED
  - **Basis:** HBI consultation may need to distinguish a reaction associated with contact from generic redness/rash because cause, exposure history, and clinical boundary matter.
- **HBI Role:** CLINICAL_CONDITION / EXPOSURE-RELATED CLINICAL ANCHOR
- **Canonical Status:** CANONICAL_PROBLEM_NOT_PROVEN
- **What it must NOT mean:** It must not imply that a particular product or ingredient caused an individual's reaction without evidence.
- **Boundary:** Allergic contact dermatitis ≠ irritant contact dermatitis ≠ generic rash. Exposure association does not by itself establish allergy.
- **Related / Overlap:** P24 Persistent redness; P27 Eczema / Dermatitis; P30 Seborrhoeic dermatitis; P33 Unspecified rash.
- **Coverage / Capability Gap:** G-S05-12 allergic-vs-irritant distinction; G-S05-13 exposure/history boundary.
- **Disposition:** KEEP
- **Execution Status:** COMPLETED — WORKING DRAFT ONLY

### P30 — Seborrhoeic dermatitis

- **Problem ID:** P30
- **Canonical / Working Name:** Seborrhoeic dermatitis
- **Concept Identity:** A common chronic or relapsing form of eczema/dermatitis that mainly affects sebaceous-gland-rich regions such as the scalp, face, and trunk. DermNet describes it as an inflammatory condition with a recognizable clinical distribution and differential diagnosis.
- **Evidence / Provenance:**
  - DermNet, “Seborrhoeic dermatitis” supports seborrhoeic dermatitis as a chronic/relapsing form of eczema/dermatitis affecting sebaceous-gland-rich regions.
    - **Claim Type:** Clinical/scientific identity and distribution.
    - **Proves:** P30 has a distinct clinical identity within the dermatitis family.
    - **Does NOT prove:** HBI canonical admission or Customer Reality.
- **HBI Relevance:** DIRECTLY_SUPPORTED
  - **Basis:** HBI must recognize this distinct inflammatory condition so it is not automatically collapsed into generic redness, dry skin, dandruff, or unspecified rash.
- **HBI Role:** CLINICAL_CONDITION / CLINICAL_ANCHOR
- **Canonical Status:** CANONICAL_PROBLEM_NOT_PROVEN
- **What it must NOT mean:** The presence of redness, scale, or oily skin alone must not be interpreted as seborrhoeic dermatitis.
- **Boundary:** Seborrhoeic dermatitis ≠ generic dandruff ≠ psoriasis ≠ rosacea ≠ contact dermatitis. Differential overlap is explicitly recognized in clinical sources.
- **Related / Overlap:** P24 Persistent redness; P27 Eczema / Dermatitis; P31 Psoriasis; P33 Unspecified rash.
- **Coverage / Capability Gap:** G-S05-14 distribution/context boundary; G-S05-15 seborrhoeic-vs-overlapping inflammatory conditions.
- **Disposition:** KEEP
- **Execution Status:** COMPLETED — WORKING DRAFT ONLY

### P31 — Psoriasis

- **Problem ID:** P31
- **Canonical / Working Name:** Psoriasis
- **Concept Identity:** A chronic inflammatory skin condition characterized by excessive skin-cell production and visible patches/plaques; manifestations vary by type and location. AAD describes several forms and identifies some severe forms as requiring immediate medical care.
- **Evidence / Provenance:**
  - AAD, “Psoriasis: Overview” supports psoriasis as a distinct chronic skin condition with thick/scaly patches and multiple possible sites.
    - **Claim Type:** Clinical/scientific identity.
    - **Proves:** Psoriasis has a distinct clinical identity and variable presentation.
    - **Does NOT prove:** HBI canonical admission or Customer Reality.
  - AAD, “Psoriasis: Signs and symptoms” supports multiple types and notes that some severe forms can be serious and require immediate medical care.
    - **Claim Type:** Clinical/scientific severity/safety context.
    - **Proves:** psoriasis can include clinically significant presentations.
    - **Does NOT prove:** an HBI referral rule or individual diagnosis.
- **HBI Relevance:** DIRECTLY_SUPPORTED
  - **Basis:** HBI consultation must recognize psoriasis as a clinically significant possibility rather than reducing scaly/red patches to generic dryness or rash.
- **HBI Role:** CLINICAL_CONDITION / CLINICAL ANCHOR / SAFETY-SENSITIVE CONTEXT
- **Canonical Status:** CANONICAL_PROBLEM_NOT_PROVEN
- **What it must NOT mean:** This concept does not create a diagnostic or emergency referral rule. Recognition is not diagnosis.
- **Boundary:** Psoriasis ≠ eczema/dermatitis ≠ generic rash. Severe psoriasis manifestations may be safety-sensitive, but safety handling is not implemented here.
- **Related / Overlap:** P24 Persistent redness; P27 Eczema / Dermatitis; P33 Unspecified rash.
- **Coverage / Capability Gap:** G-S05-16 psoriasis-vs-eczema boundary; G-S05-17 safety-sensitive clinical presentation recognition.
- **Disposition:** KEEP
- **Execution Status:** COMPLETED — WORKING DRAFT ONLY

### P32 — Hives / Urticaria

- **Problem ID:** P32
- **Canonical / Working Name:** Hives / Urticaria
- **Concept Identity:** A skin reaction characterized by suddenly appearing raised bumps or patches, often intensely itchy; urticaria is the medical term for hives. AAD notes that some cases involve angioedema and that swelling of the face, mouth, or throat can require immediate medical care.
- **Evidence / Provenance:**
  - AAD, “Hives: FAQs” supports hives/urticaria as a skin reaction causing sudden raised bumps/patches and identifies urticaria as the medical term.
    - **Claim Type:** Clinical/scientific identity.
    - **Proves:** P32 is a recognized clinical reaction/presentation with a distinct identity.
    - **Does NOT prove:** HBI canonical admission or Customer Reality.
  - AAD, “Hives: Diagnosis and treatment” supports a safety boundary for facial/oral/throat swelling and breathing/swallowing difficulty.
    - **Claim Type:** Clinical safety evidence.
    - **Proves:** Some hives-associated presentations can be safety-sensitive.
    - **Does NOT prove:** an HBI operational referral rule or diagnosis in an individual.
- **HBI Relevance:** DIRECTLY_SUPPORTED
  - **Basis:** HBI must recognize sudden wheal-like rash as a distinct clinical presentation and must not silently collapse it into generic redness/rash.
- **HBI Role:** CLINICAL REACTION / CLINICAL ANCHOR / SAFETY-SENSITIVE CONTEXT
- **Canonical Status:** CANONICAL_PROBLEM_NOT_PROVEN
- **What it must NOT mean:** Hives do not automatically establish allergy, and recognition does not establish the trigger or diagnosis.
- **Boundary:** Urticaria ≠ generic rash ≠ allergic contact dermatitis. The term identifies a reaction pattern, not necessarily its cause.
- **Related / Overlap:** P24 Persistent redness; P29 Allergic contact dermatitis; P33 Unspecified rash.
- **Coverage / Capability Gap:** G-S05-18 reaction-pattern vs cause; G-S05-19 safety-sensitive swelling boundary.
- **Disposition:** KEEP
- **Execution Status:** COMPLETED — WORKING DRAFT ONLY

### P33 — Unspecified rash

- **Problem ID:** P33
- **Canonical / Working Name:** Unspecified rash
- **Concept Identity:** A non-diagnostic presentation label for a visible skin eruption when its specific cause or condition has not yet been established. Rash can represent multiple inflammatory, allergic, infectious, or other processes.
- **Evidence / Provenance:**
  - AAD, “10 reasons your face is red” demonstrates that redness/rash can have multiple causes including seborrhoeic dermatitis, rosacea, and contact dermatitis.
    - **Claim Type:** Clinical/scientific differential/presentation evidence.
    - **Proves:** A visible red/rash presentation can have multiple underlying explanations.
    - **Does NOT prove:** that “unspecified rash” is a diagnosis, HBI canonical admission, Customer Reality, or a single treatment path.
  - AAD contact dermatitis resources support rash as a manifestation of several contact-reaction patterns.
    - **Claim Type:** Clinical/scientific presentation evidence.
    - **Proves:** rash is a manifestation shared across conditions.
    - **Does NOT prove:** a cause or diagnosis.
- **HBI Relevance:** DIRECTLY_SUPPORTED
  - **Basis:** HBI consultation needs a safe non-diagnostic representation for an observed rash when the cause is not established, so that the consultation does not force a premature clinical label.
- **HBI Role:** DISCOVERY PROBLEM / NON-DIAGNOSTIC PRESENTATION
- **Canonical Status:** CANONICAL_PROBLEM_NOT_PROVEN
- **What it must NOT mean:** “Unspecified rash” must not be treated as a diagnosis or as evidence for any particular underlying condition.
- **Boundary:** Rash ≠ diagnosis. Unspecified rash ≠ eczema, rosacea, psoriasis, infection, allergy, or any other specific condition.
- **Related / Overlap:** P24 Persistent redness; P27 Eczema / Dermatitis; P29 Allergic contact dermatitis; P30 Seborrhoeic dermatitis; P31 Psoriasis; P32 Hives / Urticaria.
- **Coverage / Capability Gap:** G-S05-20 non-diagnostic placeholder boundary; G-S05-21 presentation-to-condition clarification.
- **Disposition:** KEEP
- **Execution Status:** COMPLETED — WORKING DRAFT ONLY

---

## S05 Coverage / Capability Gap Register

- **G-S05-01 — Presentation vs condition:** P24 must remain a presentation and must not be converted into a diagnosis.
- **G-S05-02 — Persistent vs transient redness:** P24 and P25 are related but not interchangeable.
- **G-S05-03 — Cause clarification:** redness alone does not identify an underlying condition.
- **G-S05-04 — Symptom/manifestation boundary:** P25 is a manifestation/discovery signal, not automatically a canonical Problem.
- **G-S05-05 — Trigger/context capture:** P25 may require context, but no trigger inference is made.
- **G-S05-06 — Condition recognition vs diagnosis:** P26 must not become diagnosis logic.
- **G-S05-07 — Overlapping inflammatory presentations:** rosacea can overlap with acne-like or dermatitis-like presentations.
- **G-S05-08 — Umbrella vs subtype granularity:** P27 is a broad family; P28–P30 are more specific clinical concepts.
- **G-S05-09 — Dermatitis differential boundary:** eczema/dermatitis terms are not interchangeable.
- **G-S05-10 — Specific-condition recognition:** P28 requires non-diagnostic framing.
- **G-S05-11 — Non-diagnostic framing:** recognizing P28 does not establish a customer diagnosis.
- **G-S05-12 — Allergic vs irritant distinction:** P29 must not imply allergy without supporting evidence.
- **G-S05-13 — Exposure/history boundary:** suspected contact causality is not established from product or ingredient names alone.
- **G-S05-14 — Distribution/context:** P30 has a characteristic clinical distribution but no diagnosis-by-location rule is created.
- **G-S05-15 — Overlap among inflammatory conditions:** P30 may resemble other inflammatory disorders.
- **G-S05-16 — Psoriasis-vs-eczema boundary:** P31 should not be collapsed into generic dermatitis.
- **G-S05-17 — Safety-sensitive psoriasis context:** severe presentations can be clinically urgent, but no referral rule is created here.
- **G-S05-18 — Reaction-pattern vs cause:** P32 identifies a reaction pattern, not necessarily an allergy or trigger.
- **G-S05-19 — Safety-sensitive swelling:** P32 can have clinically urgent manifestations; this is recorded as a boundary, not an implementation rule.
- **G-S05-20 — Non-diagnostic unspecified rash:** P33 is intentionally a presentation placeholder, not a diagnosis.
- **G-S05-21 — Presentation-to-condition clarification:** P33 must not force a premature condition label.

No Gap above is converted into a feature, schema, API, UI, rule engine, recommendation rule, or implementation requirement.

---

## S05 Disposition Summary

| Map Entry | Working Classification | HBI Relevance | Canonical Status | Disposition |
|---|---|---|---|---|
| P24 | Problem / Presentation | DIRECTLY_SUPPORTED | CANONICAL_PROBLEM_NOT_PROVEN | KEEP |
| P25 | Symptom / Manifestation / Discovery Signal | DIRECTLY_SUPPORTED | WORKING_CLASSIFICATION_ONLY | KEEP |
| P26 | Clinical Condition / Clinical Anchor | DIRECTLY_SUPPORTED | CANONICAL_PROBLEM_NOT_PROVEN | KEEP |
| P27 | Clinical Family / Umbrella Condition | DIRECTLY_SUPPORTED | CANONICAL_PROBLEM_NOT_PROVEN | RECLASSIFY |
| P28 | Clinical Condition / Clinical Anchor | DIRECTLY_SUPPORTED | CANONICAL_PROBLEM_NOT_PROVEN | KEEP |
| P29 | Clinical Condition / Exposure-related Anchor | DIRECTLY_SUPPORTED | CANONICAL_PROBLEM_NOT_PROVEN | KEEP |
| P30 | Clinical Condition / Clinical Anchor | DIRECTLY_SUPPORTED | CANONICAL_PROBLEM_NOT_PROVEN | KEEP |
| P31 | Clinical Condition / Safety-sensitive Context | DIRECTLY_SUPPORTED | CANONICAL_PROBLEM_NOT_PROVEN | KEEP |
| P32 | Clinical Reaction / Safety-sensitive Context | DIRECTLY_SUPPORTED | CANONICAL_PROBLEM_NOT_PROVEN | KEEP |
| P33 | Discovery Problem / Non-diagnostic Presentation | DIRECTLY_SUPPORTED | CANONICAL_PROBLEM_NOT_PROVEN | KEEP |

### Disposition interpretation

**KEEP** means the pre-existing Map concept remains in the S05 working inventory in its stated role. It does **not** mean Canonical Problem Accepted.

**RECLASSIFY** means the concept remains in the working artifact but its role is corrected to reflect its umbrella/family semantics. P27 is not removed from the Map and is not replaced by a new concept.

No concept is removed in this execution.

---

## Explicitly OPEN / UNKNOWN / NOT_PROVEN

1. No S05 concept is declared a Canonical HBI Problem solely from medical evidence.
2. P24 remains a presentation rather than a diagnosis.
3. P25 remains a symptom/manifestation/discovery signal; symptom alone is not an Accepted Need.
4. P26 remains a clinical condition/anchor; canonical Problem admission is not proven.
5. P27 is retained as an umbrella clinical family, not as a specific diagnosis.
6. P28–P32 remain clinically meaningful concepts, but Canonical Problem admission is not proven.
7. P31 and P32 contain safety-sensitive clinical boundaries, but no HBI referral rule is created.
8. P33 remains a non-diagnostic presentation placeholder.
9. Customer Reality remains NOT VERIFIED.
10. Customer Language remains NOT VERIFIED.
11. No Need extraction or Need acceptance occurred.
12. No product, treatment, recommendation, or scoring logic was created.

---

## Concepts Intentionally Not Accepted Beyond the Evidence

- No claim that any S05 concept is a final Canonical HBI Problem merely because its medical identity is established.
- No claim that DIRECTLY_SUPPORTED HBI Relevance equals Canonical Problem admission.
- No claim that P25 Flushing is a diagnosis.
- No claim that P24 Persistent redness identifies rosacea.
- No claim that P27 Eczema / Dermatitis is interchangeable with P28 Atopic dermatitis, P29 Allergic contact dermatitis, or P30 Seborrhoeic dermatitis.
- No claim that P29 establishes an allergen or product causality in an individual.
- No claim that P31 creates a referral or emergency rule.
- No claim that P32 establishes allergy or its trigger.
- No Customer Reality or Customer Language is inferred from medical literature, public webpages, or common terminology.

---

## Self-Critique

### Highest Overclaim Risk

The highest risk in S05 is treating strong clinical identity plus HBI consultation relevance as equivalent to Canonical Problem admission. This artifact deliberately does not make that jump.

### Greatest Granularity Risk

P27 is the main granularity risk. “Eczema / Dermatitis” is an umbrella family while P28–P30 are more specific clinical concepts. P27 is therefore RECLASSIFIED rather than silently treated as equivalent to the specific conditions.

### Greatest Semantic Risk

P25 Flushing is a manifestation. P33 Unspecified rash is a non-diagnostic presentation. Both can be useful in consultation without being diagnoses or Accepted Needs.

### Greatest Safety Boundary Risk

P31 and P32 can include clinically significant or urgent presentations. The artifact records those as safety-sensitive context only. It does not create operational referral logic.

### Evidence Interpretation Risk

Medical sources strongly support clinical identity and boundaries. They do not establish Customer Reality, Customer Language, or Canonical HBI Problem admission.

### HBI Relevance Risk

The HBI relevance statements use the existing consultation role and are intentionally kept separate from medical evidence. They do not claim prevalence, customer demand, product demand, or treatment eligibility.

### KEEP vs Canonical Check

All KEEP decisions are working-inventory decisions. None is equivalent to CANONICAL_PROBLEM_ACCEPTED.

### Related / Overlap vs Parent / Child Check

Related concepts are recorded as related/overlapping only. No new parent-child hierarchy is asserted.

### Gap-to-Feature Check

All Coverage / Capability Gaps remain observations for later governance. None is converted into implementation authorization.

---

## Governance / Execution State

**S05 EXECUTION = COMPLETED AS WORKING DRAFT**

**S05 STATUS = WORKING DRAFT / NOT BASELINE**

**S05 VERIFIED = NOT YET**

**S05 ACCEPTED = NOT YET**

**S05 BASELINE = NOT YET**

**S05 MERGED = NOT YET**

**S05 IMPLEMENTED = NO**

**Customer Reality = NOT VERIFIED**

**Customer Language = NOT VERIFIED**

**Implementation = NOT AUTHORIZED**

**Merge = NOT AUTHORIZED**

### Exactly What Changed

- Added one repository artifact for the ten pre-existing S05 Map entries P24–P33.
- Preserved Map V0.1 as frozen.
- Recorded claim-level clinical/scientific provenance.
- Separated medical identity from HBI consultation relevance.
- Recorded HBI role, canonical status, boundary, overlap, gap, disposition, and execution status for each S05 concept.
- Reclassified P27 as an umbrella clinical family without creating a new Map concept.
- Preserved symptom/manifestation, clinical-condition, and non-diagnostic presentation boundaries.
- Recorded safety-sensitive context without creating referral or implementation logic.
- Added a self-critique and governance state.

### Exactly What Did Not Change

- Problem Space Map V0.1 was not modified or reopened.
- S01–S04 were not modified.
- No new Problem ID was created.
- No Customer Reality or Customer Language was introduced.
- No Need extraction or Need acceptance occurred.
- No Product mapping, Recommendation, Scoring, Product Intelligence, treatment, diagnosis, or referral rule logic was created.
- No schema/API/DB/UI implementation was created.
- No PR was merged.
- No Management Baseline was issued.

---

## Source Index

1. AAD — Is rosacea causing your red, irritated face?: https://www.aad.org/public/diseases/rosacea/what-is/red-face
2. AAD — Rosacea: Signs and symptoms: https://www.aad.org/public/diseases/rosacea/what-is/symptoms
3. AAD — Rosacea: Diagnosis and treatment: https://www.aad.org/public/diseases/rosacea/treatment/diagnosis-treat
4. DermNet — Flushing: https://dermnetnz.org/topics/flushing
5. AAD — Atopic dermatitis overview: https://www.aad.org/public/diseases/eczema/types/atopic-dermatitis
6. AAD — Contact dermatitis overview: https://www.aad.org/public/diseases/eczema/types/contact-dermatitis
7. AAD — Contact dermatitis signs and symptoms: https://www.aad.org/public/diseases/eczema/types/contact-dermatitis/symptoms
8. DermNet — Seborrhoeic dermatitis: https://dermnetnz.org/topics/seborrhoeic-dermatitis
9. AAD — Psoriasis: Overview: https://www.aad.org/public/diseases/psoriasis/what/overview
10. AAD — Psoriasis: Signs and symptoms: https://www.aad.org/public/diseases/psoriasis/what/symptoms
11. AAD — Hives: FAQs: https://www.aad.org/public/diseases/a-z/hives-overview
12. AAD — Hives: Signs and symptoms: https://www.aad.org/public/diseases/a-z/hives-symptoms
13. AAD — Hives: Diagnosis and treatment: https://www.aad.org/public/diseases/a-z/hives-treatment
14. AAD — 10 reasons your face is red: https://www.aad.org/public/everyday-care/skin-care-secrets/face/facial-redness

---

## Final Execution Declaration

This file is an **execution artifact only**.

It does not constitute:

- independent verification,
- Accepted Execution Pass,
- Management Baseline,
- Merge Authorization,
- Implementation Authorization,
- Need Bank acceptance,
- Product mapping,
- Recommendation authorization.

**Next required stage: independent Reality Audit / Verification of S05.**

Execution Report ≠ Verification ≠ Acceptance ≠ Baseline ≠ Merge ≠ Implementation.
