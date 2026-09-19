"""HBI-CUST-HISTORY-FOLLOWUP-001 — customer purchase history + rec trace."""

from app.models.case import Case
from app.models.customer import Customer
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.recommendation import Recommendation
from app.services.sale_service import SaleService
from app.interface.facades import SaleFacade


def _seed(db):
    db.add(Customer(customer_id="CUST-H", name="Hist", consent_to_store_data=1))
    db.commit()
    db.add(Case(case_id="CASE-H", customer_id="CUST-H", case_type="CONSULTATION"))
    db.commit()
    db.add(
        Product(
            product_id="PROD-H",
            brand="B",
            product_name="P",
            identity_status="VERIFIED",
            status="ACTIVE",
            qa_verdict="VALID",
        )
    )
    db.commit()
    db.add(
        Inventory(
            inventory_id="INV-H",
            product_id="PROD-H",
            quantity_available=5,
            quantity_reserved=0,
            sale_price_usd=10.0,
            sale_price_toman=500000,
        )
    )
    db.commit()
    db.add(
        Recommendation(
            recommendation_id="REC-H",
            case_id="CASE-H",
            product_id="PROD-H",
            eligibility_status="ELIGIBLE",
            need_match_score=1.0,
            evidence_score=1.0,
            ranking_score=1.0,
        )
    )
    db.commit()


def test_history_includes_sale_items_and_recommendation_trace(db_session):
    _seed(db_session)
    SaleService(db_session).create_sale(
        "CUST-H",
        [{"product_id": "PROD-H", "quantity": 1, "recommendation_id": "REC-H"}],
        fx_rate_usd_to_irr=500000.0,
    )
    db_session.commit()
    hist = SaleFacade(db_session).find_by_customer("CUST-H")
    assert len(hist) == 1
    assert hist[0].customer_id == "CUST-H"
    assert hist[0].items and hist[0].items[0].product_id == "PROD-H"
    assert hist[0].items[0].recommendation_id == "REC-H"


def test_history_empty_for_customer_without_sales(db_session):
    db_session.add(Customer(customer_id="CUST-EMPTY", name="E", consent_to_store_data=1))
    db_session.commit()
    assert SaleFacade(db_session).find_by_customer("CUST-EMPTY") == []


def test_history_does_not_leak_other_customer_sales(db_session):
    _seed(db_session)
    db_session.add(Customer(customer_id="CUST-OTHER", name="O", consent_to_store_data=1))
    db_session.commit()
    SaleService(db_session).create_sale(
        "CUST-H",
        [{"product_id": "PROD-H", "quantity": 1, "recommendation_id": "REC-H"}],
        fx_rate_usd_to_irr=500000.0,
    )
    db_session.commit()
    assert SaleFacade(db_session).find_by_customer("CUST-OTHER") == []
    assert len(SaleFacade(db_session).find_by_customer("CUST-H")) == 1
