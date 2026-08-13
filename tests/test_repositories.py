import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.product import Product
from app.models.customer import Customer
from app.models.case import Case
from app.models.recommendation import Recommendation
from app.models.inventory import Inventory
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.repositories import (
    ProductRepository,
    CustomerRepository,
    CaseRepository,
    RecommendationRepository,
    InventoryRepository,
    SaleRepository,
    SaleItemRepository,
)

# ایجاد engine و فعال‌سازی foreign_keys
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture
def sample_product(db):
    repo = ProductRepository(db)
    product = repo.create(
        product_id="P001",
        brand="TestBrand",
        product_name="Test Product",
        identity_status="VERIFIED",
        qa_verdict="VALID"
    )
    return product

@pytest.fixture
def sample_customer(db):
    repo = CustomerRepository(db)
    customer = repo.create(
        customer_id="C001",
        name="Test Customer",
        consent_to_store_data=1
    )
    return customer

def test_product_repository_create(db):
    repo = ProductRepository(db)
    product = repo.create(
        product_id="P002",
        brand="BrandX",
        product_name="ProductX",
        identity_status="VERIFIED",
        qa_verdict="VALID"
    )
    assert product.product_id == "P002"
    assert repo.count() == 1

def test_product_repository_get_by_id(db, sample_product):
    repo = ProductRepository(db)
    product = repo.get_by_id("P001")
    assert product is not None
    assert product.product_name == "Test Product"

def test_product_repository_update(db, sample_product):
    repo = ProductRepository(db)
    updated = repo.update("P001", product_name="Updated Product")
    assert updated is not None
    assert updated.product_name == "Updated Product"

def test_product_repository_delete(db, sample_product):
    repo = ProductRepository(db)
    assert repo.delete("P001") is True
    assert repo.get_by_id("P001") is None

def test_product_repository_find_by_brand(db, sample_product):
    repo = ProductRepository(db)
    products = repo.find_by_brand("TestBrand")
    assert len(products) == 1

def test_customer_repository_create(db):
    repo = CustomerRepository(db)
    customer = repo.create(
        customer_id="C002",
        name="CustomerX",
        consent_to_store_data=1
    )
    assert customer.customer_id == "C002"

def test_customer_repository_find_by_mobile(db):
    repo = CustomerRepository(db)
    customer = repo.create(
        customer_id="C003",
        name="CustomerY",
        mobile="09121234567",
        consent_to_store_data=1
    )
    found = repo.find_by_mobile("09121234567")
    assert found is not None
    assert found.name == "CustomerY"

def test_case_repository_create(db, sample_customer):
    repo = CaseRepository(db)
    case = repo.create(
        case_id="CA001",
        customer_id=sample_customer.customer_id,
        case_type="OPEN"
    )
    assert case.case_id == "CA001"

def test_case_repository_find_by_customer(db, sample_customer):
    repo = CaseRepository(db)
    repo.create(case_id="CA002", customer_id=sample_customer.customer_id, case_type="OPEN")
    cases = repo.find_by_customer(sample_customer.customer_id)
    assert len(cases) == 1

def test_recommendation_repository_create(db, sample_product, sample_customer):
    case_repo = CaseRepository(db)
    case = case_repo.create(case_id="CA003", customer_id=sample_customer.customer_id, case_type="OPEN")
    repo = RecommendationRepository(db)
    rec = repo.create(
        recommendation_id="R001",
        case_id=case.case_id,
        product_id=sample_product.product_id,
        eligibility_status="ELIGIBLE"
    )
    assert rec.recommendation_id == "R001"

def test_inventory_repository_find_by_product(db, sample_product):
    repo = InventoryRepository(db)
    inventory = repo.create(
        inventory_id="I001",
        product_id=sample_product.product_id,
        quantity_available=10,
        stock_status="AVAILABLE"
    )
    found = repo.find_by_product(sample_product.product_id)
    assert found is not None
    assert found.quantity_available == 10

def test_sale_repository_create(db, sample_customer):
    repo = SaleRepository(db)
    sale = repo.create(
        sale_id="S001",
        customer_id=sample_customer.customer_id,
        total_amount_toman=100000
    )
    assert sale.sale_id == "S001"

def test_sale_item_repository_create(db, sample_product, sample_customer):
    sale_repo = SaleRepository(db)
    sale = sale_repo.create(
        sale_id="S002",
        customer_id=sample_customer.customer_id,
        total_amount_toman=50000
    )
    repo = SaleItemRepository(db)
    item = repo.create(
        sale_item_id="SI001",
        sale_id=sale.sale_id,
        product_id=sample_product.product_id,
        quantity=2,
        unit_price_toman=25000
    )
    assert item.sale_item_id == "SI001"

def test_base_count_method(db):
    repo = ProductRepository(db)
    assert repo.count() == 0
