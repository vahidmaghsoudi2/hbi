# HBI Problem Bank V1 — S03 Corrected Working Draft

**Status:** WORKING DRAFT — NOT BASELINE  
**Scope:** S03 Breakout / Follicular / Pore Presentation  
**Concepts:** P08–P16  
**Customer Reality:** NOT VERIFIED  
**Customer Language:** NOT VERIFIED  
**S04:** NOT AUTHORIZED  
**Implementation:** NOT AUTHORIZED

## Correction Traceability

- C-S03-01 → P14
- C-S03-02 → P16
- C-S03-03 → P15
- C-S03-04 → P12
- C-S03-05 → P13
- C-S03-06 → P11 / P12

## Evidence Discipline

This working artifact separates medical/scientific identity from HBI relevance, HBI relevance from Customer Reality, Canonical Status from Disposition, subtype/presentation from severity, and sequela/aftermath from the original problem.

For each concept, provenance records the supported claim and its limits. Medical identity alone does not prove HBI relevance.

## Concept Register

### P08 — Acne
- **Concept Identity:** Acne; a clinical condition involving the pilosebaceous unit and characteristic acne lesions.
- **Evidence / Provenance:** AAD and DermNet sources used in S03 execution support acne as a skin condition and its characteristic lesion types.
- **HBI Relevance:** DIRECTLY_SUPPORTED
- **HBI Role:** PROBLEM / CLINICAL_ANCHOR
- **Canonical Status:** CANONICAL_PROBLEM_SUPPORTED
- **Boundary:** Acne is not equivalent to oily skin, folliculitis, or post-acne sequelae.
- **Related / Overlap:** P09, P10, P11, P12; P14 and P15 are distinct acne-like/follicular presentations.
- **Coverage / Capability Gap:** G-S03-01 Acne Lesion Hierarchy; G-S03-02 Acne vs Acne Mimics.
- **Disposition:** KEEP
- **Correction Status:** UNCHANGED BY C-S03 CORRECTIONS

### P09 — Open Comedone / Blackhead
- **Concept Identity:** Open comedone (blackhead), an acne lesion.
- **Evidence / Provenance:** AAD and DermNet support open comedones as acne lesions.
- **HBI Relevance:** DIRECTLY_SUPPORTED
- **HBI Role:** MANIFESTATION / SUBTYPE
- **Canonical Status:** MANIFESTATION
- **Boundary:** Not an independent canonical Problem merely because it is a familiar presentation.
- **Related / Overlap:** P08, P10, P11.
- **Coverage / Capability Gap:** G-S03-01.
- **Disposition:** KEEP
- **Correction Status:** UNCHANGED BY C-S03 CORRECTIONS

### P10 — Closed Comedone / Whitehead
- **Concept Identity:** Closed comedone (whitehead), an acne lesion.
- **Evidence / Provenance:** AAD and DermNet support closed comedones as acne lesions.
- **HBI Relevance:** DIRECTLY_SUPPORTED
- **HBI Role:** MANIFESTATION / SUBTYPE
- **Canonical Status:** MANIFESTATION
- **Boundary:** Not an independent canonical Problem merely because it is a familiar presentation.
- **Related / Overlap:** P08, P09, P11.
- **Coverage / Capability Gap:** G-S03-01.
- **Disposition:** KEEP
- **Correction Status:** UNCHANGED BY C-S03 CORRECTIONS

### P11 — Inflammatory Acne Lesions
- **Concept Identity:** Inflammatory acne lesions / inflammatory lesion presentation within acne.
- **Evidence / Provenance:** AAD and DermNet support inflammatory acne lesion types within acne.
- **HBI Relevance:** DIRECTLY_SUPPORTED
- **HBI Role:** MANIFESTATION
- **Canonical Status:** MANIFESTATION
- **Boundary:** Does not establish a separate canonical Problem or a severity classification by itself.
- **Related / Overlap:** P08; **P11 ↔ P12 = RELATED / OVERLAPPING. No fixed parent-child hierarchy is asserted.**
- **Coverage / Capability Gap:** G-S03-01; G-S03-04 Severity vs Subtype.
- **Disposition:** KEEP
- **Correction Status:** C-S03-06 APPLIED

### P12 — Nodular / Cystic Acne
- **Concept Identity:** Nodular / cystic acne presentation within acne.
- **Evidence / Provenance:** AAD and DermNet support nodules/cystic or deep acne lesion presentations within acne.
- **HBI Relevance:** DIRECTLY_SUPPORTED
- **HBI Role:** SUBTYPE / PRESENTATION
- **Canonical Status:** SUBTYPE
- **Boundary:** **Subtype / presentation is not severity classification. Nodular/cystic does not equal Severe, and does not automatically prove severity.**
- **Severity Classification:** OPEN
- **Related / Overlap:** **P11 ↔ P12 = RELATED / OVERLAPPING. No fixed parent-child hierarchy is asserted.**
- **Coverage / Capability Gap:** G-S03-04 Severity vs Subtype — OPEN.
- **Disposition:** KEEP
- **Correction Status:** C-S03-04 and C-S03-06 APPLIED

### P13 — Acne Aftermath / Discoloration
- **Concept Identity:** Acne aftermath / post-acne changes, including potentially distinct post-inflammatory pigmentation, erythema, hypopigmentation, and acne scarring.
- **Evidence / Provenance:** AAD and DermNet support post-acne discoloration/sequelae and distinguish flat discoloration from true acne scarring.
- **HBI Relevance:** DIRECTLY_SUPPORTED
- **HBI Role:** SEQUELA / AFTERMATH
- **Canonical Status:** WORKING CLASSIFICATION ONLY
- **Boundary:** P13 is not treated as one finalized canonical Problem. Its umbrella may contain materially distinct concepts.
- **Canonical Decomposition:** OPEN. No final decomposition is established in this artifact.
- **Related / Overlap:** **P13 ↔ S04 = RELATIONSHIP ONLY. This artifact does not reopen or rewrite S04.**
- **Coverage / Capability Gap:** G-S03-03 Aftermath Decomposition — OPEN.
- **Disposition:** RECLASSIFY / KEEP AS WORKING CONCEPT
- **Correction Status:** C-S03-05 APPLIED

### P14 — Folliculitis
- **Concept Identity:** Folliculitis; a follicular inflammatory/clinical presentation that can resemble acne.
- **Evidence / Provenance:** AAD and DermNet support folliculitis as distinct from acne and capable of acne-like appearance.
- **HBI Relevance:** NOT_PROVEN / UNKNOWN
- **HBI Role:** CLINICAL_ANCHOR / PRESENTATION
- **Canonical Status:** CANONICAL_PROBLEM_NOT_PROVEN
- **Boundary:** Medical identity does not by itself establish HBI relevance, Customer Reality, or canonical Problem admission. P14 is not equated with acne.
- **Related / Overlap:** P08; P15 is related but distinct.
- **Coverage / Capability Gap:** G-S03-02 Acne vs Acne Mimics — OPEN; HBI operational relevance — UNKNOWN.
- **Disposition:** KEEP
- **Correction Status:** C-S03-01 APPLIED

### P15 — Pseudofolliculitis / Razor Bumps
- **Concept Identity:** Pseudofolliculitis / razor-bump presentation associated with ingrown hairs and shaving-related follicular inflammation.
- **Evidence / Provenance:** DermNet supports pseudofolliculitis barbae as a distinct inflammatory follicular presentation associated with ingrown hairs/shaving and capable of acne-like appearance.
- **HBI Relevance:** INDIRECTLY_SUPPORTED
- **HBI Role:** PROBLEM / PRESENTATION / CLINICAL_ANCHOR
- **Canonical Status:** CANONICAL_PROBLEM_NOT_PROVEN
- **Boundary:** Not equated with acne or ordinary oily skin; contextual association with shaving does not itself establish Customer Reality.
- **Related / Overlap:** P08 and P14; strong contextual relation to shaving/ingrown hair.
- **Coverage / Capability Gap:** G-S03-02 Acne vs Acne Mimics — OPEN; HBI operational relevance remains indirect.
- **Disposition:** KEEP
- **Correction Status:** C-S03-03 APPLIED

### P16 — Sebaceous Hyperplasia
- **Concept Identity:** Sebaceous hyperplasia; benign enlargement of sebaceous glands presenting as papules and potentially confused visually with other lesions.
- **Evidence / Provenance:** DermNet supports sebaceous hyperplasia as a benign sebaceous-gland lesion and notes possible visual confusion with basal cell carcinoma.
- **HBI Relevance:** NOT_PROVEN
- **HBI Role:** CLINICAL_ANCHOR / PRESENTATION
- **Canonical Status:** CLINICAL_ANCHOR
- **Boundary:** Medical identity / clinical recognizability does not by itself prove HBI relevance or canonical Problem admission. It is not equated with oily skin or acne.
- **Related / Overlap:** P08 and P03 by sebaceous context, but not identity.
- **Coverage / Capability Gap:** HBI operational relevance — UNKNOWN; G-S03-05 Clinical Anchor vs Canonical Problem — OPEN.
- **Disposition:** KEEP
- **Correction Status:** C-S03-02 APPLIED

## Residual Open Boundaries

1. Clinical Anchor vs Canonical Problem remains an open HBI classification question where not independently supported.
2. Acne lesion hierarchy and acne-vs-mimic distinctions remain capability gaps; this artifact does not create a new hierarchy.
3. P13 aftermath decomposition remains open.
4. Severity classification remains open; no subtype-to-severity inference is authorized.
5. Customer Reality and Customer Language remain NOT VERIFIED.
6. No safety/referral rule is created by this artifact.

## Governance

This is a corrected Working Artifact, not a baseline acceptance.

No S04 execution, Map reopening, methodology redesign, Need extraction/acceptance, Product mapping, Recommendation/Scoring changes, schema/API/DB/UI work, treatment logic, diagnosis logic, or implementation authorization is created by this artifact.
