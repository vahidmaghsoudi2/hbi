"""Mission #150 — Customer purchase history API on current master.

AuthZ: path customer_id must match token identity.
Preserves SaleItem.recommendation_id in history payload.
"""
from __future__ import annotations

from app.core.auth import create_access_token
from app.models.case import Case
from app.models.customer import Customer
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.recommendation import Recommendation
from app.services.sale_service import SaleService


def _auth(customer_id: str) -> dict:
    return {"Authorization": f"Bearer {create_access_token({'sub': customer_id})}"}


def _seed_sale_with_rec(db_session):
    db_session.add(Customer(customer_id="CUST-HIST-A", name="Owner", consent_to_store_data=1))
    db_session.add(Customer(customer_id="CUST-HIST-B", name="Other", consent_to_store_data=1))
    db_session.commit()
    db_session.add(Case(case_id="CASE-HIST-A", customer_id="CUST-HIST-A", case_type="CONSULTATION"))
    db_session.commit()
    db_session.add(
        Product(
            product_id="PROD-HIST",
            brand="B",
            product_name="Hist Product",
            identity_status="VERIFIED",
            status="ACTIVE",
            qa_verdict="VALID",
        )
    )
    db_session.commit()
    db_session.add(
        Inventory(
            inventory_id="INV-HIST",
            product_id="PROD-HIST",
            quantity_available=5,
            quantity_reserved=0,
            sale_price_usd=10.0,
            sale_price_toman=500000,
        )
    )
    db_session.commit()
    db_session.add(
        Recommendation(
            recommendation_id="REC-HIST",
            case_id="CASE-HIST-A",
            product_id="PROD-HIST",
            need_match_score=1.0,
            evidence_score=1.0,
            eligibility_status="ELIGIBLE",
            ranking_score=1.0,
            ranking_reasons="hist-test",
            evidence_refs="[]",
            warnings="[]",
        )
    )
    db_session.commit()
    sale = SaleService(db_session).create_sale(
        "CUST-HIST-A",
        [{"product_id": "PROD-HIST", "quantity": 1, "recommendation_id": "REC-HIST"}],
        fx_rate_usd_to_irr=500000.0,
    )
    db_session.commit()
    return sale


def test_history_returns_own_sales_with_recommendation_trace(client, db_session):
    sale = _seed_sale_with_rec(db_session)
    r = client.get("/api/v1/sales/customer/CUST-HIST-A", headers=_auth("CUST-HIST-A"))
    assert r.status_code == 200, r.text
    body = r.json()
    assert isinstance(body, list)
    assert len(body) == 1
    assert body[0]["sale_id"] == sale.sale_id
    assert body[0]["customer_id"] == "CUST-HIST-A"
    assert body[0]["items"][0]["product_id"] == "PROD-HIST"
    assert body[0]["items"][0]["recommendation_id"] == "REC-HIST"


def test_history_empty_for_customer_without_sales(client, db_session):
    db_session.add(Customer(customer_id="CUST-EMPTY", name="Empty", consent_to_store_data=1))
    db_session.commit()
    r = client.get("/api/v1/sales/customer/CUST-EMPTY", headers=_auth("CUST-EMPTY"))
    assert r.status_code == 200
    assert r.json() == []


def test_history_cross_customer_forbidden(client, db_session):
    _seed_sale_with_rec(db_session)
    r = client.get("/api/v1/sales/customer/CUST-HIST-A", headers=_auth("CUST-HIST-B"))
    assert r.status_code == 403
    assert "Access denied" in r.text


def test_history_unauthenticated_rejected(client, db_session):
    r = client.get("/api/v1/sales/customer/CUST-HIST-A")
    assert r.status_code in (401, 403)
