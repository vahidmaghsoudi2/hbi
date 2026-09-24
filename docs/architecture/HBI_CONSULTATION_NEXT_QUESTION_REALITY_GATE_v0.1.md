# HBI Consultation Next Question / Progressive Profiling — Reality Gate v0.1

**Issue:** #223  
**Baseline Master:** `d1895be588de510c04471232dc7a89350749c60f`  
**Scope:** Reality audit only. No production behavior change.

## Executive finding

The current Master has **decision-state unknown/conflict awareness and ProfileFact context traceability**, but it does **not** have a dedicated Evidence Gap → Next Question / Action mechanism or decision-value-driven Progressive Profiling selector.

The strongest current boundary is:

`ProfileFact/current consultation → context projection → existing recommendation`

The next layer is therefore **not yet implemented**.

## Reality matrix

| Capability | Runtime reality | Evidence | Status | Gap |
|---|---|---|---|---|
| Case evidence_gaps field | `Case.evidence_gaps` exists as nullable String | `app/models/case.py` | VERIFIED EXISTING | No verified writer/lifecycle |
| Evidence Gap generation | Recommendation decision state initializes `evidence_gaps=[]`; no Case persistence occurs | `app/services/recommendation_service.py::_build_decision_state` | PARTIAL | Computed state is not a durable Case Evidence Gap |
| Evidence Gap persistence | No write path verified in the audited recommendation flow | Case model + RecommendationService | NOT VERIFIED | Durable contract/writer absent |
| Evidence Gap API | Generate returns recommendation DTO list; no dedicated Evidence Gap payload is constructed | `app/api/routers/recommendations.py` | NOT VERIFIED | No stable API-first-class gap response |
| Next Question | No selector/generator/persistence mechanism verified | audited consultation/recommendation path | MISSING | Need decision-value-driven mechanism |
| Next Action | Existing reasoning can emit product/evidence actions such as review/escalation, but this is product-side reasoning, not customer-question selection | `app/reasoning/reasoning_engine.py` | PARTIAL | No consultation Next Action contract |
| Progressive Profiling | Current input overrides ProfileFact; ProfileFact can override legacy Customer; no mechanism chooses questions based on expected decision change | `ProfileFactContextService` + recommendation flow | PARTIAL | Decision-value question selection absent |
| Unknown-family ProfileFact | UNKNOWN/PREFER_NOT_TO_SAY/NOT_APPLICABLE preserved in trace and not converted to invented values | `ProfileFactContextService.build` | VERIFIED EXISTING | No clarification action |
| Duplicate ACTIVE ProfileFact | Multiple ACTIVE facts become explicit CONFLICTED projection; no arbitrary selection | `ProfileFactContextService.build` | VERIFIED EXISTING | Conflict does not generate a next question |
| Recommendation effect of ProfileFact conflict | Conflict is carried into decision state; existing recommendation hard gates product-side HIGH/CRITICAL conflicts, while ProfileFact projection conflict itself does not become a customer question | Context + RecommendationService | PARTIAL | Clarification boundary absent |
| ProfileFact provenance | Trace retains source, fact id, value state, provenance | `ProfileFactContextService` | VERIFIED EXISTING | No question-selection use yet |
| Current consultation precedence | Current consultation → ACTIVE ProfileFact → legacy Customer | `ProfileFactContextService.build` | VERIFIED EXISTING | No need to change |
| Recommendation scoring/ranking | Existing formula/path remains in RecommendationService/ReasoningEngine | `RecommendationService`, `ReasoningEngine` | VERIFIED EXISTING | Next-question layer should remain additive |

## Actual current runtime path

```
Authenticated Customer
        ↓
Owned Case
        ↓
current customer_profile
        +
ACTIVE ProfileFact
        +
legacy Customer
        ↓
ProfileFactContextService.build()
        ↓
profile + _profile_fact_context
        ↓
RecommendationFacade
        ↓
RecommendationService.generate_recommendations()
        ↓
factors → canonical Needs
        ↓
existing eligibility / scoring / ranking
        ↓
Recommendation DTO
        ↓
ranking_reasons contains profile_fact trace
```

There is currently no verified branch:

`Evidence Gap → Next Question`

## Evidence Gap reality

`Case.evidence_gaps` is a storage field, but the audited generation path creates an **in-memory** `decision_state["evidence_gaps"] = []`. No verified writer was found that turns consultation uncertainty into a durable Case evidence-gap record.

The existing ReasoningEngine's `unknowns` are also **computed only** and explicitly have `persistence="COMPUTED_ONLY"`. Its `action` values (for example escalation/logging) concern product evidence reasoning; they are not a customer-facing consultation question selector.

Therefore:

**Concept exists → partial runtime signals exist → durable cross-layer Evidence Gap contract is not implemented.**

## Next Question reality

No dedicated model, service, endpoint, or selection algorithm was verified for:

- identifying candidate customer questions,
- estimating whether an answer can change the current decision,
- ranking candidate questions by decision value,
- returning a Next Question / Action to the consultation client,
- persisting the answer as either Case context or durable ProfileFact.

The current system can surface unknown/conflict information in reasoning/context traces, but it stops short of converting that information into an interactive clarification step.

## Progressive Profiling reality

The architectural principle is present, and the current context boundary provides the essential inputs:

1. current consultation value,
2. durable ACTIVE ProfileFact,
3. legacy Customer fallback,
4. UNKNOWN-family state,
5. explicit ProfileFact conflict,
6. provenance and fact IDs,
7. existing recommendation result.

What is missing is the **decision-value function**:

`Question → possible answer states → change in decision → ask/defer`

No runtime mechanism currently proves this calculation.

## Smallest next Vertical Slice

The smallest evidence-bound implementation should **not** build a general Questionnaire Engine.

Proposed slice:

```
Owned Case
   ↓
Current consultation + ProfileFact context
   ↓
Existing decision state / recommendation attempt
   ↓
Detect ONE bounded missing decision input
   ↓
Return ONE structured Next Question / Action
   ↓
Answer remains Case/current-consultation context
   ↓
Re-run existing recommendation
```

Start with one concrete Skin consultation decision factor where the existing recommendation path can demonstrate that different answers materially change the decision.

Acceptance should prove:

- missing factor is detected,
- exactly the bounded question is produced,
- known information is not redundantly requested,
- current consultation still has precedence,
- ProfileFact remains durable-only unless explicitly saved,
- UNKNOWN/Conflict can trigger clarification,
- answer changes/repeats the existing recommendation path,
- Recommendation scoring/eligibility/ranking formula remains unchanged.

This slice should receive a **separate implementation authorization** after this Reality Gate.

## Explicit boundaries

No evidence was found that justifies introducing:

- a general Questionnaire Engine,
- a new Question/Answer database hierarchy,
- a new DecisionContext entity,
- AI-generated questions,
- vector/ontology infrastructure,
- recommendation scoring changes,
- automatic ProfileFact writes.

## Final decision

**REALITY GATE RESULT: ACCEPTED AS AUDIT / IMPLEMENTATION NOT AUTHORIZED**

The next real architectural boundary is now clear:

**Evidence Gap → bounded Next Question / Action → re-run existing decision path**

Progressive Profiling should be implemented only through that narrow vertical slice, after explicit authorization.
