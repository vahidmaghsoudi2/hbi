"""Acceptance tests for the approved Recommendation V1 business contract."""

from app.models.case import Case
from app.models.customer import Customer
from app.models.evidence import Evidence
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.product_knowledge import ProductKnowledge
from app.models.recommendation import Recommendation
from app.services.recommendation_service import RecommendationService


def _seed_product(db_session, *, product_id, known_use_cases, quantity):
    product = Product(
        product_id=product_id,
        brand="HBI Contract Test",
        product_name=product_id,
        identity_status="VERIFIED",
        identity_confidence=1.0,
        qa_verdict="VALID",
        status="ACTIVE",
    )
    knowledge = ProductKnowledge(
        product_knowledge_id=f"PK-{product_id}",
        product_id=product_id,
        known_use_cases=known_use_cases,
        claimed_benefits="contract test support",
        evidence_status="SUPPORTED",
        knowledge_confidence=1.0,
    )
    evidence = Evidence(
        evidence_id=f"EV-{product_id}",
        product_id=product_id,
        claim_id=f"EV-{product_id}-1",
        source_type="PEER_REVIEWED",
        source_reference=f"test://{product_id}",
        claim="contract test support",
        field="claimed_benefits",
        claim_type="BENEFIT",
        evidence_strength="HIGH",
        qa_status="APPROVED",
        conflict_status="NONE",
    )
    inventory = Inventory(
        inventory_id=f"INV-{product_id}",
        product_id=product_id,
        quantity_available=quantity,
        quantity_reserved=0,
        quantity_damaged=0,
        stock_status="active",
        sale_price_usd=10.0,
    )
    db_session.add_all([product, knowledge, evidence])
    db_session.commit()
    db_session.add(inventory)
    db_session.commit()


def test_low_need_match_does_not_exclude_an_eligible_product(db_session):
    customer = Customer(customer_id="CUST-RV1-001", name="Contract Customer")
    case = Case(case_id="CASE-RV1-001", customer_id=customer.customer_id)
    db_session.add_all([customer, case])
    db_session.commit()

    # Product passes the four entry gates and has approved Evidence, but its
    # known use case does not match the customer's declared Need.
    _seed_product(
        db_session,
        product_id="PROD-RV1-LOW-MATCH",
        known_use_cases="hydration",
        quantity=10,
    )

    recs = RecommendationService(db_session).generate_recommendations(
        case.case_id,
        {"concerns": "ضدآفتاب"},
    )

    assert len(recs) == 1
    assert recs[0].eligibility_status == "ELIGIBLE"
    assert recs[0].need_match_score == 0.0


def test_inventory_quantity_does_not_change_ranking_score(db_session):
    customer = Customer(customer_id="CUST-RV1-002", name="Contract Customer")
    case = Case(case_id="CASE-RV1-002", customer_id=customer.customer_id)
    db_session.add_all([customer, case])
    db_session.commit()

    for product_id, quantity in (
        ("PROD-RV1-STOCK-1", 1),
        ("PROD-RV1-STOCK-2", 100),
    ):
        _seed_product(
            db_session,
            product_id=product_id,
            known_use_cases="sun protection",
            quantity=quantity,
        )

    recs = RecommendationService(db_session).generate_recommendations(
        case.case_id,
        {"concerns": "ضدآفتاب"},
    )

    assert len(recs) == 2
    assert {r.ranking_score for r in recs} == {1.0}
    assert {
        r.product_id for r in db_session.query(Recommendation)
        .filter_by(case_id=case.case_id)
    } == {"PROD-RV1-STOCK-1", "PROD-RV1-STOCK-2"}


def test_missing_approved_evidence_blocks_automatic_recommendation(db_session):
    customer = Customer(customer_id="CUST-RV1-003", name="Contract Customer")
    case = Case(case_id="CASE-RV1-003", customer_id=customer.customer_id)
    product = Product(
        product_id="PROD-RV1-NO-EVIDENCE",
        brand="HBI Contract Test",
        product_name="No Evidence Product",
        identity_status="VERIFIED",
        identity_confidence=1.0,
        qa_verdict="VALID",
        status="ACTIVE",
    )
    knowledge = ProductKnowledge(
        product_knowledge_id="PK-PROD-RV1-NO-EVIDENCE",
        product_id=product.product_id,
        known_use_cases="sun protection",
        claimed_benefits="contract test",
        evidence_status="SUPPORTED",
        knowledge_confidence=1.0,
    )
    inventory = Inventory(
        inventory_id="INV-PROD-RV1-NO-EVIDENCE",
        product_id=product.product_id,
        quantity_available=10,
        quantity_reserved=0,
        quantity_damaged=0,
        stock_status="active",
        sale_price_usd=10.0,
    )
    db_session.add_all([customer, case, product, knowledge])
    db_session.commit()
    db_session.add(inventory)
    db_session.commit()

    recs = RecommendationService(db_session).generate_recommendations(
        case.case_id,
        {"concerns": "ضدآفتاب"},
    )

    assert recs == []
