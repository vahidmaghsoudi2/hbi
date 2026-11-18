# HBI Problem Bank V1 — S10 Working Draft
## System-associated / Clinically Significant Skin Presentation

**Execution scope:** S10 only  
**Frozen source:** SKIN PROBLEM SPACE MAP V0.1, Issue #293  
**Frozen concepts:** P57, P58, P59, P60  
**Cross-shelf exclusion:** P61 remains S09↔S10 and is not duplicated or transferred  
**Customer Reality:** NOT VERIFIED  
**Customer Language:** NOT VERIFIED

---

## 1. Scope Verification

The frozen Map and S10 management order define exactly four S10 concepts:

- **P57 — Autoimmune / autoinflammatory skin disease**
- **P58 — Cutaneous lupus**
- **P59 — Adult-onset dermatomyositis with skin findings**
- **P60 — Acanthosis nigricans / systemic-associated skin changes**

P61 — Photosensitivity is **not an S10-only concept**. It remains the frozen **S09↔S10** relationship and is explicitly handled below without duplication, transfer, or creation of a new record.

S10 is an organizational/observational shelf, not a disease taxonomy. No new candidate is generated and no neighboring shelf is redesigned.

---

# 2. P57 — Autoimmune / autoinflammatory skin disease

### Concept identity / What is it?

A broad clinical domain/family covering autoimmune or autoinflammatory disorders that may have skin manifestations. The frozen Map classifies P57 as a **Clinical Domain / Condition Family** in S10.

It is intentionally a family-level structural concept, not a single diagnosis.

### Evidence / Provenance

- The American Academy of Dermatology describes autoimmune diseases as conditions in which the immune system attacks healthy cells, tissues, or organs, and notes that some autoimmune diseases affect the skin.
- DermNet maintains a dedicated autoimmune skin disease category containing multiple distinct disorders, supporting the existence of a heterogeneous clinical family rather than one uniform condition.

Sources:
- AAD, Autoimmune diseases: https://www.aad.org/public/diseases/a-z/autoimmune-diseases
- DermNet, Autoimmune skin diseases: https://dermnetnz.org/topics/autoimmune-skin-diseases

### Why HBI may need to recognize it

A broad family-level recognition can preserve the possibility that a clinically significant skin presentation belongs to an autoimmune/autoinflammatory domain without prematurely assigning a specific diagnosis.

### HBI role / classification

**Clinical Domain / Condition Family.**

P57 is a structural anchor for related clinical conditions. It does not itself establish a diagnosis or Need.

### What it must NOT mean

- Not a diagnosis of a specific autoimmune disease.
- Not proof that a skin presentation is autoimmune or autoinflammatory.
- Not an automatic Safety/Referral rule.
- Not an HBI Need.
- Not treatment or product-selection logic.
- Not permission to infer a disease from a visual manifestation alone.

### Boundary from neighboring concepts

- **P58 Cutaneous lupus:** a specific clinical condition within the broader autoimmune family, not synonymous with P57.
- **P59 Adult-onset dermatomyositis with skin findings:** a specific clinical condition with systemic implications, not equivalent to the entire P57 family.
- **P60 Acanthosis nigricans/systemic-associated skin changes:** a systemic-associated presentation with a different structural role; it is not automatically autoimmune.
- **P61 Photosensitivity:** symptom/clinical presentation with S09↔S10 relation; it does not identify a specific autoimmune diagnosis.

### What remains missing / unknown

- The final HBI operational relevance of the broad family is not established.
- Customer Reality and Customer Language are not verified.
- The appropriate granularity for any future subdivision is unresolved.
- The Map does not establish diagnostic criteria or workflow handling.

### Coverage / capability gap

**GAP:** The family-level shelf anchor is represented, but the boundary between broad clinical-domain recognition and later condition-level operational handling remains intentionally unresolved.

### Disposition

**KEEP — existing frozen Map concept.**

KEEP means retained in the working draft, not Canonical Problem or Need acceptance.

---

# 3. P58 — Cutaneous lupus

### Concept identity / What is it?

A clinical condition in which lupus affects the skin. The frozen Map classifies P58 as a **Clinical Condition** within P57/S10 and marks it **Clinical/Referral-sensitive**.

### Evidence / Provenance

- AAD describes cutaneous lupus as lupus affecting the skin and identifies several forms of cutaneous lupus.
- DermNet describes cutaneous lupus erythematosus as a group of autoimmune skin disorders and distinguishes acute, subacute, and chronic forms.

Sources:
- AAD, Cutaneous lupus: https://www.aad.org/public/diseases/a-z/cutaneous-lupus
- DermNet, Cutaneous lupus erythematosus: https://dermnetnz.org/topics/cutaneous-lupus-erythematosus

### Why HBI may need to recognize it

Recognizing P58 as a clinically significant condition helps keep a potentially systemic/autoimmune presentation distinct from ordinary redness, pigmentation, rash, or other surface descriptions. The role at this stage is recognition and structural separation, not diagnosis.

### HBI role / classification

**Clinical Condition; Clinical/Referral-sensitive.**

This is a structural classification only. It does not establish a referral protocol.

### What it must NOT mean

- Not a diagnosis based on appearance alone.
- Not proof that any red, scaly, pigmented, or photosensitive presentation is lupus.
- Not an automatic referral protocol.
- Not treatment authorization.
- Not an HBI Need.
- Not a product or recommendation rule.

### Boundary from neighboring concepts

- **P57:** broader autoimmune/autoinflammatory family; P58 is a specific condition.
- **P24/P26 and S05:** redness or rosacea presentations are not interchangeable with cutaneous lupus.
- **P20/P21 and S04:** pigmentation or vitiligo concepts do not establish lupus.
- **P61:** photosensitivity can relate to autoimmune disease, but photosensitivity alone is not cutaneous lupus.
- **P59:** dermatomyositis is a distinct autoimmune/systemic condition.

### What remains missing / unknown

- Customer Reality and Customer Language are not verified.
- HBI operational handling is not established.
- No diagnostic or referral decision rule is defined in the frozen Map.

### Coverage / capability gap

**GAP:** The condition is structurally represented, but the evidence package does not establish how HBI should operationally distinguish or handle suspected cases.

### Disposition

**KEEP — existing frozen Map concept.**

---

# 4. P59 — Adult-onset dermatomyositis with skin findings

### Concept identity / What is it?

A clinical condition involving dermatomyositis in adulthood with skin findings. The frozen Map classifies P59 as a **Clinical Condition** under P57/S10 and marks it **Clinical/Referral-sensitive**.

### Evidence / Provenance

- AAD describes dermatomyositis as a rare inflammatory disease that causes muscle weakness and skin changes.
- AAD notes that skin findings can occur with dermatomyositis and that the condition requires medical evaluation.
- DermNet describes dermatomyositis as an uncommon acquired connective tissue disease with characteristic cutaneous manifestations and systemic associations.

Sources:
- AAD, Dermatomyositis: https://www.aad.org/public/diseases/a-z/dermatomyositis
- DermNet, Dermatomyositis: https://dermnetnz.org/topics/dermatomyositis

### Why HBI may need to recognize it

P59 represents a clinically significant presentation whose skin findings may be part of a broader systemic condition. Structural recognition prevents a potentially important clinical presentation from being flattened into an ordinary cosmetic or surface descriptor.

### HBI role / classification

**Clinical Condition; Clinical/Referral-sensitive.**

No diagnostic or referral protocol is created here.

### What it must NOT mean

- Not a diagnosis from skin appearance alone.
- Not proof that a rash or skin change is dermatomyositis.
- Not a treatment protocol.
- Not a referral protocol.
- Not an HBI Need.
- Not product/recommendation eligibility.

### Boundary from neighboring concepts

- **P57:** family/domain anchor; P59 is one specific clinical condition.
- **P58:** cutaneous lupus is a distinct condition, despite potential overlap in some skin presentations.
- **P61:** photosensitivity can be a clinical feature but does not establish dermatomyositis.
- **P05/P24/P33:** sensitivity, redness, or unspecified rash are presenting descriptions, not equivalent to this condition.

### What remains missing / unknown

- Customer Reality and Customer Language are not verified.
- HBI operational role is not established.
- No diagnostic criteria or triage protocol is defined in the Map.

### Coverage / capability gap

**GAP:** P59 is structurally represented, but the later boundary between recognition and operational clinical handling remains undefined.

### Disposition

**KEEP — existing frozen Map concept.**

---

# 5. P60 — Acanthosis nigricans / systemic-associated skin changes

### Concept identity / What is it?

A clinical/systemic-associated skin presentation involving acanthosis nigricans and related systemic associations. The frozen Map classifies P60 as a **Clinical / systemic-associated presentation** in S10.

It is a presentation-level anchor and must not be collapsed into one presumed underlying systemic diagnosis.

### Evidence / Provenance

- AAD describes acanthosis nigricans as a skin condition that causes darker, thicker, often velvety skin and notes associations with underlying health conditions.
- DermNet describes acanthosis nigricans as hyperpigmentation and thickening, commonly affecting folds, and documents associations with insulin resistance and other conditions.

Sources:
- AAD, Acanthosis nigricans: https://www.aad.org/public/diseases/a-z/acanthosis-nigricans
- DermNet, Acanthosis nigricans: https://dermnetnz.org/topics/acanthosis-nigricans

### Why HBI may need to recognize it

Recognition can preserve an important distinction between a visible skin presentation and the possibility of an associated systemic context. The structural role is to avoid treating the presentation as merely generic pigmentation.

### HBI role / classification

**Clinical / systemic-associated presentation.**

No underlying systemic diagnosis is inferred.

### What it must NOT mean

- Not proof of insulin resistance, diabetes, malignancy, or another specific underlying condition.
- Not a diagnosis from appearance alone.
- Not an automatic referral protocol.
- Not a treatment or product rule.
- Not an HBI Need.
- Not permission to infer a systemic disease from the presentation alone.

### Boundary from neighboring concepts

- **P17/P20:** pigmentation presentations may describe color change, but P60 carries a distinct systemic-associated structural role.
- **P22:** sun-related pigmentation is a different context and must not be conflated with P60.
- **P57:** P60 is not automatically autoimmune/autoinflammatory.
- **P61:** photosensitivity is a separate symptom/clinical presentation with a cross-shelf relation.

### What remains missing / unknown

- Customer Reality and Customer Language are not verified.
- HBI operational relevance is not established.
- The Map does not define diagnostic criteria or an underlying-cause decision tree.

### Coverage / capability gap

**GAP:** The systemic-associated presentation is represented, but its later operational boundary and customer-presenting frequency remain unverified.

### Disposition

**KEEP — existing frozen Map concept.**

---

# 6. P61 Cross-Shelf Handling — Photosensitivity

P61 is **not an S10 concept for this working draft**.

The frozen Map places P61 as:

**Photosensitivity — Symptom / clinical presentation — S09↔S10 — Clinical / Context relationship**

Therefore:

- P61 is not duplicated in this artifact.
- P61 is not transferred from S09 to S10.
- No new P61 record is created.
- P61 is referenced only to preserve the existing cross-shelf relationship.
- Photosensitivity alone must not be interpreted as a diagnosis of lupus, dermatomyositis, or another autoimmune disease.
- No safety/referral protocol is derived from P61 here.

This preserves the frozen Map rather than rewriting its shelf structure.

---

# 7. S10 Coverage / Gap Register

| Area | Current state | Gap / limitation |
|---|---|---|
| Frozen S10 scope | P57–P60 represented | No new candidates generated |
| Broad autoimmune/autoinflammatory family | P57 represented | Final operational granularity unresolved |
| Cutaneous lupus | P58 represented | Diagnostic/operational handling not defined |
| Adult-onset dermatomyositis with skin findings | P59 represented | Diagnostic/operational handling not defined |
| Systemic-associated skin presentation | P60 represented | Underlying-cause boundary intentionally unresolved |
| P61 relationship | S09↔S10 preserved | No duplication/transfer |
| Clinical boundary | Clinical existence separated from Need | HBI operational relevance unproven |
| Customer Reality | NOT VERIFIED | No verified customer corpus |
| Customer Language | NOT VERIFIED | No verified customer language corpus |
| Need | No Need accepted | Need Extraction NOT AUTHORIZED |
| Product/Recommendation | Out of scope | No mapping or scoring |
| Implementation | NOT AUTHORIZED | No code/schema/API/DB/UI changes |

---

# 8. Mandatory Self-Critique

1. **P57 breadth:** The family-level concept is heterogeneous. Treating it as one diagnosis would be structurally wrong, so this artifact retains it only as a domain/family anchor.
2. **P58/P59 specificity:** Both are clinical conditions with potentially important systemic context. The artifact preserves their distinction without inventing diagnostic or referral rules.
3. **P60 causality risk:** Acanthosis nigricans has recognized systemic associations, but appearance alone does not establish a particular underlying disease. The artifact deliberately avoids that inference.
4. **P61 integrity:** P61 is kept as S09↔S10 rather than duplicated. Cross-shelf structure is preserved rather than “cleaned up” by quietly rewriting the Map.
5. **Medical evidence boundary:** Medical sources support existence and clinical characterization. They do not prove HBI Need acceptance, Customer Reality, Customer Language, or product/recommendation eligibility.
6. **Coverage limitation:** Four concepts cannot prove that S10 exhausts all system-associated or clinically significant skin presentations. The gap is recorded, not filled with invented candidates.
7. **Customer evidence limitation:** No prevalence, customer wording, demand frequency, or operator workflow is claimed without verified evidence.
8. **Operational boundary:** “Clinical/Referral-sensitive” in the frozen Map is retained as classification language only. This artifact does not turn it into an operational referral protocol.

---

# 9. Governance Footer

**S10 Execution:** COMPLETED  
**S10 Acceptance:** PENDING INDEPENDENT REVIEW  
**Management Baseline:** PENDING  
**Repository Master Baseline:** unchanged by this working draft  

**Canonical Problem admission:** NOT AUTHORIZED  
**Need Extraction:** NOT AUTHORIZED  
**Need Acceptance:** NOT AUTHORIZED  
**Need→Product Mapping:** NOT AUTHORIZED  
**Recommendation/Scoring changes:** NOT AUTHORIZED  
**Implementation:** NOT AUTHORIZED  
**Merge:** NOT AUTHORIZED  

**Customer Reality:** NOT VERIFIED  
**Customer Language:** NOT VERIFIED  

**Principle preserved:**

**DONE ≠ VERIFIED ≠ ACCEPTED ≠ MERGED**

This artifact is an execution working draft only. It is not independent verification, acceptance, management baseline, or downstream implementation authorization.
