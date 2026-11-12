# HBI Problem Bank V1 — S06 Working Draft

**S06 WORKING DRAFT — NOT BASELINE**

**Scope:** S06 — Infection / Infestation  
**Map Source:** Skin Problem Space Map V0.1 — ACCEPTED / FROZEN  
**Map Entries:** P34–P42 only  
**Customer Reality:** NOT VERIFIED  
**Customer Language:** NOT VERIFIED  
**Implementation:** NOT AUTHORIZED  
**Need Extraction:** OUT OF SCOPE  
**Need Acceptance:** OUT OF SCOPE  
**Product Mapping:** OUT OF SCOPE  
**Recommendation:** OUT OF SCOPE  

## Execution Boundary

This artifact executes only the nine pre-existing S06 entries from the frozen Map V0.1:

- P34 Dermatophytosis / fungal skin infection
- P35 Tinea / Ringworm
- P36 Bacterial skin infection
- P37 Viral skin infection
- P38 Herpes simplex
- P39 Warts
- P40 Impetigo
- P41 Scabies
- P42 Shingles

No new Map concept is introduced. Map V0.1 is not modified or reopened. S01–S05 are not modified.

S06 is an organizational/observational shelf. Presence in S06 does not imply Ordinary Care suitability, Canonical Problem admission, diagnosis, treatment eligibility, or referral authorization.

## Evidence Discipline

Evidence is recorded at claim level:

**Source → Exact Supported Claim → Claim Type → What it proves → What it does NOT prove**

Medical/scientific evidence establishes clinical identity or presentation only. It does not by itself establish HBI canonical Problem admission, Customer Reality, Customer Language, Need acceptance, treatment eligibility, product suitability, or recommendation eligibility.

Customer Reality and Customer Language are intentionally not inferred from medical sources, prevalence, or terminology.

## Concept Register

### P34 — Dermatophytosis / fungal skin infection

- **Problem ID:** P34
- **Canonical / Working Name:** Dermatophytosis / fungal skin infection
- **Concept Identity:** A fungal skin infection caused by dermatophytes; DermNet identifies tinea as dermatophyte infection and uses dermatophytosis as a synonym.
- **Evidence / Provenance:**
  - DermNet, “Tinea (fungal skin infection)” identifies tinea as a skin infection with a dermatophyte fungus and lists dermatophytosis as a synonym.
    - **Claim Type:** Clinical/scientific identity.
    - **Proves:** Dermatophytosis/tinea is a recognized fungal infection category.
    - **Does NOT prove:** HBI canonical Problem admission, Customer Reality, or treatment/recommendation eligibility.
- **HBI Relevance:** DIRECTLY_SUPPORTED
  - **Basis:** An infectious skin presentation must be recognizable in consultation so it is not silently treated as an ordinary non-infectious skin-care problem.
  - **Boundary of HBI claim:** This is consultation-recognition relevance, not a diagnosis or treatment rule.
- **HBI Role:** CLINICAL CONDITION / INFECTION ANCHOR
- **Canonical Status:** CANONICAL_PROBLEM_NOT_PROVEN
- **What it must NOT mean:** Recognition of the concept does not establish that a customer has a fungal infection.
- **Boundary:** Dermatophytosis is the broader dermatophyte-infection concept represented here; specific anatomic tinea forms are not separately introduced by this execution.
- **Related / Overlap:** P35 Tinea / Ringworm.
- **Coverage / Capability Gap:** Infection-vs-non-infection recognition; distinction between broad fungal infection concept and specific clinical subtype.
- **Disposition:** KEEP
- **Execution Status:** COMPLETED — WORKING DRAFT ONLY

### P35 — Tinea / Ringworm

- **Problem ID:** P35
- **Canonical / Working Name:** Tinea / Ringworm
- **Concept Identity:** DermNet states that “tinea” refers to a skin infection with a dermatophyte fungus and lists dermatophytosis as a synonym.
- **Evidence / Provenance:**
  - DermNet, “Tinea (fungal skin infection)” supports the identity and synonym relationship between tinea and dermatophytosis.
    - **Claim Type:** Clinical/scientific identity and terminology.
    - **Proves:** P35 substantially overlaps with P34 at the concept level.
    - **Does NOT prove:** HBI canonical admission or Customer Reality.
- **HBI Relevance:** INHERITED_FROM_P34
  - **Basis:** The consultation-recognition rationale is the same as P34.
- **HBI Role:** CLINICAL CONDITION / TERMINOLOGY VARIANT
- **Canonical Status:** MERGE / RELATED TO P34
- **What it must NOT mean:** Ringworm is not a separate HBI Need merely because it is a familiar label.
- **Boundary:** Tinea is not a synonym for every fungal skin infection; the Map concept is specifically the dermatophyte/tinea family represented by P34.
- **Related / Overlap:** P34 Dermatophytosis.
- **Coverage / Capability Gap:** Terminology normalization and avoidance of duplicate condition entries.
- **Disposition:** MERGE → P34
- **Execution Status:** COMPLETED — WORKING DRAFT ONLY

### P36 — Bacterial skin infection

- **Problem ID:** P36
- **Canonical / Working Name:** Bacterial skin infection
- **Concept Identity:** DermNet describes bacterial skin infections as infections caused by bacteria that may invade normal skin or affect compromised skin barriers, with multiple clinical forms.
- **Evidence / Provenance:**
  - DermNet, “Bacterial skin infections” supports bacterial skin infection as a recognized category and gives multiple examples.
    - **Claim Type:** Clinical/scientific identity and category.
    - **Proves:** Bacterial skin infection is a distinct infection family with multiple presentations.
    - **Does NOT prove:** HBI canonical Problem admission or suitability for ordinary care.
- **HBI Relevance:** DIRECTLY_SUPPORTED
  - **Basis:** Recognition of an infectious category is relevant to consultation because infection must not be silently collapsed into a generic skin-care presentation.
- **HBI Role:** CLINICAL FAMILY / INFECTION ANCHOR
- **Canonical Status:** CANONICAL_PROBLEM_NOT_PROVEN
- **What it must NOT mean:** The category does not establish a diagnosis or identify the causative organism in an individual.
- **Boundary:** P40 Impetigo is a specific bacterial infection and remains a related child/clinical example rather than an automatic duplicate.
- **Related / Overlap:** P40 Impetigo; broader skin-infection domain.
- **Coverage / Capability Gap:** Broad bacterial-family recognition vs specific bacterial conditions; severity/context boundary.
- **Disposition:** KEEP
- **Execution Status:** COMPLETED — WORKING DRAFT ONLY

### P37 — Viral skin infection

- **Problem ID:** P37
- **Canonical / Working Name:** Viral skin infection
- **Concept Identity:** DermNet identifies multiple localized skin and mucosal conditions caused by viruses, including herpes simplex, herpes zoster, and viral warts.
- **Evidence / Provenance:**
  - DermNet, “Viral skin infections” lists herpes simplex, herpes zoster, and viral warts among localized viral skin/mucosal conditions.
    - **Claim Type:** Clinical/scientific category.
    - **Proves:** Viral skin infection is a recognized broad clinical family containing distinct conditions.
    - **Does NOT prove:** HBI canonical Problem admission or individual diagnosis.
- **HBI Relevance:** DIRECTLY_SUPPORTED
  - **Basis:** The broad category is relevant to consultation recognition because infectious presentations can require a different handling path from ordinary skin-care concerns.
- **HBI Role:** CLINICAL FAMILY / INFECTION ANCHOR
- **Canonical Status:** CANONICAL_PROBLEM_NOT_PROVEN
- **What it must NOT mean:** A viral-family label cannot be used as a diagnosis for an individual presentation.
- **Boundary:** P38, P39, and P42 are distinct named conditions within/related to the viral infection family.
- **Related / Overlap:** P38 Herpes simplex; P39 Warts; P42 Shingles.
- **Coverage / Capability Gap:** Broad viral-family recognition vs named-condition recognition.
- **Disposition:** KEEP
- **Execution Status:** COMPLETED — WORKING DRAFT ONLY

### P38 — Herpes simplex

- **Problem ID:** P38
- **Canonical / Working Name:** Herpes simplex
- **Concept Identity:** DermNet describes herpes simplex virus infections as affecting mucocutaneous sites and recurring with characteristic grouped vesicles.
- **Evidence / Provenance:**
  - DermNet, “Herpes simplex” supports herpes simplex as a recognized viral infection with characteristic mucocutaneous manifestations.
    - **Claim Type:** Clinical/scientific identity.
    - **Proves:** Herpes simplex is a distinct clinical infection.
    - **Does NOT prove:** HBI canonical admission, individual diagnosis, or treatment eligibility.
- **HBI Relevance:** DIRECTLY_SUPPORTED
  - **Basis:** A named infectious condition may need to be recognized during consultation so it is not silently treated as generic redness, irritation, or another ordinary skin concern.
- **HBI Role:** CLINICAL CONDITION / CLINICAL ANCHOR
- **Canonical Status:** CANONICAL_PROBLEM_NOT_PROVEN
- **What it must NOT mean:** The artifact does not diagnose herpes simplex from appearance alone.
- **Boundary:** Herpes simplex ≠ herpes zoster/shingles; vesicular presentations can have differential diagnoses.
- **Related / Overlap:** P37 Viral skin infection; P42 Shingles.
- **Coverage / Capability Gap:** Viral vesicular presentation vs named-condition recognition; diagnostic boundary.
- **Disposition:** KEEP
- **Execution Status:** COMPLETED — WORKING DRAFT ONLY

### P39 — Warts

- **Problem ID:** P39
- **Canonical / Working Name:** Warts
- **Concept Identity:** DermNet describes viral warts as benign proliferations of skin and mucosa caused by human papillomavirus.
- **Evidence / Provenance:**
  - DermNet, “Viral warts” supports warts as HPV-related viral proliferations with characteristic verrucous/hyperkeratotic papules.
    - **Claim Type:** Clinical/scientific identity.
    - **Proves:** Warts are a recognized viral skin condition.
    - **Does NOT prove:** HBI canonical Problem admission or individual diagnosis.
- **HBI Relevance:** DIRECTLY_SUPPORTED
  - **Basis:** A recognizable infectious/viral lesion category should not automatically be treated as an ordinary texture or cosmetic concern.
- **HBI Role:** CLINICAL CONDITION / LESION ANCHOR
- **Canonical Status:** CANONICAL_PROBLEM_NOT_PROVEN
- **What it must NOT mean:** A verrucous or hyperkeratotic lesion is not automatically a wart without appropriate assessment.
- **Boundary:** Warts can resemble other lesions; recognition does not authorize a treatment or removal protocol.
- **Related / Overlap:** P37 Viral skin infection; S07/S08 lesion and surface concepts.
- **Coverage / Capability Gap:** Wart-vs-other-lesion boundary; infection-vs-benign-appearance distinction.
- **Disposition:** KEEP
- **Execution Status:** COMPLETED — WORKING DRAFT ONLY

### P40 — Impetigo

- **Problem ID:** P40
- **Canonical / Working Name:** Impetigo
- **Concept Identity:** DermNet describes impetigo as a common, superficial, highly contagious bacterial skin infection characterized by pustules and honey-coloured crusted erosions.
- **Evidence / Provenance:**
  - DermNet, “Impetigo” supports the clinical identity and contagious superficial bacterial nature of impetigo.
    - **Claim Type:** Clinical/scientific identity.
    - **Proves:** Impetigo is a distinct bacterial skin infection.
    - **Does NOT prove:** HBI canonical admission, individual diagnosis, or treatment eligibility.
- **HBI Relevance:** DIRECTLY_SUPPORTED
  - **Basis:** Its infectious and contagious nature makes recognition relevant to consultation so it is not silently handled as an ordinary non-infectious skin-care presentation.
- **HBI Role:** CLINICAL CONDITION / INFECTION ANCHOR
- **Canonical Status:** CANONICAL_PROBLEM_NOT_PROVEN
- **What it must NOT mean:** The artifact does not establish an individual diagnosis or prescribe infection management.
- **Boundary:** Impetigo is a specific bacterial infection and is related to, but not identical with, the broader P36 bacterial skin infection family.
- **Related / Overlap:** P36 Bacterial skin infection.
- **Coverage / Capability Gap:** Broad-family vs specific-condition boundary; contagious infection recognition.
- **Disposition:** KEEP
- **Execution Status:** COMPLETED — WORKING DRAFT ONLY

### P41 — Scabies

- **Problem ID:** P41
- **Canonical / Working Name:** Scabies
- **Concept Identity:** DermNet describes scabies as a transmissible human skin infestation caused by the mite Sarcoptes scabiei var. hominis.
- **Evidence / Provenance:**
  - DermNet, “Scabies” supports scabies as a contagious infestation and distinguishes it from dermatitis and other differentials.
    - **Claim Type:** Clinical/scientific identity.
    - **Proves:** Scabies is a distinct infestation requiring recognition as such.
    - **Does NOT prove:** HBI canonical admission, individual diagnosis, or treatment eligibility.
- **HBI Relevance:** DIRECTLY_SUPPORTED
  - **Basis:** An infestation is materially different from an ordinary cosmetic/skin-care presentation and therefore must be recognizable in consultation without being silently collapsed into eczema, rash, or itch.
- **HBI Role:** INFESTATION / CLINICAL ANCHOR
- **Canonical Status:** CANONICAL_PROBLEM_NOT_PROVEN
- **What it must NOT mean:** Recognition of scabies as a concept is not diagnosis-by-rule.
- **Boundary:** Scabies ≠ eczema/dermatitis ≠ generic rash; differential diagnosis remains clinical.
- **Related / Overlap:** P33 Unspecified rash; S05 inflammatory/rash concepts.
- **Coverage / Capability Gap:** Infestation-vs-inflammatory presentation; contact/context recognition.
- **Disposition:** KEEP
- **Execution Status:** COMPLETED — WORKING DRAFT ONLY

### P42 — Shingles

- **Problem ID:** P42
- **Canonical / Working Name:** Shingles / Herpes zoster
- **Concept Identity:** DermNet describes herpes zoster as a painful blistering rash caused by reactivation of varicella-zoster virus.
- **Evidence / Provenance:**
  - DermNet, “Herpes zoster” supports shingles/herpes zoster as a distinct viral infection with characteristic painful blistering rash.
    - **Claim Type:** Clinical/scientific identity.
    - **Proves:** Shingles is a distinct viral condition.
    - **Does NOT prove:** HBI canonical admission, individual diagnosis, or treatment eligibility.
- **HBI Relevance:** DIRECTLY_SUPPORTED
  - **Basis:** A potentially clinically significant infectious presentation must be recognizable in consultation and not silently treated as an ordinary rash or irritation.
- **HBI Role:** CLINICAL CONDITION / CLINICAL ANCHOR
- **Canonical Status:** CANONICAL_PROBLEM_NOT_PROVEN
- **What it must NOT mean:** The artifact does not establish an individual diagnosis or create a treatment/referral rule.
- **Boundary:** Shingles ≠ herpes simplex; pain, distribution, timing, and other clinical features matter to actual diagnosis.
- **Related / Overlap:** P37 Viral skin infection; P38 Herpes simplex; P33 Unspecified rash.
- **Coverage / Capability Gap:** Viral vesicular/rash recognition; distinction between named viral conditions.
- **Disposition:** KEEP
- **Execution Status:** COMPLETED — WORKING DRAFT ONLY

## Disposition Summary

| Disposition | Count |
|---|---:|
| KEEP | 8 |
| MERGE | 1 |
| RECLASSIFY | 0 |
| PARK | 0 |
| REMOVE | 0 |
| **TOTAL** | **9** |

The single merge is:

**P35 Tinea / Ringworm → P34 Dermatophytosis**

No concept was removed from the Map. The merge is a working-draft deduplication of terminology, not a change to the frozen Map.

## Cross-S06 Boundaries

- Infection / Infestation ≠ ordinary skin-care Need.
- Clinical condition ≠ accepted HBI Need.
- Medical existence ≠ HBI canonical admission.
- HBI relevance ≠ diagnosis.
- Recognition of a named infection ≠ diagnosis of that infection in an individual.
- P34/P35 terminology overlap does not authorize removal or modification of the frozen Map entry.
- P36/P40 and P37/P38/P39/P42 represent broad-family versus named-condition relationships; these are not being converted into a fixed medical taxonomy.
- No referral protocol or treatment rule is created by this artifact.

## Coverage / Capability Gaps

Recorded as gaps, not implementation requirements:

- Infection vs ordinary skin-care presentation.
- Broad infection family vs named clinical condition.
- Dermatophyte terminology and subtype boundary.
- Viral condition differentiation.
- Bacterial family vs specific condition boundary.
- Infestation vs inflammatory/rash presentation.
- Infectious presentation vs Safety/Referral operational rules.
- Customer Reality for infection/infestation presentations.
- Customer Language for infection/infestation presentations.
- HBI canonical Problem admission for S06 concepts.

## Self-Critique

1. **Highest overclaim risk:** treating strong clinical identity plus HBI consultation relevance as Canonical Problem admission. This has deliberately not been done.
2. **P34/P35 risk:** tinea and dermatophytosis are treated as a terminology/concept overlap based on DermNet; this does not modify the frozen Map.
3. **Broad-family risk:** P36 and P37 are broad clinical families. They are retained for coverage and recognition, not asserted as final canonical Problems.
4. **Safety risk:** infectious/infestation recognition is not converted into referral or treatment rules.
5. **Customer evidence risk:** no Customer Reality or Customer Language is inferred.
6. **Scope risk:** no concept outside P34–P42 has been introduced.

## Governance State

```
S06 Scope = P34–P42 — CONFIRMED FROM FROZEN MAP V0.1
S06 Execution = COMPLETED AS WORKING DRAFT
S06 Verification = NOT YET
S06 Accepted = NOT YET
S06 Baseline = NOT YET
S06 Merge = NOT AUTHORIZED
S06 Implementation = NOT AUTHORIZED

Map V0.1 = ACCEPTED / FROZEN
Customer Reality = NOT VERIFIED
Customer Language = NOT VERIFIED
Need Extraction = OUT OF SCOPE
Need Acceptance = OUT OF SCOPE
Product Mapping = OUT OF SCOPE
Recommendation = OUT OF SCOPE
Schema / API / DB / UI = NOT AUTHORIZED
```

This artifact records execution only. Independent verification and Management Baseline are separate later gates.
