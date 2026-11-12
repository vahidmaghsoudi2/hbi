# HBI Skin Consultation Intelligence — Integrated Roadmap v1.0

**Status:** Consolidated roadmap proposal for PO review; not an implementation contract.  
**Scope:** Skin consultation and skin-product intelligence only.  
**Strategic anchors:** Issues #71, #78, #223, #225, #276 and #278; approved product-intake contract: `docs/architecture/SKIN_PRODUCT_INTAKE_EXECUTION_CONTRACT_v1.1.md`.  
**Governance:** No merge, schema change, ontology change, scoring change, migration, or implementation expansion is authorized by this roadmap.

## 1. Purpose and product priority

HBI is primarily a high-quality consultation and decision-support system, not merely a product catalogue or a product recommender. Rich, accurate consultation and evidence-grounded decision support are the priority; product recommendation is downstream and must be justified by the consultation findings. No percentage estimate is used as a product requirement or performance metric.

The target workflow starts with a customer's skin concern, develops and tests plausible explanations, uses known customer context to reduce uncertainty, asks targeted follow-up questions where valuable, supports human review, and only then evaluates whether any product recommendation is justified.

## 2. Non-negotiable principles

1. **Concern first, product second.** A statement such as “my skin has become dry” must not trigger an automatic moisturizer recommendation.
2. **Hypotheses are not diagnoses.** Possible causes are provisional reasoning paths, not confirmed medical conclusions.
3. **Profile-informed reasoning.** Use relevant, provenance-bearing customer ProfileFacts and the current consultation/Case context to support, narrow, or challenge hypotheses.
4. **Current Case context matters.** A current answer can override or qualify a previously stored ProfileFact for the present consultation; do not silently rewrite durable ProfileFacts from a single answer.
5. **Human review is explicit.** Present remaining plausible paths, rationale, evidence, uncertainty, and contradictions so the operator/qualified professional can eliminate or select paths. The desired operational pattern may reduce a larger candidate set (up to roughly ten possibilities where justified) to one or two paths for further assessment; ten is a planning ceiling/example, not a fixed algorithmic requirement.
6. **Ask rather than guess.** If a missing answer can materially change the decision, ask the next best question. If information remains insufficient, say so and continue gathering information, defer product advice, or recommend appropriate professional assessment.
7. **Evidence is traceable.** Separate verified facts, manufacturer claims, evidence, inference, unknowns, and conflicts. Preserve source/provenance and review status.
8. **Ingredient presence is not product efficacy.** An ingredient's presence alone does not establish that the finished product is effective, suitable, safe, or appropriate for a particular customer.
9. **Product-side and customer-side safety are separate.** Product identity/quality/contraindication knowledge, customer medical context, customer-product compatibility, inventory, and final recommendation eligibility must not be collapsed into one flag.
10. **No silent inference promotion.** An INFERENCE must not silently become FACT or approved ProductKnowledge.
11. **Empty is not safe.** EMPTY, UNKNOWN, CONFLICT, and confirmed absence are distinct states. Neither EMPTY nor UNKNOWN means SAFE or ELIGIBLE.
12. **Reuse before invention.** Inspect current repository models, services, APIs, contracts, tests, and runtime evidence before proposing a new entity, field, ontology, pipeline, or score.
13. **No unauthorized scope expansion.** Existing scoring/ranking/eligibility behavior stays frozen unless the PO explicitly authorizes a bounded change.
14. **Governance states remain distinct:** DONE ≠ VERIFIED ≠ ACCEPTED ≠ MERGED.

## 3. End-to-end target flow

`Customer concern + current Case + relevant ProfileFacts`
→ `normalize concern / identify decision context`
→ `check sufficiency, safety, and need for professional assessment`
→ `generate bounded plausible hypotheses`
→ `link each hypothesis to supporting, weakening, missing, and conflicting evidence`
→ `use profile and current answers to reduce/qualify the candidate set`
→ `identify the highest-value next question or action`
→ `capture answer in current Case with provenance`
→ `re-evaluate hypotheses and uncertainty`
→ `human review / eliminate / retain paths`
→ `derive or clarify the customer's need`
→ `evaluate product knowledge and finished-product evidence`
→ `check product gates, customer compatibility, contraindications, and stock`
→ `use existing recommendation/ranking contract only when authorized conditions are met`
→ `show recommendation or explain why no recommendation is justified`
→ `persist traceable rationale, evidence, unknowns, conflicts, and outcome`.

This is the target conceptual flow. It is not a claim that every stage is implemented in current master.

## 4. Roadmap phases and gates

### Phase 0 — Repository reality and contract reconciliation

**Goal:** Establish exactly what exists now before designing or implementing more.

- Record current master SHA and audit timestamp.
- Reconcile Issues #71, #78, #223, #225, #276, and #278 with current code and tests; historical SHAs are not current-master evidence.
- Inspect the approved execution contract and relevant models, migrations, services, endpoints, UI, tests, and runtime traces.
- Build a capability matrix: implemented and tested; implemented but not verified end-to-end; partial; absent; contradicted; unknown.
- Trace the real path from customer input through Case/ProfileFacts, question generation, evidence gaps, need normalization, ProductKnowledge, eligibility, ranking, explanation, persistence, and readback.
- Distinguish code presence from actual invocation, durable persistence, API/UI visibility, and runtime behavior.

**Exit gate:** A source-linked reality matrix with current commit SHA, file/test references, gaps, and no unsupported “DONE” claims.

### Phase 1 — Consultation context and concern normalization

**Goal:** Represent what the customer reports without prematurely converting it into a cause or product request.

- Preserve the customer's original words and provenance.
- Normalize the concern into a bounded, explainable representation using existing contracts where possible.
- Keep separate: reported symptom/concern, observed fact, inferred factor, underlying need, decision, and recommendation.
- Identify missing context and contradictions.
- Use the current consultation/Case as the active context and relevant ProfileFacts as prior evidence, not unquestionable truth.

**Exit gate:** Tests demonstrate that the concern is represented without automatic diagnosis or automatic product selection.

### Phase 2 — Sufficiency, safety, and escalation gate

**Goal:** Decide whether it is appropriate to continue automated decision support, ask more questions, defer advice, or request professional assessment.

- Evaluate whether enough relevant information exists for the next decision.
- Check for safety-relevant unknowns, conflicts, contraindications, and warning conditions within the approved scope.
- Distinguish “not enough information” from “no issue found.”
- Do not invent medical triage rules. Any clinical safety/escalation policy must be evidence-based, explicitly scoped, and reviewed by qualified stakeholders.
- When uncertainty or risk is beyond the approved scope, do not force a product recommendation.

**Exit gate:** Explicit, tested outcomes for sufficient information, insufficient information, unresolved conflict, and out-of-scope/professional-review paths.

### Phase 3 — Hypothesis generation and evidence mapping

**Goal:** Develop a bounded set of plausible explanations for a concern such as skin dryness, without presenting them as diagnoses.

- Generate only hypotheses relevant to the concern and available context; “up to about ten” is a planning example, not a required fixed count.
- For each hypothesis, record its status and rationale plus supporting evidence, weakening evidence, missing evidence, conflicts, and provenance.
- Potential illustrative categories for dryness may include environmental exposure, cleansing routine, skin-barrier disruption, hydration-related factors, overuse/irritation from active ingredients, or other explanations. These are examples for discovery, not a validated clinical taxonomy or a predetermined list.
- Separate customer-reported facts from model-generated inferences and manufacturer claims.
- Do not create a new ontology/schema until repository reality and reuse/extend/new analysis are complete and the PO approves the contract.

**Exit gate:** Each hypothesis can be traced to evidence and uncertainty; no unsupported hypothesis is presented as fact or diagnosis.

### Phase 4 — Profile-informed reduction and progressive questioning

**Goal:** Reduce uncertainty efficiently and ask questions whose answers can change the next decision.

- Compare hypotheses with relevant ProfileFacts and current Case answers.
- Record why evidence supports, weakens, excludes, or leaves a hypothesis unresolved; do not eliminate a path solely because a field is empty.
- Select the next question/action by decision value: what answer is most likely to distinguish remaining paths or change the safe next step?
- Present clear, bounded answer options when appropriate; retain an “other / not sure” path where the contract and UX support it.
- Store the answer in the current consultation/Case context with provenance. Do not automatically convert it into a durable ProfileFact.
- Re-evaluate the candidate set after each answer; stop asking when the answer will not materially change the decision or when a safe next step is already clear.

**Existing related work:** Issue #223 tracks Evidence Gap → Next Question / Progressive Profiling. Issue #225 describes a bounded skin concern next-question → Case answer → recommendation slice, including `Case.evidence_gaps` and reuse of the existing recommendation endpoint. That bounded slice is not proof of a general-purpose hypothesis-generation and elimination engine.

**Exit gate:** Tests cover missing information, known information, conflicting answers, current-Case-over-ProfileFact precedence, meaningful question selection, and observable answer-dependent outcomes.

### Phase 5 — Human review and decision checkpoint

**Goal:** Make uncertainty and human judgment operational, not merely descriptive.

- Present the remaining plausible hypotheses and their supporting/contradicting evidence.
- Show why each path remains, was weakened, or was excluded.
- Allow the operator/qualified professional to remove hypotheses and retain one or two paths for further assessment where appropriate.
- Preserve who made the decision, what changed, and why.
- Do not portray the operator's selection as a medical diagnosis unless an appropriately qualified professional and applicable process explicitly establish that conclusion.
- If the evidence remains inadequate, retain the uncertainty and request more information or assessment rather than manufacturing certainty.

**Exit gate:** Review actions are auditable and the resulting decision state can be reconstructed.

### Phase 6 — Need formulation and ProductKnowledge/evidence readiness

**Goal:** Connect the assessed concern/need to trustworthy knowledge about finished products.

- Normalize the need only after the consultation evidence supports doing so.
- Reuse the existing Need/ProductKnowledge/Evidence contracts; inspect the actual implementation before any changes.
- Maintain the current V1 claim distinctions: `FACT`, `MANUFACTURER_CLAIM`, `EVIDENCE`, `INFERENCE`, `UNKNOWN`, `CONFLICT`.
- Research/input flows through Evidence → QA/conflict resolution → ProductKnowledge.
- Research drafts and PENDING evidence remain provisional; unresolved conflicts do not become trusted ProductKnowledge.
- Capture ingredient identity, role/use, concentration/formulation when known, target skin/site, warnings, contraindications, and supporting sources only to the extent supported by evidence and the approved contract.
- Do not infer finished-product efficacy from an ingredient list alone.
- Preserve the difference between product claims, independent evidence, and an inference about possible suitability.

**Exit gate:** Every material product-knowledge assertion has a type, source/provenance, review status, and explicit uncertainty where appropriate.

### Phase 7 — Product intake, identity, safety, and operational readiness

**Goal:** Ensure the product record is trustworthy and operationally usable before it can be recommended.


**Medical scope clarification — skin assessment and professional escalation (planning rule; not a new clinical protocol)**

HBI must not avoid medically relevant terminology or evidence-based analysis merely because the consultation concerns skin. Within the gallery's approved scope, the workflow may assess routine skin-care concerns, review relevant reported or observed skin features, and evaluate product ingredients, intended use, evidence of finished-product efficacy, contraindications, precautions, adverse effects, and customer-specific suitability. Each material conclusion must retain its evidence/provenance, uncertainty, and review status.

This is decision support for skin care, not an autonomous diagnosis or a substitute for medical assessment. A staff member's medical credential does not, by itself, establish specialist dermatology qualification or authorize every clinical decision. HBI must support human review and a documented referral/defer outcome when symptoms suggest a possible skin disease, warning conditions are present, uncertainty exceeds the approved scope, or diagnosis/treatment by a qualified clinician is needed. It must not force a product recommendation in those cases.

Do not invent clinical warning criteria, diagnostic rules, or referral thresholds during implementation. Any operational clinical safety/escalation policy must be evidence-based, explicitly scoped, and reviewed by appropriately qualified stakeholders before it is treated as an executable rule. This clarification records the product/business boundary; it does not authorize a new diagnosis engine, treatment workflow, schema, or clinical protocol.

Apply the PO-approved contract `SKIN_PRODUCT_INTAKE_EXECUTION_CONTRACT_v1.1.md`:

- Draft minimum identity: `product_id`, `product_name`, `brand`; requirements increase by lifecycle stage.
- Preserve current DuplicateCheck semantics; do not invent fuzzy matching or new identity models.
- Before approval, contraindication status must be supported information or explicit UNKNOWN; EMPTY is not safe.
- Keep product safety, customer medical context, and customer × product safety separate.
- Product-level gates remain: ACTIVE, identity VERIFIED, product QA VALID, Evidence Readiness PASS, D3 requirements satisfied, and operational stock available.
- Product registration and stock receipt are separate. Registration must not invent available stock, sellable units, or price.
- AI may assist research/enrichment but cannot approve, activate, bypass QA, bypass Evidence Readiness, or convert inference into fact.

**Exit gate:** Product intake and stock lifecycle are verified on the real path; no unverified or unavailable product is silently treated as recommendable.

### Phase 8 — Customer × Product suitability and recommendation

**Goal:** Recommend only when the consultation state and product evidence justify it.

- Evaluate need matching separately from product eligibility and customer-specific suitability.
- Consider relevant customer context, contraindications, target skin/site, known sensitivities, warnings, uncertainty, and evidence quality within approved policy.
- Keep product eligibility, customer-specific eligibility, and final recommendation eligibility distinct.
- Use the existing recommendation endpoint, eligibility gates, scoring, and ranking unchanged unless a separate PO-approved implementation work package explicitly authorizes a change.
- Do not force a recommendation: valid outcomes include ask another question, defer, show no eligible product, or request professional assessment.
- Explain why a product is considered, why alternatives are excluded, and what remains unknown.
- Persist evaluated ineligible-product reasons where the existing contract requires it; verify readback and UI presentation rather than relying on logs alone.

**Exit gate:** End-to-end tests demonstrate justified recommendations and correct non-recommendation behavior, with no scoring changes hidden inside unrelated work.

### Phase 9 — Explanation, provenance, persistence, and readback

**Goal:** Make the reasoning auditable to operators and reconstructable after the interaction.

- Preserve concern, relevant context, questions/answers, hypothesis status changes, human decisions, evidence references, unknowns/conflicts, product decision, and recommendation rationale.
- Explain both positive reasons and disqualifying/limiting reasons.
- Distinguish source facts, manufacturer claims, evidence, and model inference in the UI/API.
- Verify durable storage, API readback, and the actual browser/operator experience.
- A successful API response alone does not prove end-to-end completion.

**Exit gate:** An operator can reconstruct why the system asked a question, retained or removed a path, recommended or rejected a product, or declined to recommend.

### Phase 10 — Validation, release, and governance

**Goal:** Accept only behavior supported by reproducible evidence.

- Unit tests for state distinctions and rules.
- Service/API integration tests for Case/ProfileFact precedence, Evidence Gap lifecycle, and recommendation boundaries.
- End-to-end tests for customer input → question → answer → reassessment → human review → product outcome → persisted readback.
- Negative tests for EMPTY/UNKNOWN, unresolved CONFLICT, unsupported manufacturer claims, missing evidence, ineligible products, unavailable stock, and insufficient consultation data.
- Runtime/browser evidence for critical flows; report the tested commit SHA and environment.
- Separate statuses: implemented, tests passed, runtime verified, PO accepted, merged.
- No merge without explicit PO authorization. No G8 completion claim without current, reproducible runtime evidence.

**Exit gate:** Evidence package is linked to the exact commit and the PO explicitly accepts the bounded work package.

## 5. Cross-cutting contracts to keep separate

| Concept | Required distinction |
|---|---|
| Customer concern | What the customer reports; not a diagnosis |
| Observation / ProfileFact | Recorded information with source and context |
| Current Case answer | Current consultation evidence; may qualify prior profile data |
| Hypothesis / inference | Provisional explanation; never silently a fact |
| Evidence Gap | Missing or unresolved information that can affect a decision |
| Next Question / Action | Chosen for its expected decision value |
| Need | What the customer may need after sufficient assessment |
| ProductKnowledge | Reviewed, traceable knowledge about the product |
| Manufacturer claim | Attributed claim; not automatically verified truth |
| Product eligibility | Product-side lifecycle/quality/evidence/stock gates |
| Customer suitability | Customer-specific compatibility and safety |
| Recommendation | Downstream decision with rationale and limitations |
| Human decision | Explicit review/override with actor and reason |

## 6. Repository work already identified — and limits of what is proven

- **Issue #71:** decision architecture and contract baseline.
- **Issue #78:** decision-quality and end-to-end reality audit.
- **Issue #223:** Evidence Gap → Next Question / Progressive Profiling; prior findings are historical and require current-master reconciliation.
- **Issue #225:** bounded skin next-question → Case answer → recommendation vertical slice; not the complete hypothesis engine.
- **Issue #276:** skin-product intake strategic baseline.
- **Issue #278:** consolidated roadmap and reality reconciliation; historical checkpoint SHA is not current-master proof.
- **Execution contract:** `docs/architecture/SKIN_PRODUCT_INTAKE_EXECUTION_CONTRACT_v1.1.md`, PO-approved for separately authorized implementation work packages.

These references establish relevant prior work and constraints; they do not, by themselves, prove that the full target flow is implemented in current master. Phase 0 must verify the current code, tests, and runtime.

## 7. Explicit non-goals unless separately approved

- Autonomous medical diagnosis.
- Automatic conversion of hypotheses into diagnoses.
- Unbounded or opaque hypothesis generation.
- New schema/entity/ontology without a repository reality audit and PO approval.
- Recommendation scoring/ranking redesign.
- Treating a product ingredient as sufficient proof of finished-product efficacy.
- Treating missing data as safe or eligible.
- AI-controlled approval/activation or bypass of quality and governance gates.
- OCR/PDF ingestion, supplier APIs, SKU/GTIN allocation, full regulatory engine, adverse-event management, or rich eligibility engine unless separately authorized under the existing product-intake contract.

## 8. Immediate execution sequence

1. **Documentation proposal registered:** PR #348 contains this roadmap; it remains open for PO review. Registration is not acceptance or merge authorization.
2. **Next:** perform a current-master reality audit, beginning with SHA capture and a source-linked matrix for the stages above.
3. **Then:** reconcile the audit against #223/#225/#278 and identify the smallest genuine gap without duplicating existing work.
4. **Then:** present a bounded work package with acceptance tests and explicit out-of-scope items for PO authorization.
5. **Only after authorization:** implement, test, gather runtime/browser evidence, and request PO acceptance.
6. **Never:** infer merge authorization from roadmap registration or from a passing test alone.

## 9. Acceptance checklist for the integrated system

- [ ] A skin concern does not trigger an automatic product recommendation.
- [ ] Concern, observation, hypothesis, need, product knowledge, and recommendation are distinct.
- [ ] Hypotheses are bounded, evidence-linked, and explicitly uncertain.
- [ ] Relevant ProfileFacts inform reasoning without overriding current Case answers blindly.
- [ ] Empty, unknown, conflict, and confirmed absence remain distinct.
- [ ] Next questions are selected because their answers can change the decision.
- [ ] Case answers persist with provenance; no automatic durable ProfileFact write.
- [ ] Human review can eliminate/retain hypotheses and is auditable.
- [ ] Insufficient information and professional-review paths are valid outcomes.
- [ ] Product claims, evidence, and inference remain distinct.
- [ ] Product identity, QA, evidence readiness, contraindication status, and stock gates are enforced.
- [ ] Product eligibility and customer-specific suitability remain separate.
- [ ] Recommendation rationale, exclusions, limitations, and source provenance are visible and persisted.
- [ ] Current-master tests and runtime/browser evidence support every completion claim.
- [ ] PO acceptance and merge authorization are explicit and separate.

## 10. Decision record

This roadmap consolidates prior decisions and known repository anchors to reduce omissions and prevent parallel redesign. It is a planning baseline, not a replacement for the PO-approved product-intake execution contract, not proof of current implementation, and not authorization to implement every phase. Any conflict with current repository evidence must be reported and reconciled before execution.
