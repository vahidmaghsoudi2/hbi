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

@pytest.fixture(scope="module")
def setup_data(db_session):
    # Customer با فیلدهای اجباری
    customer = Customer(
        customer_id="test_customer",
        name="Test User",
        consent_to_store_data=True
    )
    db_session.add(customer)
    db_session.commit()

    # Case
    case = Case(
        case_id="test_case",
        customer_id="test_customer"
    )
    db_session.add(case)
    db_session.commit()

    # یک محصول ACTIVE با موجودی مثبت (برای تست‌های بعدی)
    active_product = Product(
        product_id="active_test_001",
        brand="TestBrand",
        product_name="Active Product",
        identity_status="VERIFIED",
        qa_verdict="VALID",
        status="ACTIVE"
    )
    db_session.add(active_product)
    db_session.commit()

    # موجودی برای محصول فعال
    inventory = Inventory(
        product_id=active_product.product_id,
        quantity_available=10,
        quantity_reserved=0,
        quantity_damaged=0,
        stock_status="active"
    )
    db_session.add(inventory)
    db_session.commit()

    return customer, case

def get_pilot_token():
    response = client.post("/api/v1/auth/pilot-token", json={"customer_id": "test_customer"})
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

@pytest.fixture(scope="module")
def auth_headers():
    token = get_pilot_token()
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

def test_generate_owned_case_returns_list(db_session, setup_data, auth_headers):
    _, case = setup_data
    assert auth_headers, "Pilot token could not be obtained"
    response = client.post(
        "/api/v1/recommendations/generate",
        json={"case_id": case.case_id},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)

def test_draft_products_excluded(db_session, setup_data, auth_headers):
    _, case = setup_data
    assert auth_headers, "Pilot token could not be obtained"

    # فقط محصول DRAFT بساز — نیازی به Inventory نیست
    draft_product = Product(
        product_id="draft_test_001",
        brand="TestBrand",
        product_name="Draft Product",
        identity_status="VERIFIED",
        qa_verdict="VALID",
        status="DRAFT"
    )
    db_session.add(draft_product)
    db_session.commit()

    # یک محصول ACTIVE دیگر با موجودی
    active_product2 = Product(
        product_id="active_test_002",
        brand="TestBrand",
        product_name="Active Product 2",
        identity_status="VERIFIED",
        qa_verdict="VALID",
        status="ACTIVE"
    )
    db_session.add(active_product2)
    db_session.commit()

    inventory2 = Inventory(
        product_id=active_product2.product_id,
        quantity_available=5,
        quantity_reserved=0,
        quantity_damaged=0,
        stock_status="active"
    )
    db_session.add(inventory2)
    db_session.commit()

    response = client.post(
        "/api/v1/recommendations/generate",
        json={"case_id": case.case_id},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    product_ids = [item["product_id"] for item in data["recommendations"]]

    assert draft_product.product_id not in product_ids
    assert active_product2.product_id in product_ids
    assert "active_test_001" in product_ids

def test_inventory_zero_excluded(db_session, setup_data, auth_headers):
    _, case = setup_data
    assert auth_headers, "Pilot token could not be obtained"

    # محصول با موجودی صفر
    zero_inv_product = Product(
        product_id="zero_inv_test_001",
        brand="TestBrand",
        product_name="Zero Inventory Product",
        identity_status="VERIFIED",
        qa_verdict="VALID",
        status="ACTIVE"
    )
    db_session.add(zero_inv_product)
    db_session.commit()

    # موجودی صفر — inventory_id توسط مدل خودکار مقداردهی می‌شود
    zero_inventory = Inventory(
        product_id=zero_inv_product.product_id,
        quantity_available=0,
        quantity_reserved=0,
        quantity_damaged=0,
        stock_status="out_of_stock"
    )
    db_session.add(zero_inventory)
    db_session.commit()

    response = client.post(
        "/api/v1/recommendations/generate",
        json={"case_id": case.case_id},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    product_ids = [item["product_id"] for item in data["recommendations"]]

    assert zero_inv_product.product_id not in product_ids
    assert "active_test_001" in product_ids
    assert "active_test_002" in product_ids
