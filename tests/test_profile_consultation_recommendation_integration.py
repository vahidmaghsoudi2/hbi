"""Integration reality test: persistent customer profile + today's consultation -> recommendation.

This test exercises the same backend integration seam used by Home:
Customer/Case ownership -> recommendation endpoint -> profile merge -> RecommendationService
-> product eligibility/evidence/inventory gates -> persisted eligible recommendation.
"""
from app.api.routers.recommendations import RecommendationRequest, generate_recommendations
from app.models.case import Case
from app.models.customer import Customer
from app.models.evidence import Evidence
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.product_knowledge import ProductKnowledge
from app.models.recommendation import Recommendation


def test_persistent_profile_plus_current_consultation_reaches_recommendation(db_session):
    customer = Customer(
        customer_id="CUST_E2E_001",
        name="Integration Customer",
        mobile="09120000001",
        concerns="خشکی",
        skin_profile="پوست خشک",
    )
    case = Case(
        case_id="CASE_E2E_001",
        customer_id=customer.customer_id,
        case_type="OPEN",
    )
    product = Product(
        product_id="PROD_E2E_HYDRATION",
        brand="HBI Test",
        product_name="Hydration Test Product",
        identity_status="VERIFIED",
        identity_confidence=1.0,
        qa_verdict="VALID",
        status="ACTIVE",
    )
    knowledge = ProductKnowledge(
        product_knowledge_id="PK_E2E_HYDRATION",
        product_id=product.product_id,
        known_use_cases="hydration",
        claimed_benefits="supports skin hydration",
        evidence_status="SUPPORTED",
        knowledge_confidence=1.0,
    )
    evidence = Evidence(
        evidence_id="EV_E2E_HYDRATION",
        product_id=product.product_id,
        claim_id="EV-PROD_E2E_HYDRATION-1",
        source_type="PEER_REVIEWED",
        source_reference="test://approved-evidence",
        claim="supports skin hydration",
        field="claimed_benefits",
        claim_type="BENEFIT",
        evidence_strength="HIGH",
        qa_status="APPROVED",
    )
    inventory = Inventory(
        inventory_id="INV_E2E_HYDRATION",
        product_id=product.product_id,
        quantity_available=10,
        quantity_reserved=0,
        quantity_damaged=0,
        stock_status="active",
        sale_price_usd=10.0,
    )
    db_session.add_all([customer, case, product, knowledge, evidence, inventory])
    db_session.commit()

    # Today's problem is new: it must be combined with the saved profile,
    # without requiring the saved customer.concerns field to be overwritten.
    current_consultation = {
        "concerns": "آبرسان",
        "skin_profile": "پوست حساس",
    }
    result = generate_recommendations(
        RecommendationRequest(
            case_id=case.case_id,
            customer_profile=current_consultation,
        ),
        db_session,
        customer.customer_id,
    )

    assert len(result) == 1
    dto = result[0]
    assert dto["product_id"] == product.product_id
    assert dto["eligibility_status"] == "ELIGIBLE"
    assert dto["need_match_score"] == 1.0
    assert dto["evidence_score"] == 1.0
    assert dto["availability"] == 10

    # Persistent profile remains historical data; today's consultation was
    # used as recommendation context rather than overwriting the profile.
    persisted_customer = db_session.get(Customer, customer.customer_id)
    assert persisted_customer.concerns == "خشکی"
    assert persisted_customer.skin_profile == "پوست خشک"

    persisted_recommendation = db_session.query(Recommendation).filter_by(
        case_id=case.case_id,
        product_id=product.product_id,
    ).one()
    assert persisted_recommendation.eligibility_status == "ELIGIBLE"
    assert "hydration" not in (persisted_recommendation.ranking_reasons or "") or "needs=" in persisted_recommendation.ranking_reasons
    assert "Evidence items considered: 1" in persisted_recommendation.ranking_reasons
