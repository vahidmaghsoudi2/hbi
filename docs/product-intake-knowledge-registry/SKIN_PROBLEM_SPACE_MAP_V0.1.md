> ⚠️ **STATUS NOTICE — DRAFT / NOT THE ACTIVE PROBLEM BANK**
>
> This file is a structural draft only. It is **not** the accepted refined list, a medically approved Problem Bank, a canonical Need Bank, or authorization to recommend products. Do not start new work from this file or treat its contents as accepted. Use the [Skin Problem Bank Consolidated Reference](./SKIN_PROBLEM_BANK_CONSOLIDATED_REFERENCE.md) for the current status and entry points, and the [Source Retirement Register](./PRODUCT_INTAKE_SOURCE_RETIREMENT_REGISTER.md) for source authority and disposition. Preserve this draft for traceability; do not copy it into active working packets as an accepted list.

---

> Team entry point: [Skin Problem Bank Workspace Index](./SKIN_PROBLEM_BANK_WORKSPACE_INDEX.md). This map remains a structural draft only.

# HBI — SKIN PROBLEM SPACE MAP V0.1
## Official Red-Team Input Artifact

**Mission:** Skin Problem Space Mapping  
**Scope:** SKIN  
**Status:** DRAFT / V0.1  
**Purpose:** Structural mapping of existing P01–P61 discovery stock  
**Not included:** Problem Bank V1, Need Extraction, Need Acceptance, Product, Recommendation, Implementation

## 1. Problem Unit Definition

A Problem Unit is an encounter-relevant skin issue, condition, manifestation, or contextual problem that can be represented with a distinct and defensible boundary inside the Skin Problem Space.

It must have:
- definable meaning;
- distinguishable boundary from neighboring units;
- defensible location within the Problem Space;
- sufficient evidence or explicit UNKNOWN/GAP;
- no requirement to already qualify as an HBI Need.

Semantic boundaries:
Problem ≠ Symptom/Manifestation ≠ Clinical Condition ≠ Safety/Referral Signal ≠ Context ≠ Need.

A Symptom/Manifestation may nevertheless be a legitimate Problem Unit when it represents a meaningful presenting problem.

Symptom alone ≠ Accepted Need.  
Clinical Condition ≠ automatically Need.  
Safety Signal ≠ Ordinary Care Need.

## 2. Lightweight Skin Problem Space

Shelves are organizational/observational, not a disease taxonomy.

S01 — Barrier / Hydration / Surface  
Hydration, dryness, surface integrity, sensitivity and barrier-related presentation. Boundary: does not automatically imply diagnosis.

S02 — Oil / Sebum / Follicular Balance  
Oiliness, sebum and related follicular characteristics. Combination skin is not automatically an independent Problem.

S03 — Acne / Follicular / Pore Presentation  
Acne-related and follicular presentations, including comedonal and inflammatory patterns. Individual lesion forms may be manifestations/severity characteristics.

S04 — Pigmentation / Color  
Altered coloration, hyperpigmentation, hypopigmentation and pigmentation presentation. Melasma/vitiligo remain Clinical Conditions, not automatically Needs.

S05 — Redness / Inflammation / Rash  
Redness, flushing, rash and inflammatory presentations. Presenting manifestations and Clinical Conditions remain distinct.

S06 — Infection / Infestation  
Infectious/infestation-related presentations. Presence here does not imply Ordinary Care suitability.

S07 — Texture / Keratinization / Surface Growth  
Texture abnormalities, keratinization and selected benign surface growths. Diagnostic lesions are not converted into Ordinary Care Needs.

S08 — Lesions / Growths / Change  
Moles, new/growing lesions and lesion-related presentations. Suspicion/change may be Safety/Referral rather than Ordinary Care.

S09 — Sun / UV-Related Change  
UV exposure, chronic UV-related change and associated findings. Context is not automatically Need/diagnosis.

S10 — Systemic / Autoimmune / Clinically Significant Skin Presentation  
Systemic, autoimmune, autoinflammatory and clinically significant skin manifestations. Inclusion does not authorize treatment or Ordinary Care handling.

## 3. Structural Model

Primary relationship:

SHELF → Problem / Presentation → Clinical Condition → Clinical Anchor

Parallel relations:
Problem / Presentation → Safety / Referral Signal  
Problem / Presentation → Context / Descriptor

Later only:
Problem → Potential HBI Need

The final arrow is NOT evaluated in V0.1.

## 4. P01–P61 Mapping

### S01
P01 Dry skin/Xerosis — Problem/Clinical presentation — S01 — Mapped  
P02 Dehydration/impaired moisture retention — Manifestation/related presentation — P01 — MERGE/RELATED TO P01  
P05 Sensitive skin — Problem/presentation — S01 — Mapped  
P06 Irritant dermatitis — Clinical Condition/inflammatory presentation — S01→S05 — Clinical Anchor  
P07 Fissuring/cracking — Manifestation — P01/S01 — Manifestation, not separate Need

### S02
P03 Oily skin/Seborrhoea — Problem/presentation — S02 — Mapped  
P04 Combination skin — State Descriptor — S02 — Descriptor, not independent Problem

### S03
P08 Acne — Problem/Clinical presentation — S03 — Mapped  
P09 Blackheads/open comedones — Manifestation/subtype — P08 — Child/Related  
P10 Whiteheads/closed comedones — Manifestation/subtype — P08 — Child/Related  
P11 Inflammatory acne lesions — Manifestation/subtype — P08 — Child/Related  
P12 Nodular/cystic acne — Severity/clinical subtype — P08 — Clinical/Severity Anchor  
P13 Acne aftermath/discoloration — Sequela/post-inflammatory presentation — P08→S04 — Related/Cross-Shelf  
P14 Folliculitis — Clinical Condition/follicular presentation — S03 — Clinical Anchor/HBI relevance unresolved  
P15 Pseudofolliculitis/razor bumps — Problem/follicular presentation — S03 — Mapped  
P16 Sebaceous hyperplasia — Clinical Condition/lesion presentation — S02→S07 — Clinical Anchor/HBI relevance unresolved

### S04
P17 Hyperpigmentation/dark spots — Problem/presentation — S04 — Mapped  
P18 Melasma — Clinical Condition — P17/S04 — Clinical Anchor  
P19 Post-inflammatory hyperpigmentation — Sequela/pigmentation presentation — P17/S04 — Related  
P20 Hypopigmentation — Problem/presentation — S04 — Mapped; evidence boundary retained  
P21 Vitiligo — Clinical Condition — S04 — Clinical/Referral-sensitive  
P22 Sun-related pigmentation — Context/pigmentation presentation — P17/S09 — Related/Context  
P23 Poikiloderma — Clinical Condition/UV-associated presentation — S04↔S09 — Parked/Evidence Boundary

### S05
P24 Persistent redness — Problem/presentation — S05 — Mapped  
P25 Flushing — Symptom/manifestation — P24/S05 — Related/Signal  
P26 Rosacea — Clinical Condition — P24/S05 — Clinical Anchor  
P27 Eczema/Dermatitis — Clinical Condition/presentation — S05 — Clinical Anchor  
P28 Atopic dermatitis — Clinical Condition — P27/S05 — Clinical Anchor  
P29 Allergic contact dermatitis — Clinical Condition — P27/S05 — Clinical Anchor  
P30 Seborrhoeic dermatitis — Clinical Condition — S05↔S02 — Clinical Anchor  
P31 Psoriasis — Clinical Condition — S05 — Clinical/Referral-sensitive  
P32 Hives/Urticaria — Clinical Condition/acute presentation — S05 — Safety/Referral-sensitive  
P33 Unspecified rash — Presenting Problem/unresolved manifestation — S05 — Mapped

### S06
P34 Dermatophytosis/fungal infection — Clinical Condition — S06 — Clinical/Safety-sensitive  
P35 Tinea/ringworm — Clinical subtype/manifestation — P34 — Child/Related  
P36 Bacterial skin infection — Clinical Condition — S06 — Clinical/Safety-sensitive  
P37 Viral skin infection — Clinical Condition — S06 — Clinical/Safety-sensitive  
P38 Cutaneous herpes simplex — Clinical Condition — P37 — Clinical/Safety-sensitive  
P39 Warts — Clinical Condition/lesion presentation — S06↔S08 — Clinical Anchor  
P40 Impetigo — Clinical Condition — P36/S06 — Clinical/Safety-sensitive  
P41 Scabies — Clinical Condition/infestation — S06 — Clinical/Safety-sensitive  
P42 Shingles — Clinical Condition — S06 — Clinical/Referral-sensitive

### S07
P43 Uneven skin texture — Problem/presentation — S07 — Mapped; boundary open  
P44 Hyperkeratosis — Clinical/structural presentation — S07 — Clinical Anchor/boundary open  
P45 Keratosis pilaris — Clinical Condition/presentation — S07 — Clinical Anchor  
P46 Seborrhoeic keratosis — Clinical Condition/lesion — S07↔S08 — Clinical Anchor  
P47 Skin tags — Lesion/benign growth presentation — S07↔S08 — Clinical Anchor

### S08
P48 Moles/nevi — Lesion/clinical anchor — S08 — Safety-aware Clinical Anchor  
P49 Changing mole — Safety/Referral Signal — P48/S08 — Safety/Referral  
P50 New/growing skin lesion — Safety/Referral Signal — S08 — Safety/Referral  
P53 Suspicious skin-cancer lesion — Safety/Referral Signal — S08 — Safety/Referral  
P54 Suspicious melanoma lesion — Safety/Referral Signal — S08 — Safety/Referral  
P55 Bleeding/non-healing lesion — Safety/Referral Signal — S08 — Safety/Referral  
P56 Rapid change in lesion size/shape/color — Safety/Referral Signal — S08 — Safety/Referral

### S09
P51 Chronic UV damage — Context/Discovery Problem — S09 — DISCOVERY CONTEXT; NOT NEED-LEVEL  
P22 Sun-related pigmentation — Context/presentation — S09↔S04 — Related  
P52 Actinic keratosis — Clinical/Safety-sensitive lesion — S09↔S08 — Safety/Referral

P51 locked disposition:
Discovery Problem / Context; in-scope as discovery context; Context/not Need-level; V1 Need Eligibility = NOT ELIGIBLE; Safety/Referral = NO automatic flag; Acceptance = NOT ACCEPTED.

### S10
P57 Autoimmune/autoinflammatory skin disease — Clinical Domain/Condition Family — S10 — Clinical Anchor/broad  
P58 Cutaneous lupus — Clinical Condition — P57/S10 — Clinical/Referral-sensitive  
P59 Adult-onset dermatomyositis with skin findings — Clinical Condition — P57/S10 — Clinical/Referral-sensitive  
P60 Acanthosis nigricans/systemic-associated skin changes — Clinical/systemic-associated presentation — S10 — Clinical Anchor  
P61 Photosensitivity — Symptom/clinical presentation — S09↔S10 — Clinical/Context relationship

## 5. Cross-Shelf Relationships

Pigmentation ↔ UV: P22 links S04 and S09.  
Acne ↔ Pigmentation: P13 links S03 and S04.  
Sebum ↔ Inflammation: P30 links S02 and S05.  
Lesions ↔ Safety: P48 leads to P49–P50 and P53–P56 Safety/Referral.  
UV ↔ Clinical Lesions: S09 links P52 to S08.

## 6. Boundary / Overlap Register

B01 P01/P02: P02 = related manifestation/overlapping presentation; no independent Need distinction established.

B02 P08–P12: P08 parent; P09–P11 manifestations/subtypes; P12 severity/clinical subtype. No independent Need determination.

B03 P17–P19: P17 presentation/problem-level; P18 Clinical Condition; P19 Sequela.

B04 P24–P26: P24 presentation; P25 symptom/manifestation; P26 Clinical Condition.

B05 P34/P35: P35 is not independent merely because it is a familiar named presentation.

B06 P48/P49/P50/P53–P56: Safety-oriented cluster, not Ordinary Care cluster.

B07 P51: P51 ≠ Diagnosis; P51 ≠ Accepted Need; P51 ≠ Automatic Safety Signal.

## 7. Obvious Coverage Gaps

G01 — Heterogeneous symptom/presentation layer: current 61 contain some symptoms/manifestations, but general presentation coverage is not demonstrably systematic. GAP / NOT TO BE FILLED IN V0.1.

G02 — Structural separation of lesion presentation vs lesion diagnosis: boundary is not uniformly represented. STRUCTURAL GAP.

G03 — Non-diagnostic customer-presenting formulations: Customer Language deferred/not verified; Map cannot claim adequate representation of real customer language. UNKNOWN, not a discovered omission.

G04 — HBI Operational Relevance: for some clinically valid items, distinct HBI operational role is not established. UNKNOWN.

## 8. Unknowns

U01 Final boundary of Problem vs Presentation  
U02 Final granularity of several Problem families  
U03 Operational relevance of several Clinical Conditions  
U04 Whether some broad families require further structural subdivision  
U05 Customer Reality coverage  
U06 Customer Language coverage  
U07 Final Coverage threshold

UNPROVEN ≠ FALSE; UNPROVEN = NOT AUTHORIZED.

## 9. Evidence / Provenance

V0.1 is primarily a structural artifact derived from the existing 61-item Discovery Input Stock and its prior evidence/review history. It does not independently re-verify every medical claim behind P01–P61.

Therefore:
Map placement ≠ medical validation  
Map placement ≠ HBI Need acceptance  
Map placement ≠ treatment authorization

Where evidence does not establish a stronger conclusion, the artifact retains UNKNOWN / GAP / CLINICAL ANCHOR / SAFETY-REFERRAL / CONTEXT rather than inventing certainty.

## 10. Structural Result

S01 Barrier/Hydration/Surface  
S02 Oil/Sebum/Follicular Balance  
S03 Acne/Follicular/Pore Presentation  
S04 Pigmentation/Color  
S05 Redness/Inflammation/Rash  
S06 Infection/Infestation  
S07 Texture/Keratinization/Surface Growth  
S08 Lesions/Growths/Change  
S09 Sun/UV-Related Change  
S10 Systemic/Autoimmune/Clinically Significant Skin Presentation

All P01–P61 are mapped, related, structurally reclassified, or explicitly marked clinical/safety/context.

No new candidate generated. No Need accepted. No Product relationship. No implementation.

## 11. V0.1 Status

Problem Unit Definition = PRODUCED  
Lightweight Problem Map = PRODUCED  
P01–P61 Mapping = PRODUCED  
Boundary/Overlap = PRODUCED  
Obvious Gaps = RECORDED  
Unknowns = RECORDED  
Evidence/Provenance = RECORDED

Problem Bank V1 = NOT STARTED  
Need Extraction = NOT STARTED  
Need Acceptance = NOT STARTED  
Product Mapping = NOT STARTED  
Implementation = NOT AUTHORIZED

**V0.1 is intentionally not a Final Problem Space. Its purpose is to provide a concrete object for independent Red-Team.**

### MANAGEMENT NOTE

This comment is the **full executable review input** for Grok-2. It is not a new Map and does not alter the Artifact. It exists solely to close the handoff gap identified in Grok-2 updates.

Grok-2: proceed with the previously issued eight-axis Red-Team against this exact text. Do not redesign the Map.