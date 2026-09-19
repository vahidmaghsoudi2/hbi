"""HBI-REC-SALE-TRACE-001 — Recommendation to Sale traceability tests."""

from app.models.case import Case
from app.models.customer import Customer
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.recommendation import Recommendation
from app.models.sale_item import SaleItem
from app.services.sale_service import SaleService


def _setup(db_session):
    customer = Customer(customer_id="CUST-TRACE", name="Trace User", consent_to_store_data=1)
    case = Case(case_id="CASE-TRACE", customer_id="CUST-TRACE", case_type="CONSULTATION")
    product = Product(
        product_id="PROD-TRACE",
        brand="Brand",
        product_name="Trace Product",
        identity_status="VERIFIED",
        status="ACTIVE",
        qa_verdict="VALID",
    )
    inventory = Inventory(
        inventory_id="INV-TRACE",
        product_id="PROD-TRACE",
        quantity_available=5,
        quantity_reserved=0,
        sale_price_usd=10.0,
        sale_price_toman=500000,
    )
    recommendation = Recommendation(
        recommendation_id="REC-TRACE",
        case_id="CASE-TRACE",
        product_id="PROD-TRACE",
        need_match_score=1.0,
        evidence_score=1.0,
        eligibility_status="ELIGIBLE",
        ranking_score=1.0,
        ranking_reasons="trace-test",
        evidence_refs="[]",
        warnings="[]",
    )
    # Explicit parent-first commits: under PRAGMA foreign_keys=ON, a single
    # add_all/flush can insert Inventory before Product and fail FK.
    db_session.add(customer)
    db_session.commit()
    db_session.add(case)
    db_session.commit()
    db_session.add(product)
    db_session.commit()
    db_session.add(inventory)
    db_session.commit()
    db_session.add(recommendation)
    db_session.commit()
    return customer, case, product, inventory, recommendation


def test_recommendation_sale_trace_persists_and_retrieves(db_session):
    _, _, _, _, recommendation = _setup(db_session)

    sale = SaleService(db_session).create_sale(
        "CUST-TRACE",
        [{"product_id": "PROD-TRACE", "quantity": 1, "recommendation_id": recommendation.recommendation_id}],
        fx_rate_usd_to_irr=500000.0,
    )
    db_session.commit()

    item = db_session.query(SaleItem).filter(SaleItem.sale_id == sale.sale_id).one()
    assert item.product_id == recommendation.product_id
    assert item.recommendation_id == recommendation.recommendation_id

    retrieved = SaleService(db_session).find_with_items(sale.sale_id)
    assert retrieved.sale_items[0].recommendation_id == recommendation.recommendation_id


def test_recommendation_customer_ownership_is_enforced(db_session):
    _, case, product, inventory, recommendation = _setup(db_session)
    other = Customer(customer_id="CUST-OTHER", name="Other User", consent_to_store_data=1)
    db_session.add(other)
    db_session.commit()

    try:
        SaleService(db_session).create_sale(
            "CUST-OTHER",
            [{"product_id": product.product_id, "quantity": 1, "recommendation_id": recommendation.recommendation_id}],
            fx_rate_usd_to_irr=500000.0,
        )
        assert False, "cross-customer recommendation must be rejected"
    except ValueError as exc:
        assert "does not belong" in str(exc)


def test_recommendation_product_consistency_is_enforced(db_session):
    _, _, product, _, recommendation = _setup(db_session)
    other_product = Product(
        product_id="PROD-OTHER",
        brand="Brand",
        product_name="Other Product",
        identity_status="VERIFIED",
        status="ACTIVE",
        qa_verdict="VALID",
    )
    other_inventory = Inventory(
        inventory_id="INV-OTHER",
        product_id="PROD-OTHER",
        quantity_available=2,
        sale_price_usd=10.0,
    )
    db_session.add(other_product)
    db_session.commit()
    db_session.add(other_inventory)
    db_session.commit()

    try:
        SaleService(db_session).create_sale(
            "CUST-TRACE",
            [{"product_id": other_product.product_id, "quantity": 1, "recommendation_id": recommendation.recommendation_id}],
            fx_rate_usd_to_irr=500000.0,
        )
        assert False, "recommendation/product mismatch must be rejected"
    except ValueError as exc:
        assert "does not match sale product" in str(exc)


def test_legacy_unlinked_sale_remains_valid(db_session):
    _setup(db_session)
    sale = SaleService(db_session).create_sale(
        "CUST-TRACE",
        [{"product_id": "PROD-TRACE", "quantity": 1}],
        fx_rate_usd_to_irr=500000.0,
    )
    db_session.commit()
    item = db_session.query(SaleItem).filter(SaleItem.sale_id == sale.sale_id).one()
    assert item.recommendation_id is None


def test_non_eligible_recommendation_cannot_be_linked_to_sale(db_session):
    _, _, _, _, recommendation = _setup(db_session)
    # Must use a value allowed by Recommendation CHECK constraint
    recommendation.eligibility_status = "INELIGIBLE_PENDING_REVIEW"
    db_session.commit()

    try:
        SaleService(db_session).create_sale(
            "CUST-TRACE",
            [{"product_id": "PROD-TRACE", "quantity": 1, "recommendation_id": recommendation.recommendation_id}],
            fx_rate_usd_to_irr=500000.0,
        )
        assert False, "non-ELIGIBLE recommendation must be rejected"
    except ValueError as exc:
        assert "Only an ELIGIBLE recommendation" in str(exc)
