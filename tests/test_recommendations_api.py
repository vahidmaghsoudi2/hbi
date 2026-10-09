"""Recommendation API tests — fixture/auth only; no production logic changes."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app as fastapi_app
from app.database import get_db
from app.models.base import Base
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.case import Case
from app.models.customer import Customer
from app.models.product_knowledge import ProductKnowledge
from app.models.evidence import Evidence
from app.models.recommendation import Recommendation  # noqa: F401
from app.models.sale import Sale  # noqa: F401
from app.models.sale_item import SaleItem  # noqa: F401
from app.models.stock_movement import StockMovement  # noqa: F401
from app.models.payment import Payment  # noqa: F401
from app.models.sale_return import SaleReturn  # noqa: F401
from app.models.category import Category  # noqa: F401
from app.services.skin_next_question_service import SkinNextQuestionService


@pytest.fixture()
def api_env():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _fk(dbapi_conn, _):
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()

    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    db = Session()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    fastapi_app.dependency_overrides[get_db] = override_get_db
    client = TestClient(fastapi_app)

    customer = Customer(
        customer_id="test_customer",
        name="Test User",
        consent_to_store_data=1,
    )
    db.add(customer)
    case = Case(case_id="test_case", customer_id="test_customer")
    db.add(case)
    db.commit()
    SkinNextQuestionService(db).capture_answer(
        case, "skin.primary_need.v1", "sun_protection"
    )
    db.commit()

    yield client, db, case

    fastapi_app.dependency_overrides.clear()
    db.close()
    Base.metadata.drop_all(bind=engine)


def _token(client: TestClient) -> str:
    response = client.post(
        "/api/v1/auth/pilot-token", json={"customer_id": "test_customer"}
    )
    assert response.status_code == 200, response.text
    token = response.json().get("access_token")
    assert token, "Token not received"
    return token


def test_draft_products_excluded(api_env):
    client, db, case = api_env

    draft = Product(
        product_id="draft_test_001",
        brand="TestBrand",
        product_name="Draft Product",
        identity_status="VERIFIED",
        qa_verdict="VALID",
        status="DRAFT",
    )
    db.add(draft)

    active = Product(
        product_id="active_test_001",
        brand="TestBrand",
        product_name="Active Product",
        identity_status="VERIFIED",
        qa_verdict="VALID",
        status="ACTIVE",
    )
    db.add(active)
    db.flush()

    db.add(ProductKnowledge(
        product_knowledge_id="PK-active_test_001",
        product_id=active.product_id,
        known_use_cases="sun protection",
        claimed_benefits="sun protection",
        contraindications="",
        ingredients="",
    ))
    db.add(Evidence(
        evidence_id="EV-active_test_001",
        product_id=active.product_id,
        source_type="INDEPENDENT",
        source_reference="TEST-SOURCE",
        claim="sun protection use case",
        claim_type="FACT",
        evidence_status="SUPPORTED",
        qa_status="APPROVED",
        conflict_status="NONE",
    ))

    inv = Inventory(
        inventory_id="inv-active_test_001",
        product_id=active.product_id,
        quantity_available=10,
        quantity_reserved=0,
        quantity_damaged=0,
        stock_status="active",
    )
    db.add(inv)
    db.commit()

    token = _token(client)
    response = client.post(
        "/api/v1/recommendations/generate",
        json={
            "case_id": case.case_id,
            "customer_profile": {"concerns": "ضدآفتاب"},
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    if isinstance(data, list):
        product_ids = [item.get("product_id") for item in data if isinstance(item, dict)]
    else:
        product_ids = [
            item.get("product_id")
            for item in data.get("recommendations", data.get("products", []))
            if isinstance(item, dict)
        ]

    assert draft.product_id not in product_ids
    assert active.product_id in product_ids


def test_inventory_zero_excluded(api_env):
    client, db, case = api_env

    zero_inv = Product(
        product_id="zero_inv_test_001",
        brand="TestBrand",
        product_name="Zero Inventory Product",
        identity_status="VERIFIED",
        qa_verdict="VALID",
        status="ACTIVE",
    )
    db.add(zero_inv)
    db.flush()

    inv_zero = Inventory(
        inventory_id="inv-zero_inv_test_001",
        product_id=zero_inv.product_id,
        quantity_available=0,
        quantity_reserved=0,
        quantity_damaged=0,
        stock_status="out_of_stock",
    )
    db.add(inv_zero)
    db.commit()

    token = _token(client)
    response = client.post(
        "/api/v1/recommendations/generate",
        json={
            "case_id": case.case_id,
            "customer_profile": {"concerns": "test"},
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    if isinstance(data, list):
        product_ids = [item.get("product_id") for item in data if isinstance(item, dict)]
    else:
        product_ids = [
            item.get("product_id")
            for item in data.get("recommendations", data.get("products", []))
            if isinstance(item, dict)
        ]

    assert zero_inv.product_id not in product_ids
    assert db.query(Recommendation).filter_by(
        case_id=case.case_id, product_id=zero_inv.product_id
    ).count() == 0, "pre-evaluation zero-stock exclusions must not create why-not records"


def test_verified_evidence_is_decision_usable(api_env):
    client, db, case = api_env

    product = Product(
        product_id="verified_evidence_test_001",
        brand="TestBrand",
        product_name="Verified Evidence Product",
        identity_status="VERIFIED",
        qa_verdict="VALID",
        status="ACTIVE",
    )
    db.add(product)
    db.flush()

    db.add(ProductKnowledge(
        product_knowledge_id="PK-verified_evidence_test_001",
        product_id=product.product_id,
        known_use_cases="sun protection",
        claimed_benefits="sun protection",
        contraindications="",
        ingredients="",
    ))
    db.add(Evidence(
        evidence_id="EV-verified_evidence_test_001",
        product_id=product.product_id,
        source_type="INDEPENDENT",
        source_reference="TEST-VERIFIED-SOURCE",
        claim="sun protection use case",
        claim_type="FACT",
        evidence_status="SUPPORTED",
        qa_status="VERIFIED",
        conflict_status="NONE",
    ))
    db.add(Inventory(
        inventory_id="inv-verified_evidence_test_001",
        product_id=product.product_id,
        quantity_available=10,
        quantity_reserved=0,
        quantity_damaged=0,
        stock_status="active",
    ))
    db.commit()

    token = _token(client)
    response = client.post(
        "/api/v1/recommendations/generate",
        json={
            "case_id": case.case_id,
            "customer_profile": {"concerns": "ضدآفتاب"},
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert product.product_id in [item["product_id"] for item in data]



def test_customer_case_read_hides_rejected_rows_and_internal_reasons(api_env):
    client, db, case = api_env
    eligible = Product(
        product_id="api_eligible_001", brand="TestBrand",
        product_name="Eligible", identity_status="VERIFIED", qa_verdict="VALID",
        status="ACTIVE",
    )
    rejected = Product(
        product_id="api_rejected_001", brand="TestBrand",
        product_name="Rejected", identity_status="VERIFIED", qa_verdict="VALID",
        status="ACTIVE",
    )
    db.add_all([eligible, rejected])
    db.flush()
    db.add_all([
        Recommendation(
            recommendation_id="rec_api_eligible_001", case_id=case.case_id,
            product_id=eligible.product_id, eligibility_status="ELIGIBLE",
            exclusion_reasons="",
        ),
        Recommendation(
            recommendation_id="rec_api_rejected_001", case_id=case.case_id,
            product_id=rejected.product_id, eligibility_status="INELIGIBLE_PENDING_REVIEW",
            exclusion_reasons='["NO_APPROVED_EVIDENCE"]',
        ),
    ])
    db.commit()

    token = _token(client)
    response = client.get(
        f"/api/v1/recommendations/case/{case.case_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert [row["product_id"] for row in payload] == [eligible.product_id]
    assert all("exclusion_reasons" not in row for row in payload)


def test_operator_case_evaluations_include_rejected_reason_and_require_role(api_env):
    client, db, case = api_env
    eligible = Product(
        product_id="api_operator_eligible_001", brand="TestBrand",
        product_name="Eligible", identity_status="VERIFIED", qa_verdict="VALID",
        status="ACTIVE",
    )
    rejected = Product(
        product_id="api_operator_rejected_001", brand="TestBrand",
        product_name="Rejected", identity_status="VERIFIED", qa_verdict="VALID",
        status="ACTIVE",
    )
    db.add_all([eligible, rejected])
    db.flush()
    db.add_all([
        Recommendation(
            recommendation_id="rec_api_operator_eligible_001", case_id=case.case_id,
            product_id=eligible.product_id, eligibility_status="ELIGIBLE",
            exclusion_reasons="",
        ),
        Recommendation(
            recommendation_id="rec_api_operator_rejected_001", case_id=case.case_id,
            product_id=rejected.product_id, eligibility_status="INELIGIBLE_PENDING_REVIEW",
            exclusion_reasons='["NO_APPROVED_EVIDENCE"]',
        ),
    ])
    db.commit()

    customer_token = _token(client)
    denied = client.get(
        f"/api/v1/recommendations/case/{case.case_id}/evaluations",
        headers={"Authorization": f"Bearer {customer_token}"},
    )
    assert denied.status_code == 403

    operator_response = client.post("/api/v1/auth/pilot-operator-token")
    assert operator_response.status_code == 200, operator_response.text
    operator_token = operator_response.json()["access_token"]
    response = client.get(
        f"/api/v1/recommendations/case/{case.case_id}/evaluations",
        headers={"Authorization": f"Bearer {operator_token}"},
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert {row["product_id"] for row in payload} == {
        eligible.product_id, rejected.product_id
    }
    rejected_row = next(row for row in payload if row["product_id"] == rejected.product_id)
    assert rejected_row["exclusion_reasons"] == ["NO_APPROVED_EVIDENCE"]
