# HBI — Problem Bank V1
## S07 WORKING DRAFT — NOT BASELINE
### Texture / Keratinization / Surface Growth

**Execution owner:** GPT-2  
**Frozen source:** HBI — SKIN PROBLEM SPACE MAP V0.1  
**Management registration:** Issue #293, S07 Execution Mission (comment 5978680852)  
**Scope:** P43–P47 only  
**Repository base:** `a05e1708d24e2485c5f6307f8f85b2c676b6017d`

---

## 1. Scope / Map source

The frozen Map V0.1 management registration defines S07 as:

| ID | Frozen Map concept |
|---|---|
| P43 | Uneven skin texture |
| P44 | Hyperkeratosis |
| P45 | Keratosis pilaris |
| P46 | Seborrhoeic keratosis |
| P47 | Skin tags |

No concept outside P43–P47 is examined here.

**Execution boundary:** this artifact does not modify Map V0.1 and does not admit any concept as a canonical HBI Need.

---

## 2. Method and semantic guardrails

For each concept:

**Concept → What is it? → Evidence / Provenance → Why HBI needs it? → HBI Role → HBI Classification → What it must NOT mean → Boundary → What is still missing? → Coverage / Capability Gap → Disposition**

The following distinctions are mandatory:

- Medical/scientific existence ≠ HBI Canonical Problem admission.
- HBI encounter relevance ≠ Canonical Problem admission.
- Presentation / descriptor ≠ diagnosis.
- Clinical condition ≠ Need.
- Recognition ≠ diagnosis.
- Recognition ≠ treatment.
- A manifestation or descriptor must not be silently promoted to its underlying condition.
- P46 may relate to S08, but that relationship does not authorize a Map rewrite or merge.
- Customer Reality = NOT VERIFIED.
- Customer Language = NOT VERIFIED.
- No treatment, diagnosis, referral protocol, safety rule, product mapping, recommendation logic, or implementation is produced.

---

# 3. Concept-by-concept execution

## P43 — Uneven skin texture

### What is it?
A broad presentation/descriptor referring to skin whose surface or tactile/visual texture is perceived as uneven. It is not, by itself, a single disease entity.

### Evidence / Provenance
**Source:** American Academy of Dermatology, “Microneedling can fade scars, uneven skin tone, and more.”

**Supported claim:** AAD explicitly lists “uneven skin texture and tone” among skin concerns addressed in dermatologic practice and discusses texture changes associated with scars and other conditions.

**Claim type:** Encounter/presentation terminology.

**What it proves:** The phrase is used as a recognizable skin concern/presentation in dermatology-facing material.

**What it does NOT prove:** It does not establish a unique disease, etiology, diagnosis, canonical HBI Problem, or customer-language term.

### Why HBI needs it?
A client may present with a texture complaint before an underlying cause is established. Retaining the presentation allows the Problem Bank to represent the observed concern without prematurely assigning a diagnosis.

### HBI Role
Presentation / discovery descriptor.

### HBI Classification
**PRESENTATION / DESCRIPTOR — not a diagnosis.**

### What it must NOT mean
- Not equivalent to hyperkeratosis.
- Not equivalent to keratosis pilaris.
- Not equivalent to scarring, acne, ageing, or any other cause.
- Not evidence of a treatment requirement.
- Not verified Customer Language.

### Boundary
The concept remains intentionally broad. Different underlying causes may produce an uneven-texture presentation. The working draft must not collapse those causes into P43.

### What is still missing?
- Direct HBI Customer Reality evidence.
- Verified Customer Language.
- Evidence defining whether P43 should ultimately remain a canonical Problem candidate or only a presentation-level intake descriptor.
- More precise coverage of common underlying causes if later needed.

### Coverage / Capability Gap
**Open:** the Map contains the presentation, but causal decomposition and HBI admission are not yet proven.

### Disposition
**RECLASSIFY** — from the raw Map label “Problem” to **Presentation / Descriptor** for Problem Bank V1 working semantics.

---

## P44 — Hyperkeratosis

### What is it?
A structural dermatologic descriptor describing thickening of the stratum corneum. DermNet defines hyperkeratosis as thickening of the stratum corneum; Cleveland Clinic describes hyperkeratosis as skin thickening associated with excess keratin and notes multiple forms and causes.

### Evidence / Provenance
**Source 1:** DermNet, “Glossary — Hyperkeratosis.”

**Supported claim:** Hyperkeratosis is thickening of the stratum corneum, the outermost layer of skin.

**Source 2:** DermNet, “Glossary of dermatopathological terms.”

**Supported claim:** Hyperkeratosis is thickening of the epidermis due to thickening of the stratum corneum.

**Source 3:** Cleveland Clinic, “Hyperkeratosis: What It Is, Types, Causes & Treatment.”

**Supported claim:** Hyperkeratosis can occur in multiple clinical settings and has multiple forms and causes.

**Claim type:** Clinical/structural terminology.

**What it proves:** P44 has a defined medical meaning as a structural descriptor/pattern.

**What it does NOT prove:** It does not identify one underlying disease, one customer need, or a unique HBI treatment pathway.

### Why HBI needs it?
The descriptor may be encountered when a client presents with rough, thickened, or scaly skin. Its value is primarily as a structured observation that can coexist with or point toward different underlying conditions.

### HBI Role
Structural / surface descriptor.

### HBI Classification
**DESCRIPTOR / STRUCTURAL FINDING — not a standalone diagnosis.**

### What it must NOT mean
- Not synonymous with keratosis pilaris.
- Not synonymous with seborrhoeic keratosis.
- Not equivalent to actinic keratosis or another specific condition.
- Not a standalone Need.
- Not a treatment instruction.

### Boundary
P44 describes a structural feature. The underlying cause remains open unless separately established.

### What is still missing?
- HBI Customer Reality and Customer Language.
- Evidence for whether this descriptor should ever be admitted as a canonical Problem rather than retained as an observation/descriptor.
- HBI-specific encounter frequency or decision utility.

### Coverage / Capability Gap
**Open:** P44 has strong medical existence evidence, but its HBI Problem-level role is not proven.

### Disposition
**RECLASSIFY** — from “Problem/condition” to **Structural / Clinical Descriptor** in the working draft.

---

## P45 — Keratosis pilaris

### What is it?
A recognized skin condition characterized by small rough-feeling bumps, commonly related to keratin accumulation and follicular plugging.

### Evidence / Provenance
**Source 1:** American Academy of Dermatology, “Keratosis pilaris: Overview.”

**Supported claim:** Keratosis pilaris is a common skin condition appearing as tiny, rough-feeling bumps; the bumps are associated with plugs of dead skin cells.

**Source 2:** DermNet, “Keratosis pilaris.”

**Supported claim:** Keratosis pilaris is a common dry skin condition caused by keratin accumulation in hair follicles; it is clinically diagnosed and has recognizable clinical features.

**Claim type:** Clinical condition / presentation.

**What it proves:** P45 is a medically recognized condition with a defined clinical presentation.

**What it does NOT prove:** Medical recognition alone does not establish canonical HBI Problem or Need admission.

### Why HBI needs it?
It can present as a concrete skin concern involving rough texture and bumps. Its identity is sufficiently distinct from generic P43 texture because the medical condition has a recognizable clinical definition.

### HBI Role
Condition / presentation candidate.

### HBI Classification
**CLINICAL CONDITION / PRESENTATION — canonical HBI status unproven.**

### What it must NOT mean
- Not simply “uneven texture.”
- Not a generic hyperkeratosis bucket.
- Not a customer diagnosis unless established by an authorized clinician.
- Not automatic eligibility for any particular treatment or product.

### Boundary
P45 should remain distinct from P43 and P44 in this working draft because the former is a named clinical condition while the latter are broader presentation/structural descriptors.

### What is still missing?
- Direct HBI Customer Reality.
- Verified Customer Language.
- Evidence that the condition has a distinct HBI consultation decision path.

### Coverage / Capability Gap
**Open:** clinical identity is supported; HBI canonical admission is not.

### Disposition
**KEEP** — retain as a distinct S07 concept candidate, without canonical Need admission.

---

## P46 — Seborrhoeic keratosis

### What is it?
A common benign epidermal growth/lesion characterized clinically by a sharply demarcated, often warty or “stuck-on” appearance. It can have a rough, waxy, or warty surface.

### Evidence / Provenance
**Source 1:** American Academy of Dermatology, “Seborrheic keratoses: Overview.”

**Supported claim:** Seborrheic keratosis is a common, non-cancerous skin growth that can have a warty surface.

**Source 2:** DermNet, “Seborrhoeic keratoses.”

**Supported claim:** Seborrhoeic keratoses may present as flat or raised papules/plaques with smooth, waxy, or warty surfaces and can resemble other lesions.

**Source 3:** DermNet, “Seborrhoeic keratosis pathology.”

**Supported claim:** Seborrhoeic keratosis is a benign acanthoma involving epidermal keratinocytes and may show hyperkeratosis.

**Claim type:** Benign lesion / clinical condition.

**What it proves:** P46 is a distinct recognized lesion/condition with a characteristic surface presentation.

**What it does NOT prove:** It does not prove that every rough or raised lesion is seborrhoeic keratosis, nor that P46 is a canonical HBI Need.

### Why HBI needs it?
A client may present with a visible or palpable growth whose surface resembles the broader texture concerns in S07. Distinguishing the lesion category from generic texture is important for correct semantic handling.

### HBI Role
Benign lesion / condition candidate; possible cross-shelf relation to lesion-focused S08.

### HBI Classification
**BENIGN LESION / CLINICAL CONDITION — canonical HBI status unproven.**

### What it must NOT mean
- Not equivalent to P43 uneven texture.
- Not equivalent to P44 hyperkeratosis, although hyperkeratosis can be part of its pathology.
- Not a blanket diagnosis for any “stuck-on” or rough growth.
- Not an automatic treatment or referral rule.

### Boundary and S07 ↔ S08 relation
P46 remains in S07 because its presentation has a surface-growth/texture dimension. Its lesion identity also creates a relationship to S08. This is a **RELATED / CROSS-SHELF relationship only** in this working draft.

No Map concept is moved, merged, renamed, or deleted.

### What is still missing?
- HBI Customer Reality and Customer Language.
- Evidence of the actual HBI decision path for this lesion.
- Formal management decision on how cross-shelf relationships should be represented in later Problem Bank/Need structures.

### Coverage / Capability Gap
**Open:** medical identity is well supported; HBI canonical role and final shelf semantics remain unproven.

### Disposition
**KEEP** — retain P46 as a distinct candidate and record S07↔S08 as a relationship only.

---

## P47 — Skin tags

### What is it?
Skin tags (acrochordons) are common benign growths composed of connective tissue and blood vessels with an epidermal covering. They commonly occur in skin folds and may be irritated by friction.

### Evidence / Provenance
**Source 1:** American Academy of Dermatology, “Skin tags: Why they develop, and how to remove them.”

**Supported claim:** Skin tags are harmless growths that commonly occur on areas such as the neck, eyelids, and underarms; irritation or discomfort can lead people to seek removal.

**Source 2:** DermNet, “Skin tags. Acrochordons.”

**Supported claim:** Skin tags are composed of loosely arranged collagen fibres and blood vessels surrounded by epidermis; several other lesions can resemble them.

**Claim type:** Benign lesion / presentation.

**What it proves:** P47 is a recognized benign lesion/presentation with a distinct clinical identity.

**What it does NOT prove:** It does not prove a canonical HBI Need, treatment eligibility, or a specific HBI action.

### Why HBI needs it?
It can be a concrete client-presenting skin growth, particularly where the client reports appearance, irritation, discomfort, or concern about a growth. The concept should remain semantically separate from generic texture.

### HBI Role
Benign lesion / presentation candidate.

### HBI Classification
**BENIGN LESION / CLINICAL PRESENTATION — canonical HBI status unproven.**

### What it must NOT mean
- Not equivalent to P43 uneven texture.
- Not equivalent to P46 seborrhoeic keratosis.
- Not proof that a lesion should be removed.
- Not authorization for procedural treatment.
- Not a referral rule.

### Boundary
The working draft records the lesion identity only. Any future treatment or referral decision is outside this execution.

### What is still missing?
- Direct HBI Customer Reality.
- Verified Customer Language.
- Evidence for the distinct HBI decision path and service boundary.

### Coverage / Capability Gap
**Open:** clinical existence is supported; HBI canonical admission and operational handling are not proven.

### Disposition
**KEEP** — retain as a distinct S07 candidate without Need or treatment admission.

---

# 4. Disposition table

| Concept | Working classification | Primary disposition | Key reason |
|---|---|---|---|
| P43 | Presentation / Descriptor | **RECLASSIFY** | Broad presentation; not a single condition |
| P44 | Structural / Clinical Descriptor | **RECLASSIFY** | Defined structural descriptor with multiple causes |
| P45 | Clinical Condition / Presentation | **KEEP** | Distinct recognized condition; HBI admission still unproven |
| P46 | Benign Lesion / Clinical Condition | **KEEP** | Distinct lesion; preserve S07↔S08 relation |
| P47 | Benign Lesion / Clinical Presentation | **KEEP** | Distinct recognized lesion; HBI admission still unproven |

**Exact disposition count:** KEEP = 3; RECLASSIFY = 2; MERGE = 0; PARK = 0; REMOVE = 0; TOTAL = 5.

**Important:** “KEEP” means retain the concept in this working draft. It does **not** mean Canonical Problem accepted, HBI Need accepted, Customer Reality verified, or Product/Recommendation eligibility established.

---

# 5. Boundary / semantic conclusions

### P43 vs P44
P43 is a broad surface presentation. P44 is a structural descriptor with a specific dermatologic meaning. They must not be merged merely because both can be associated with rough/uneven skin.

### P44 vs P45
Hyperkeratosis can occur as a feature in multiple conditions, while keratosis pilaris is a named clinical condition involving follicular keratin accumulation. P44 therefore must not become a synonym for P45.

### P45 vs P46/P47
P45 is a follicular clinical condition; P46 and P47 are benign lesion categories. Similar visible surface effects do not make them one concept.

### P46 and S08
P46 has a legitimate cross-shelf relationship with S08 because it is a lesion. The relationship is preserved as **RELATED / CROSS-SHELF**, without changing the frozen Map.

---

# 6. Coverage / Capability gaps

1. Customer Reality is not verified for any S07 concept.
2. Customer Language is not verified for any S07 concept.
3. HBI canonical Problem admission is not established by this artifact.
4. P43 remains intentionally broad and needs later evidence if a canonical Problem representation is desired.
5. P44 requires later governance on whether structural descriptors belong in a canonical Problem Bank or only in intake/observation vocabulary.
6. P45–P47 have stronger clinical identities, but distinct HBI decision utility has not yet been demonstrated.
7. P46↔S08 cross-shelf representation remains a governance/data-model question and is not solved here.
8. No treatment, diagnosis, referral, safety, or product capability is inferred from the evidence.

---

# 7. Self-critique

### Overclaim risk 1 — P43
The phrase “uneven skin texture” is clearly used in dermatology-facing material, but this does not establish that it is a formal disease entity. The draft therefore classifies it as a presentation/descriptor rather than a diagnosis.

### Overclaim risk 2 — P44
Medical existence is strong, but “hyperkeratosis” is a structural descriptor/pattern with multiple causes. Treating it as a single HBI Problem would create diagnosis/etiology creep.

### Overclaim risk 3 — P45
Clinical recognition does not prove HBI canonical admission. KEEP is deliberately weaker than acceptance.

### Overclaim risk 4 — P46
A benign label cannot be inferred from a generic rough or raised lesion. The draft does not create a referral rule, but future HBI handling must not confuse appearance with diagnosis.

### Overclaim risk 5 — P47
The fact that patients may want skin tags removed does not establish HBI procedural eligibility or a treatment path.

### Overclaim risk 6 — HBI relevance
The encounter rationales show why the concepts could matter in a dermatology/skin-care consultation context, but they are not Customer Reality evidence and do not establish actual HBI frequency.

### Overclaim risk 7 — S07↔S08
The P46 cross-shelf relationship is preserved conceptually only. No Map, schema, or data-model change is authorized by this artifact.

---

# 8. Governance state

- **S07 execution artifact:** CREATED
- **Artifact status:** WORKING DRAFT — NOT BASELINE
- **Map V0.1:** UNCHANGED / FROZEN
- **S01–S06 artifacts:** UNCHANGED
- **Customer Reality:** NOT VERIFIED
- **Customer Language:** NOT VERIFIED
- **Canonical Problem admission:** NOT ESTABLISHED
- **Need Extraction / Need Acceptance:** OUT OF SCOPE
- **Need → Product:** OUT OF SCOPE
- **Recommendation / Product Intelligence:** OUT OF SCOPE
- **Code / Schema / API / DB / UI:** UNCHANGED
- **Independent Verification:** PENDING
- **Management Acceptance:** PENDING
- **Management Baseline:** PENDING
- **PR Merge:** NOT AUTHORIZED
- **Implementation:** NOT AUTHORIZED

---

## 9. Source register

- American Academy of Dermatology — Keratosis pilaris overview: https://www.aad.org/public/diseases/a-z/keratosis-pilaris-overview
- American Academy of Dermatology — Keratosis pilaris symptoms: https://www.aad.org/public/diseases/a-z/keratosis-pilaris-symptoms
- American Academy of Dermatology — Seborrheic keratoses overview: https://www.aad.org/public/diseases/a-z/seborrheic-keratoses-overview
- American Academy of Dermatology — Skin tags: https://www.aad.org/public/diseases/a-z/skin-tags
- American Academy of Dermatology — Microneedling / uneven skin texture: https://www.aad.org/public/cosmetic/scars-stretch-marks/microneedling-fade-scars
- DermNet — Keratosis pilaris: https://dermnetnz.org/topics/keratosis-pilaris
- DermNet — Seborrhoeic keratoses: https://dermnetnz.org/topics/seborrhoeic-keratosis
- DermNet — Seborrhoeic keratosis pathology: https://dermnetnz.org/topics/seborrhoeic-keratosis-pathology
- DermNet — Skin tags / Acrochordons: https://dermnetnz.org/topics/skin-tag
- DermNet — Glossary of dermatopathological terms: https://dermnetnz.org/topics/dermatopathological-terminology
- Cleveland Clinic — Hyperkeratosis: https://my.clevelandclinic.org/health/diseases/hyperkeratosis

**Final execution boundary:** This document is an evidence-backed working draft only. It does not constitute verification, acceptance, baseline, diagnosis, treatment, referral policy, or implementation authorization.
