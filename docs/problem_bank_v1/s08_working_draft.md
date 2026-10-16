# HBI — Problem Bank V1
## S08 WORKING DRAFT — NOT BASELINE
### Lesions / Growths / Change

**Execution owner:** GPT-2  
**Frozen source:** SKIN PROBLEM SPACE MAP V0.1, Issue #293  
**Scope:** P48, P49, P50, P53, P54, P55, P56 only  
**Repository base:** `a05e1708d24e2485c5f6307f8f85b2c676b6017d`

---

## 1. Scope lock

The frozen Map V0.1 explicitly places these seven units in S08:

| ID | Map concept | Map role |
|---|---|---|
| P48 | Moles / nevi | Lesion / clinical anchor / safety-aware |
| P49 | Changing mole | Safety / Referral Signal |
| P50 | New / growing skin lesion | Safety / Referral Signal |
| P53 | Suspicious skin-cancer lesion | Safety / Referral Signal |
| P54 | Suspicious melanoma lesion | Safety / Referral Signal |
| P55 | Bleeding / non-healing lesion | Safety / Referral Signal |
| P56 | Rapid change in lesion size / shape / color | Safety / Referral Signal |

**Explicit scope exclusion:** P46 and P47 are not S08 Concepts in the frozen Map. They remain S07 Concepts with an S07↔S08 relationship. This artifact does not duplicate or move them.

No Concept is added, removed, renamed, or transferred in the Map.

---

## 2. Method / evidence discipline

For every Concept:

**Concept → What is it? → Evidence / Provenance → Why HBI needs it? → HBI Role → HBI Classification → What it must NOT mean → Boundary → What is still missing? → Coverage / Capability Gap → Disposition**

Evidence is claim-level. Medical identity, HBI relevance, classification, Canonical Problem admission, Customer Reality, and Customer Language are separate claims.

**Customer Reality = NOT VERIFIED.**  
**Customer Language = NOT VERIFIED.**

The safety-sensitive concepts below are retained as Map-level safety/referral signals. This draft does not create diagnosis, treatment, referral, eligibility, or recommendation rules.

---

# 3. Concept-by-concept execution

## P48 — Moles / Nevi

### What is it?
Moles, also called nevi, are common skin growths/lesions. The American Academy of Dermatology describes moles as common and notes that they can be flat or slightly raised and vary in size, shape, and color.

### Evidence / Provenance
**Source:** American Academy of Dermatology, “Moles: Overview.”

**Exact supported claim:** Moles are also called nevi; they are common and may be flat or slightly raised. New moles or changes to existing moles in adults can be a sign requiring dermatologic assessment.

**Claim type:** Clinical identity / safety context.

**What it proves:** P48 has a recognized clinical identity and a defined observational boundary.

**What it does NOT prove:** It does not prove that a particular mole is benign or malignant, and does not establish Canonical HBI Problem or Need admission.

### Why HBI needs it?
A client may present with a mole or concern about a mole. Recognizing the presentation as a lesion category allows HBI to distinguish the existence of the lesion from later safety-sensitive observations.

### HBI Role
Lesion / clinical anchor with safety-aware boundary.

### HBI Classification
**CLINICAL LESION / PRESENTATION — Canonical HBI Problem admission NOT ESTABLISHED.**

### What it must NOT mean
- Not a diagnosis of benign nevus in an individual case.
- Not a diagnosis of melanoma or other skin cancer.
- Not automatic treatment eligibility.
- Not an ordinary-care recommendation rule.

### Boundary
P48 is the baseline lesion concept. Changes and warning characteristics are represented separately by P49, P50, P53–P56.

### What is still missing?
HBI Customer Reality, Customer Language, and evidence of a distinct HBI decision path.

### Coverage / Capability Gap
**OPEN:** clinical identity is established; HBI canonical status and operational role remain unproven.

### Disposition
**KEEP**

---

## P49 — Changing mole

### What is it?
A mole that changes in appearance or behavior over time. AAD identifies evolving/change in a mole as a warning sign that warrants professional assessment, while also noting that not every changing lesion is melanoma.

### Evidence / Provenance
**Source 1:** American Academy of Dermatology, “Moles: Overview.”

**Exact supported claim:** In adults, new moles and changes to existing moles can be a sign of melanoma; a mole that is growing, itching, bleeding, or changing should be assessed by a dermatologist.

**Source 2:** DermNet, “ABCDEFG of melanoma.”

**Exact supported claim:** A melanocytic naevus is usually stable, whereas melanoma can change over time; however, melanoma accounts for less than 3% of changing skin lesions.

**Claim type:** Safety / referral signal.

**What it proves:** P49 is a medically recognized change signal associated with the need for professional assessment.

**What it does NOT prove:** Change alone does not diagnose melanoma or another malignancy.

### Why HBI needs it?
A client can present with an existing mole that has changed. This is materially different from merely having a stable mole and must remain a safety-sensitive observation rather than an ordinary product/recommendation problem.

### HBI Role
Safety / Referral Signal.

### HBI Classification
**SAFETY / REFERRAL SIGNAL — not an Ordinary Care Need and not a diagnosis.**

### What it must NOT mean
- Not “changing mole = melanoma.”
- Not a diagnosis of malignancy.
- Not a treatment recommendation.
- Not an automatic disease classification.

### Boundary
P49 describes change in an existing mole. The underlying lesion remains undiagnosed within this artifact.

### What is still missing?
HBI Customer Reality and Language; formal HBI handling/triage boundary is outside this execution.

### Coverage / Capability Gap
**OPEN:** Map-level safety semantics are clear, but operational HBI workflow is not established.

### Disposition
**KEEP**

---

## P50 — New / growing skin lesion

### What is it?
A new skin lesion or a lesion/growth that is increasing or otherwise changing. AAD identifies new or growing spots/growths among skin-cancer warning presentations.

### Evidence / Provenance
**Source:** American Academy of Dermatology, “Skin cancer: Symptoms, diagnosis, and causes.”

**Exact supported claim:** A common early sign of skin cancer is a spot on the skin that is growing, bleeding, or changing; skin cancer can also present as a new or changing spot or growth.

**Claim type:** Safety-sensitive presentation.

**What it proves:** A new or growing skin lesion is a recognized warning presentation requiring careful clinical assessment.

**What it does NOT prove:** It does not establish that the lesion is cancerous or otherwise malignant.

### Why HBI needs it?
A client may present a newly appearing or growing lesion without knowing its identity. Capturing the presentation separately from a diagnosis prevents appearance-based inference.

### HBI Role
Safety / Referral Signal.

### HBI Classification
**SAFETY / REFERRAL SIGNAL — diagnosis not established.**

### What it must NOT mean
- Not “new/growing = cancer.”
- Not a diagnosis of melanoma or non-melanoma skin cancer.
- Not a product eligibility rule.
- Not a treatment protocol.

### Boundary
P50 is a presenting change/growth signal. Diagnostic identity remains unresolved.

### What is still missing?
HBI Customer Reality/Language and formal operational handling.

### Coverage / Capability Gap
**OPEN:** strong medical warning-sign evidence; HBI-specific operational boundary remains unverified.

### Disposition
**KEEP**

---

## P53 — Suspicious skin-cancer lesion

### What is it?
A lesion or skin finding considered suspicious for skin cancer based on clinical features. “Suspicious” is a qualifier indicating uncertainty and the need for professional evaluation, not a diagnosis.

### Evidence / Provenance
**Source:** American Academy of Dermatology, “Skin cancer: Symptoms, diagnosis, and causes.”

**Exact supported claim:** Skin cancer may appear as growing, bleeding, changing, or non-healing spots/growths, and a dermatologist can determine whether a spot is skin cancer or something else.

**Claim type:** Safety / diagnostic-boundary terminology.

**What it proves:** There is a legitimate clinical distinction between suspicious skin findings and confirmed diagnosis.

**What it does NOT prove:** Suspicion does not establish skin cancer.

### Why HBI needs it?
The Map needs a representation for findings that are outside ordinary cosmetic/ordinary-care inference and require clinical evaluation rather than product recommendation.

### HBI Role
Safety / Referral Signal.

### HBI Classification
**SAFETY-SENSITIVE PRESENTATION — not a diagnosis.**

### What it must NOT mean
- Not confirmed cancer.
- Not confirmed malignancy.
- Not a cancer subtype.
- Not an automatic product or treatment rule.

### Boundary
The word “suspicious” must remain epistemically explicit. The artifact records a safety-sensitive presentation, not the diagnosis behind it.

### What is still missing?
HBI operational handling, Customer Reality, and Customer Language.

### Coverage / Capability Gap
**OPEN:** classification boundary is clear; workflow implementation is intentionally outside scope.

### Disposition
**KEEP**

---

## P54 — Suspicious melanoma lesion

### What is it?
A skin lesion whose observed characteristics raise concern for melanoma. AAD describes evolving, asymmetric, irregularly bordered, variably colored, or otherwise changing spots as features that can warrant dermatologic examination.

### Evidence / Provenance
**Source:** American Academy of Dermatology, “Melanoma: Signs and symptoms.”

**Exact supported claim:** Melanoma can appear as a changing mole, a new/different spot, a growing spot with irregular border or multiple colors, or other changing growths. AAD recommends dermatologic examination when ABCDE warning signs are present.

**Claim type:** Safety / melanoma-screening boundary.

**What it proves:** There are recognizable warning presentations associated with possible melanoma.

**What it does NOT prove:** An appearance or warning sign alone does not diagnose melanoma.

### Why HBI needs it?
The Map must distinguish a melanoma-sensitive safety presentation from an ordinary skin concern so that the system does not silently treat a safety signal as a routine recommendation problem.

### HBI Role
Safety / Referral Signal.

### HBI Classification
**SAFETY-SENSITIVE PRESENTATION — not a melanoma diagnosis.**

### What it must NOT mean
- Not “ABCDE = melanoma.”
- Not a confirmed malignancy.
- Not a treatment recommendation.
- Not a product eligibility rule.

### Boundary
P54 is explicitly about suspicion. Confirmation remains outside this artifact.

### What is still missing?
HBI operational workflow and Customer Reality/Language.

### Coverage / Capability Gap
**OPEN:** evidence supports the warning-sign boundary; HBI operationalization remains unproven.

### Disposition
**KEEP**

---

## P55 — Bleeding / non-healing lesion

### What is it?
A skin lesion or sore that bleeds and/or fails to heal. AAD identifies bleeding growths and sores that do not heal or recur as warning presentations.

### Evidence / Provenance
**Source:** American Academy of Dermatology, “Skin cancer: Symptoms, diagnosis, and causes.”

**Exact supported claim:** Skin cancer can appear as a growing spot or bump that may bleed, or as a sore that does not heal or heals and returns.

**Source:** American Academy of Dermatology, “Squamous cell carcinoma: From symptoms to treatments.”

**Exact supported claim:** Squamous cell carcinoma can appear as a sore that does not heal and may bleed; growth or bleeding in a scar, wound, or sore warrants dermatologic assessment.

**Claim type:** Safety-sensitive presentation.

**What it proves:** Bleeding and non-healing are recognized warning features that can justify professional assessment.

**What it does NOT prove:** They do not establish skin cancer or squamous cell carcinoma.

### Why HBI needs it?
This is a high-salience safety presentation that should not be collapsed into ordinary skin texture, lesion, or product-selection semantics.

### HBI Role
Safety / Referral Signal.

### HBI Classification
**SAFETY / REFERRAL SIGNAL — not a diagnosis.**

### What it must NOT mean
- Not “bleeding = cancer.”
- Not “non-healing = SCC.”
- Not a confirmed malignancy.
- Not a treatment or recommendation rule.

### Boundary
The signal is defined by observed behavior of the lesion/sore. Etiology remains unresolved.

### What is still missing?
HBI workflow and Customer Reality/Language.

### Coverage / Capability Gap
**OPEN:** medical safety boundary is supported; HBI operational rule remains outside scope.

### Disposition
**KEEP**

---

## P56 — Rapid change in lesion size / shape / color

### What is it?
A lesion that changes rapidly in observable dimensions or appearance. The frozen Map records this as a Safety/Referral Signal.

### Evidence / Provenance
**Source:** American Academy of Dermatology, “What to look for: ABCDEs of melanoma.”

**Exact supported claim:** The “E” in ABCDE refers to an evolving spot that looks different or is changing in size, shape, or color.

**Source:** American Academy of Dermatology, “Moles: Signs and symptoms.”

**Exact supported claim:** A mole or skin lesion that looks different from others or is changing in size, shape, or color warrants dermatologic examination.

**Claim type:** Safety / evolving-lesion signal.

**What it proves:** Change in size, shape, or color is a recognized warning characteristic.

**What it does NOT prove:** The change does not establish melanoma or another malignancy.

### Why HBI needs it?
It captures a specific change pattern that should remain safety-sensitive and separate from generic lesion identity.

### HBI Role
Safety / Referral Signal.

### HBI Classification
**SAFETY / REFERRAL SIGNAL — not a diagnosis.**

### What it must NOT mean
- Not “rapid change = melanoma.”
- Not a confirmed cancer diagnosis.
- Not a treatment or product rule.
- Not a standalone malignancy classification.

### Boundary
P56 records the change signal only. Diagnostic identity remains outside this artifact.

### What is still missing?
HBI operational workflow and Customer Reality/Language.

### Coverage / Capability Gap
**OPEN:** evidence supports the safety signal; operational HBI handling is not established here.

### Disposition
**KEEP**

---

# 4. Disposition table

| Concept | Map role | Working classification | Primary disposition |
|---|---|---|---|
| P48 | Lesion / clinical anchor | Clinical lesion / presentation | **KEEP** |
| P49 | Safety / Referral Signal | Safety / Referral Signal | **KEEP** |
| P50 | Safety / Referral Signal | Safety / Referral Signal | **KEEP** |
| P53 | Safety / Referral Signal | Safety-sensitive presentation | **KEEP** |
| P54 | Safety / Referral Signal | Safety-sensitive presentation | **KEEP** |
| P55 | Safety / Referral Signal | Safety / Referral Signal | **KEEP** |
| P56 | Safety / Referral Signal | Safety / Referral Signal | **KEEP** |

**Exact count:** KEEP = 7; MERGE = 0; RECLASSIFY = 0; PARK = 0; REMOVE = 0; TOTAL = 7.

**Interpretation of KEEP:** retain the Map concept in the S08 working draft. It does **not** mean Canonical HBI Problem, HBI Need, treatment eligibility, or recommendation eligibility.

---

# 5. Cross-Shelf relations

### P46 / P47 ↔ S08
The frozen Map places P46 and P47 in S07 while explicitly recording S07↔S08 relationships.

**Working interpretation:** relation only. No duplication, movement, merge, or Map change.

### P48 → P49 / P50 / P53–P56
The Map explicitly describes P48 as the lesion/clinical anchor and the other concepts as safety-oriented descendants/signals.

This is a structural relationship in the Map, **not** a diagnostic pipeline.

---

# 6. Boundary findings

1. **Lesion ≠ Problem ≠ Need.** P48 has clinical identity, but Canonical HBI admission remains unproven.
2. **Clinical identity ≠ diagnosis of an individual lesion.** The artifact never identifies a user's lesion.
3. **Change ≠ malignancy.** AAD and DermNet support change as a warning characteristic, not as proof of melanoma/cancer. citeturn0search1turn0search13
4. **Safety signal ≠ diagnosis.** P49/P50/P53–P56 are retained in their Map-defined safety role.
5. **Appearance ≠ diagnosis.** AAD explicitly notes that a dermatologist determines whether a spot is skin cancer or something else. citeturn0search0
6. **P53/P54 “suspicious” must remain uncertain.** No confirmation is implied.
7. **P55 is not automatically cancer.** Bleeding/non-healing is a warning presentation, not a diagnosis. citeturn0search0turn0search7
8. **P56 is an evolving-lesion signal.** AAD's ABCDE framework supports size/shape/color change as a warning characteristic, not a diagnosis. citeturn0search3turn0search4

---

# 7. Safety findings

S08 is unusually safety-sensitive. Therefore:

- No diagnosis is made.
- No malignancy is asserted.
- No cancer subtype is inferred.
- No treatment protocol is created.
- No referral protocol is designed.
- No automatic eligibility rule is created.
- No product recommendation is generated.
- Safety/Referral status is recorded only because the frozen Map already defines these units that way.

The evidence supports the existence of warning-sign concepts. It does **not** authorize HBI operational logic.

---

# 8. Customer Reality / Customer Language

**Customer Reality = NOT VERIFIED**

**Customer Language = NOT VERIFIED**

Medical terms such as “mole,” “changing mole,” “new growth,” “bleeding,” and “non-healing sore” are retained as source terminology or Map terminology only.

No claim is made that these are the words HBI customers actually use.

---

# 9. Coverage / Capability Gaps

1. HBI-specific operational relevance is not independently established for P48.
2. P49/P50/P53–P56 have clear safety-sensitive clinical relevance, but no operational referral workflow is defined here.
3. Customer Reality remains unverified.
4. Customer Language remains unverified.
5. Final distinction between discovery-level Problem representation and Safety/Referral representation remains a later governance matter.
6. No evidence in this execution establishes any S08 Concept as a Canonical HBI Need.

---

# 10. SELF-CRITIQUE

### Medical Identity vs Canonical Admission
The draft deliberately keeps P48 despite strong medical identity evidence, but does not treat that evidence as Canonical HBI admission.

### Medical prominence vs KEEP
All seven concepts are KEEP only because the frozen Map already contains them in S08. KEEP here means execution/retention of the frozen concept, not independent approval.

### Appearance vs Diagnosis
The evidence was used to establish warning characteristics and clinical terminology only. No individual lesion is diagnosed.

### Safety vs Recommendation
Safety sensitivity is preserved without creating an eligibility, treatment, referral, or product rule.

### Cross-Shelf vs Map Change
P46/P47 are mentioned only to preserve the already-frozen S07↔S08 relationship. They are not copied into S08.

### Customer Reality / Language
No consumer wording is invented. Medical terminology is not presented as verified customer language.

### Scope
Only P48, P49, P50, P53, P54, P55, P56 are executed because those are the exact S08 records in the frozen Map.

### Evidence gaps
Where evidence supports a warning signal but not diagnosis or HBI workflow, the draft stops at that boundary rather than filling the gap by inference.

---

# 11. Governance footer

```
Map V0.1 = FROZEN / UNCHANGED

S08 Working Draft = EXECUTION ARTIFACT

Canonical Problem Admission = NOT ESTABLISHED

Customer Reality = NOT VERIFIED
Customer Language = NOT VERIFIED

Need Acceptance = OUT OF SCOPE
Product = OUT OF SCOPE
Recommendation = OUT OF SCOPE
Implementation = NOT AUTHORIZED

Independent Verification = PENDING
Management Acceptance = PENDING
Management Baseline = PENDING
Merge Authorization = NOT AUTHORIZED
```

**Execution end state:** S08 Execution = COMPLETED only after Artifact and PR Repository Reality are confirmed below.
