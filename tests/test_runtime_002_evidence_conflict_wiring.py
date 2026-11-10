"""HBI-RUNTIME-002 — Evidence.conflict_status propagation into Recommendation path."""
import json
from types import SimpleNamespace

from app.models.case import Case
from app.models.customer import Customer
from app.models.evidence import Evidence
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.product_knowledge import ProductKnowledge
from app.models.recommendation import Recommendation
from app.reasoning.reasoning_engine import ReasoningEngine
from app.services.recommendation_service import RecommendationService


def test_engine_receives_and_analyzes_existing_conflicts():
    engine = ReasoningEngine()
    result = engine.run(
        product_id="p1",
        evidence_list=[{
            "evidence_id": "e1",
            "field": "safety",
            "claim": "claim A",
            "claim_type": "FACT",
            "conflict_status": "CONFLICT",
            "source_reference": "src",
            "source_type": "PEER_REVIEWED",
        }],
        existing_conflicts=[{
            "field": "safety",
            "conflicting_values": ["claim A", "claim B"],
            "evidence_refs": ["e1"],
            "sources": ["src"],
        }],
        need_match=0.9,
        evidence_score=0.8,
        inventory_score=1.0,
    )
    assert len(result.get("conflicts") or []) >= 1
    assert result.get("eligibility") != "ELIGIBLE"


def test_no_conflict_keeps_eligible_when_scores_ok():
    engine = ReasoningEngine()
    result = engine.run(
        product_id="p1",
        evidence_list=[{
            "evidence_id": "e1",
            "field": "texture",
            "claim": "smooth",
            "claim_type": "FACT",
            "conflict_status": "NONE",
            "source_reference": "src",
            "source_type": "PEER_REVIEWED",
        }],
        existing_conflicts=[],
        need_match=0.9,
        evidence_score=0.8,
        inventory_score=1.0,
    )
    assert result.get("conflicts") == []
    assert result.get("eligibility") == "ELIGIBLE"


def test_existing_conflicts_from_evidence_helper():
    svc = RecommendationService.__new__(RecommendationService)
    evidences = [
        SimpleNamespace(
            evidence_id="e1", field="safety", claim="A",
            conflict_status="CONFLICT", source_reference="s1",
        ),
        SimpleNamespace(
            evidence_id="e2", field="texture", claim="B",
            conflict_status="NONE", source_reference="s2",
        ),
        SimpleNamespace(
            evidence_id="e3", field="allergy", claim="C",
            conflict_status="CONFLICT", source_reference="s3",
        ),
    ]
    out = svc._existing_conflicts_from_evidence(evidences, "prod-1")
    assert len(out) == 2
    fields = {c["field"] for c in out}
    assert fields == {"safety", "allergy"}
    assert all(c["product_id"] == "prod-1" for c in out)


def test_map_eligibility_with_engine_needs_review_from_conflict():
    svc = RecommendationService.__new__(RecommendationService)
    decision_state = {"unknowns": [], "needs": ["hydration"], "medical_context_active": False}
    engine_result = {
        "eligibility": "NEEDS_REVIEW",
        "conflicts": [{"field": "safety", "severity": "CRITICAL"}],
        "unknowns": [],
    }
    elig = svc._map_eligibility(engine_result, decision_state, need_match=0.9, product_unknowns=[])
    assert elig == "INELIGIBLE_PENDING_REVIEW"


def test_case_unknowns_not_mutated_by_product_conflicts():
    """GAP-01: product conflicts must not write into shared Case Decision State unknowns."""
    svc = RecommendationService.__new__(RecommendationService)
    decision_state = {
        "unknowns": [],
        "needs": ["hydration"],
        "medical_context_active": False,
        "factors": [{"value": "hydration", "source": "customer_input", "validity": "DECLARED"}],
    }
    before = list(decision_state["unknowns"])
    engine_result = {
        "eligibility": "NEEDS_REVIEW",
        "conflicts": [{"field": "safety", "severity": "CRITICAL"}],
        "unknowns": [{"field": "safety", "severity": "CRITICAL"}],
    }
    _ = svc._map_eligibility(engine_result, decision_state, need_match=0.9, product_unknowns=[])
    assert decision_state["unknowns"] == before



def test_recommendation_service_persists_review_gate_for_ingredient_conflict(db_session):
    """LOW-severity ingredient conflicts still require review in the persisted service result."""
    customer_id = "C-RUNTIME-002-CONFLICT"
    case_id = "CASE-RUNTIME-002-CONFLICT"
    product_id = "P-RUNTIME-002-CONFLICT"

    db_session.add(Customer(
        customer_id=customer_id,
        name="Runtime conflict fixture",
        consent_to_store_data=1,
    ))
    db_session.add(Case(
        case_id=case_id,
        customer_id=customer_id,
        case_type="SKIN",
        evidence_gaps=json.dumps({
            "answers": [{
                "question_id": "skin.primary_need.v2",
                "factor": "concerns",
                "source": "CURRENT_CASE_CONSULTATION",
                "value_state": "KNOWN",
                "value": ["hydration"],
            }]
        }),
    ))
    db_session.add(Product(
        product_id=product_id,
        brand="TestBrand",
        product_name="Ingredient conflict fixture",
        product_line="SKIN",
        identity_status="VERIFIED",
        qa_verdict="VALID",
        status="ACTIVE",
    ))
    db_session.add(ProductKnowledge(
        product_knowledge_id="PK-RUNTIME-002-CONFLICT",
        product_id=product_id,
        known_use_cases="hydration",
        evidence_status="SUPPORTED",
        knowledge_confidence=0.8,
    ))
    db_session.add(Inventory(
        inventory_id="INV-RUNTIME-002-CONFLICT",
        product_id=product_id,
        quantity_available=2,
        quantity_reserved=0,
        quantity_damaged=0,
        stock_status="AVAILABLE",
    ))
    db_session.add_all([
        Evidence(
            evidence_id="EV-RUNTIME-002-INGREDIENT-A",
            product_id=product_id,
            claim_id="CL-RUNTIME-002-INGREDIENT-A",
            source_type="MANUFACTURER",
            source_reference="https://manufacturer.example/ingredient-a",
            claim="The formula contains ingredient A.",
            field="ingredients",
            claim_type="MANUFACTURER_CLAIM",
            evidence_strength="UNVERIFIED",
            evidence_status="UNKNOWN",
            conflict_status="CONFLICT",
            qa_status="VERIFIED",
        ),
        Evidence(
            evidence_id="EV-RUNTIME-002-INGREDIENT-B",
            product_id=product_id,
            claim_id="CL-RUNTIME-002-INGREDIENT-B",
            source_type="MANUFACTURER",
            source_reference="https://manufacturer.example/ingredient-b",
            claim="The formula contains ingredient B.",
            field="ingredients",
            claim_type="MANUFACTURER_CLAIM",
            evidence_strength="UNVERIFIED",
            evidence_status="UNKNOWN",
            conflict_status="CONFLICT",
            qa_status="VERIFIED",
        ),
        Evidence(
            evidence_id="EV-RUNTIME-002-APPROVED",
            product_id=product_id,
            claim_id="CL-RUNTIME-002-APPROVED",
            source_type="MANUFACTURER",
            source_reference="https://manufacturer.example/usage",
            claim="Use after cleansing.",
            field="usage_instructions",
            claim_type="MANUFACTURER_CLAIM",
            evidence_strength="STRONG",
            evidence_status="SUPPORTED",
            conflict_status="NONE",
            qa_status="VERIFIED",
        ),
    ])
    db_session.commit()

    generated = RecommendationService(db_session).generate_recommendations(
        case_id,
        {"concerns": "hydration"},
    )

    assert generated == []
    persisted = db_session.query(Recommendation).filter_by(
        case_id=case_id,
        product_id=product_id,
    ).one()
    assert persisted.eligibility_status == "INELIGIBLE_PENDING_REVIEW"
    assert json.loads(persisted.exclusion_reasons) == [
        "EVIDENCE_CONFLICT_REVIEW_REQUIRED"
    ]
    assert persisted.evidence_score > 0
    assert "product_conflicts=2" in persisted.ranking_reasons
