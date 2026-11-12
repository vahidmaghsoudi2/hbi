# HBI Problem Bank V1 — S09 Working Draft
## Sun / UV-Related Change

**Execution scope:** S09 only  
**Frozen source:** HBI SKIN PROBLEM SPACE MAP V0.1, Issue #293 management input  
**Frozen concepts:** P22, P51, P52  
**Execution status:** WORKING DRAFT  
**Customer Reality:** NOT VERIFIED  
**Customer Language:** NOT VERIFIED  

---

## 1. Scope Verification

The frozen Map V0.1 places exactly three concepts in S09:

- **P22 — Sun-related pigmentation / pigmentation associated with sun exposure**
- **P51 — Chronic UV damage**
- **P52 — Actinic keratosis**

S09 is defined as **Sun / UV-Related Change**.

Important structural constraints:

- P22 is cross-shelf **S04↔S09** and must remain represented in S04. This artifact does not duplicate, transfer, or create a second P22.
- P51 has a prior locked management disposition and is not reopened or upgraded.
- P52 is a clinical/safety-sensitive lesion concept and remains non-diagnostic.
- P46/P47 and other concepts outside S09 are out of scope.
- No new Problem candidate is generated.

**Scope result:** 3 concepts, exactly as frozen.

---

# 2. P22 — Sun-related pigmentation

### Concept identity / What is it?

A pigmentation-related presentation associated with sun exposure. The frozen Map classifies P22 as a **Context / pigmentation presentation**, linked to P17/S04 and cross-shelf to S09.

This is intentionally broader than assigning a diagnosis such as solar lentigo.

### Evidence / Provenance

- DermNet describes solar lentigo as a common benign flat pigmented lesion predominantly on sun-exposed skin and states that it develops from chronic ultraviolet radiation exposure.
- DermNet also distinguishes solar lentigines from other brown marks and notes that sun-exposed pigmentation can have clinically relevant differentials.

Sources:
- DermNet, Solar lentigo: https://dermnetnz.org/topics/solar-lentigo
- DermNet, Brown spots and freckles: https://dermnetnz.org/topics/brown-spots-and-freckles

### Why HBI may need to recognize it

A sun-associated pigmentation presentation can be relevant when a person presents with a change in skin color or spots and the sun/UV context is part of the observed or reported picture. Recognition of the context helps prevent collapsing a presentation into an unsupported diagnosis.

### HBI role / classification

**Context / pigmentation presentation; S04↔S09 cross-shelf relation.**

P22 may inform recognition and contextual framing. It does not itself establish a diagnosis or Need.

### What it must NOT mean

- Not a diagnosis of solar lentigo.
- Not proof that every sun-associated dark spot has the same cause.
- Not an automatic HBI Need.
- Not a treatment or product-selection rule.
- Not a reason to transfer P22 out of S04.

### Boundary from neighboring concepts

- **P17 Hyperpigmentation/dark spots:** broader pigmentation presentation in S04; P22 adds a sun-associated context.
- **P51 Chronic UV damage:** broader exposure/damage context; P22 is a pigmentation presentation associated with that context.
- **P52 Actinic keratosis:** distinct clinical/safety-sensitive lesion concept; pigmentation alone must not be treated as AK.
- **S08 lesion signals:** an observed pigmented spot cannot be assigned a lesion diagnosis from appearance alone.

### What remains missing / unknown

- Customer Reality for sun-associated pigmentation is not verified.
- Customer Language is not verified.
- HBI operational relevance at the Need level is not established.
- The Map does not establish a diagnostic rule for distinguishing sun-related pigmentation from other pigmented presentations.

### Coverage / capability gap

**GAP:** The current Map records the structural relationship between pigmentation and UV context, but does not prove how often real HBI customers present this way or what exact operational role the context should later have.

### Disposition

**KEEP — existing frozen Map concept.**

KEEP means retain the concept in this working draft. It does not mean Canonical Problem or Need acceptance.

---

# 3. P51 — Chronic UV damage

### Concept identity / What is it?

A chronic UV-exposure/damage context associated with cumulative sun-related skin change.

The frozen Map explicitly classifies P51 as:

- **Discovery Problem / Context**
- in-scope as discovery context
- **Context / not Need-level**
- **V1 Need Eligibility = NOT ELIGIBLE**
- **Safety/Referral = NO automatic flag**
- **NOT ACCEPTED**

### Evidence / Provenance

- AAD states that sunlight damages healthy skin cells and that damage can build up over time, producing signs such as freckles, age spots, wrinkles and, in some people, precancerous skin growths.
- AAD states that actinic keratosis develops on skin badly damaged by UV light.

Sources:
- AAD, Sun damage and your skin: https://www.aad.org/public/everyday-care/sun-protection/sun-damage-skin
- AAD, Actinic keratosis: Who gets and causes: https://www.aad.org/public/diseases/skin-cancer/actinic-keratosis-causes

These sources support the existence of cumulative UV-related skin damage. They do not authorize an HBI Need or an automatic safety classification for P51.

### Why HBI may need to recognize it

P51 can provide contextual information about cumulative UV exposure/damage when interpreting other sun-related presentations. Its value in this stage is contextual recognition, not conversion into a care category.

### HBI role / classification

**Discovery Context / contextual Problem Unit.**

The prior locked management classification is preserved exactly. No upgrade is made.

### What it must NOT mean

- Not a diagnosis.
- Not an Accepted Need.
- Not an automatic Safety/Referral signal.
- Not evidence that a particular lesion is malignant or premalignant.
- Not authorization for treatment, referral protocol, product selection, or recommendation logic.
- Not permission to reopen its prior disposition.

### Boundary from neighboring concepts

- **P22:** pigmentation presentation associated with sun exposure; P51 is the broader chronic UV damage context.
- **P52:** specific clinical/safety-sensitive lesion concept; P51 does not imply P52.
- **S08:** lesion-related safety signals require their own structural representation and must not be inferred from P51 alone.

### What remains missing / unknown

- Customer Reality and Customer Language are not verified.
- The operational relevance of P51 to later HBI workflows remains unproven.
- The Map does not define a quantitative exposure threshold or diagnostic criterion for “chronic UV damage.”

### Coverage / capability gap

**GAP:** Contextual UV damage is structurally represented, but its real-world presentation frequency and later HBI operational role are not established.

### Disposition

**KEEP — locked prior management classification.**

This disposition does **not** reopen, upgrade, or accept P51. The locked status remains: **Context / not Need-level; V1 Need Eligibility = NOT ELIGIBLE; Safety/Referral = NO automatic flag; NOT ACCEPTED.**

---

# 4. P52 — Actinic keratosis

### Concept identity / What is it?

A clinical lesion associated with chronically UV-exposed skin. The frozen Map classifies P52 as a **Clinical / Safety-sensitive lesion** and links it to **S09↔S08**.

Medical sources describe actinic keratosis as a precancerous skin growth/lesion associated with significant UV damage.

### Evidence / Provenance

- AAD states that actinic keratosis develops when skin has been badly damaged by UV light from the sun or indoor tanning.
- AAD describes common appearances including rough/scaly patches or bumps and notes that some AKs can develop into squamous cell carcinoma.
- DermNet describes actinic keratosis as a precancerous scaly spot on sun-damaged skin and notes that it may present as a flat/thickened papule or plaque with a scaly or horny surface.

Sources:
- AAD, Actinic keratosis: Signs and symptoms: https://www.aad.org/public/diseases/skin-cancer/actinic-keratosis-symptoms
- AAD, Actinic keratosis: Overview: https://www.aad.org/public/diseases/skin-cancer/actinic-keratosis-overview
- DermNet, Actinic keratosis: https://dermnetnz.org/topics/actinic-keratosis

### Why HBI may need to recognize it

Because the frozen Map identifies P52 as a clinical/safety-sensitive lesion, recognizing the concept prevents an apparently sun-related skin change from being treated as an ordinary pigmentation or cosmetic presentation without appropriate clinical boundary awareness.

### HBI role / classification

**Clinical / Safety-sensitive lesion; S09↔S08 cross-shelf relation.**

Recognition is structural only in this working draft. No diagnostic decision rule or referral protocol is created.

### What it must NOT mean

- A visual description alone is not a confirmed diagnosis of AK.
- A sun-exposed rough or pigmented area must not automatically be labeled AK.
- P52 does not authorize treatment instructions.
- P52 does not create a referral protocol.
- P52 does not create product or recommendation logic.
- P52 does not convert the whole S09 shelf into a safety/referral shelf.
- Medical evidence for AK does not prove HBI Need acceptance.

### Boundary from neighboring concepts

- **P51 Chronic UV damage:** exposure/damage context; P52 is a distinct clinical lesion concept.
- **P22 Sun-related pigmentation:** pigmentation/context presentation; P52 is not synonymous with sun-related pigmentation.
- **S08 lesion/change concepts:** P52 has a deliberate S09↔S08 relationship because it is a UV-associated clinical lesion, but it remains the frozen P52 concept in S09 and is not transferred.
- **S07 texture/keratinization:** rough/scaly surface appearance can overlap descriptively, but appearance alone does not collapse P52 into S07.

### What remains missing / unknown

- Customer Reality is not verified.
- Customer Language is not verified.
- The final HBI operational role beyond structural recognition is not established.
- No diagnostic or triage protocol is defined by the Map.

### Coverage / capability gap

**GAP:** The structural Map captures P52 as a UV-associated clinical/safety-sensitive lesion, but the later operational handling boundary remains intentionally unspecified at this stage.

### Disposition

**KEEP — existing frozen Map concept.**

KEEP means retain the concept in the working draft. It does not mean Canonical Problem admission, Need admission, treatment authorization, or referral authorization.

---

# 5. S09 Coverage / Gap Register

| Area | Current state | Gap / limitation |
|---|---|---|
| Frozen S09 scope | 3 concepts: P22, P51, P52 | No new candidates generated |
| UV/pigmentation context | P22 represented | Customer Reality/Language not verified |
| Chronic UV damage context | P51 represented with locked status | Operational role remains unproven |
| UV-associated clinical lesion | P52 represented | Diagnostic/operational protocol not defined |
| S04↔S09 relation | P22 retained as cross-shelf | No duplication or transfer |
| S09↔S08 relation | P52 retained as cross-shelf | No shelf rewrite |
| Safety boundary | P52 safety-sensitive only | No diagnosis/referral protocol |
| Need boundary | No Need accepted | Need Extraction NOT AUTHORIZED |
| Customer Reality | NOT VERIFIED | External reality evidence absent |
| Customer Language | NOT VERIFIED | Customer corpus absent |
| Product/Recommendation | Out of scope | No mapping or scoring |
| Implementation | NOT AUTHORIZED | No code/schema/API/DB/UI changes |

---

# 6. Mandatory Self-Critique

1. **P22 ambiguity:** “Sun-related pigmentation” is broader than any single named diagnosis. The artifact deliberately does not collapse it into solar lentigo or another diagnosis.
2. **P51 locked status:** The working draft preserves the prior management disposition instead of treating medical evidence about UV damage as permission to reopen it.
3. **P52 safety boundary:** Medical evidence establishes what AK is and its clinical significance, but the artifact does not infer diagnosis from appearance or create an HBI referral/treatment protocol.
4. **Cross-shelf integrity:** P22 remains S04↔S09 and P52 remains S09↔S08. No transfer or duplication is introduced.
5. **Evidence limitation:** Medical evidence supports existence and clinical characterization, not Customer Reality, Customer Language, HBI Need acceptance, or product/recommendation eligibility.
6. **Coverage limitation:** Three frozen concepts do not prove that S09 exhausts the real-world UV-related skin problem space. The artifact records this as an unresolved coverage limitation rather than generating new candidates.
7. **No synthetic customer evidence:** No customer phrasing, prevalence, demand frequency, or operator workflow is claimed without verified source evidence.

---

# 7. Governance Footer

**S09 Execution:** COMPLETED  
**S09 Acceptance:** PENDING INDEPENDENT REVIEW  
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
DONE ≠ VERIFIED ≠ ACCEPTED ≠ MERGED

This artifact is an execution working draft only. It must not be treated as independent verification, acceptance, management baseline, or authorization for downstream implementation.
