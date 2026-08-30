import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.case import Case
from app.models.customer import Customer
from app.database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

def get_token():
    response = client.post("/api/v1/auth/pilot-token", json={"customer_id": "test_customer"})
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

@pytest.fixture(scope="module")
def setup_data(db_session):
    customer = Customer(customer_id="test_customer", name="Test User", consent_to_store_data=True)
    db_session.add(customer)
    db_session.commit()

    case = Case(case_id="test_case", customer_id="test_customer")
    db_session.add(case)
    db_session.commit()

    return customer, case

def test_draft_products_excluded(db_session, setup_data):
    _, case = setup_data

    draft = Product(
        product_id="draft_test_001",
        brand="TestBrand",
        product_name="Draft Product",
        identity_status="VERIFIED",
        qa_verdict="VALID",
        status="DRAFT"
    )
    db_session.add(draft)
    db_session.commit()

    active = Product(
        product_id="active_test_001",
        brand="TestBrand",
        product_name="Active Product",
        identity_status="VERIFIED",
        qa_verdict="VALID",
        status="ACTIVE"
    )
    db_session.add(active)
    db_session.commit()

    inv = Inventory(
        product_id=active.product_id,
        quantity_available=10,
        quantity_reserved=0,
        quantity_damaged=0,
        stock_status="active"
    )
    db_session.add(inv)
    db_session.commit()

    token = get_token()
    assert token, "Token not received"

    response = client.post(
        "/api/v1/recommendations/generate",
        json={"case_id": case.case_id},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    
    if isinstance(data, list):
        product_ids = [item.get("product_id") for item in data if isinstance(item, dict)]
    else:
        product_ids = [item.get("product_id") for item in data.get("recommendations", data.get("products", [])) if isinstance(item, dict)]

    assert draft.product_id not in product_ids
    assert active.product_id in product_ids

def test_inventory_zero_excluded(db_session, setup_data):
    _, case = setup_data

    zero_inv = Product(
        product_id="zero_inv_test_001",
        brand="TestBrand",
        product_name="Zero Inventory Product",
        identity_status="VERIFIED",
        qa_verdict="VALID",
        status="ACTIVE"
    )
    db_session.add(zero_inv)
    db_session.commit()

    inv_zero = Inventory(
        product_id=zero_inv.product_id,
        quantity_available=0,
        quantity_reserved=0,
        quantity_damaged=0,
        stock_status="out_of_stock"
    )
    db_session.add(inv_zero)
    db_session.commit()

    token = get_token()
    assert token

    response = client.post(
        "/api/v1/recommendations/generate",
        json={"case_id": case.case_id},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    
    if isinstance(data, list):
        product_ids = [item.get("product_id") for item in data if isinstance(item, dict)]
    else:
        product_ids = [item.get("product_id") for item in data.get("recommendations", data.get("products", [])) if isinstance(item, dict)]

    assert zero_inv.product_id not in product_ids
