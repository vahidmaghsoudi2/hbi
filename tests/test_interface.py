from sqlalchemy.engine import Engine
from sqlalchemy import event
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.product import Product
from app.models.customer import Customer
from app.models.inventory import Inventory
from app.repositories.product_repository import ProductRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.inventory_repository import InventoryRepository
from app.interface.facades import (
    ProductFacade, CustomerFacade, CaseFacade,
    RecommendationFacade, InventoryFacade, SaleFacade
)
from app.interface.errors import NotFoundError, BusinessRuleError

engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

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
        from app.models.recommendation import Recommendation
        from app.models.sale_item import SaleItem
        from app.models.sale import Sale
        from app.models.payment import Payment
        from app.models.sale_return import SaleReturn
        from app.models.stock_movement import StockMovement
        from app.models.case import Case
        from app.models.inventory import Inventory
        from app.models.product_knowledge import ProductKnowledge
        from app.models.evidence import Evidence
        from app.models.customer import Customer
        from app.models.product import Product
        session.query(Recommendation).delete(synchronize_session=False)
        session.query(Payment).delete(synchronize_session=False)
        session.query(SaleReturn).delete(synchronize_session=False)
        session.query(StockMovement).delete(synchronize_session=False)
        session.query(SaleItem).delete(synchronize_session=False)
        session.query(Sale).delete(synchronize_session=False)
        session.query(Case).delete(synchronize_session=False)
        session.query(Inventory).delete(synchronize_session=False)
        session.query(ProductKnowledge).delete(synchronize_session=False)
        session.query(Evidence).delete(synchronize_session=False)
        session.query(Customer).delete(synchronize_session=False)
        session.query(Product).delete(synchronize_session=False)
        session.commit()
        session.close()


@pytest.fixture
def sample_product(db):
    repo = ProductRepository(db)
    p = repo.create(
        product_id="P001",
        brand="TestBrand",
        product_name="Test Product",
        identity_status="VERIFIED",
        qa_verdict="VALID"
    )
    # Explicit-intent escape hatch for test fixture only (NOT AuthZ).
    repo.update_governance_privileged(
        p.product_id, confirm_escape_hatch=True, status="ACTIVE"
    )
    return p

@pytest.fixture
def sample_customer(db):
    repo = CustomerRepository(db)
    return repo.create(
        customer_id="C001",
        name="Test Customer",
        consent_to_store_data=1
    )

@pytest.fixture
def sample_inventory(db, sample_product):
    repo = InventoryRepository(db)
    return repo.create(
        inventory_id="I001",
        product_id=sample_product.product_id,
        quantity_available=10,
        quantity_reserved=0,
        stock_status="AVAILABLE"
    )

def test_product_facade_get_by_id(db, sample_product):
    facade = ProductFacade(db)
    dto = facade.get_by_id("P001")
    assert dto.product_id == "P001"
    assert dto.brand == "TestBrand"

def test_product_facade_not_found(db):
    facade = ProductFacade(db)
    with pytest.raises(NotFoundError):
        facade.get_by_id("INVALID")

def test_product_facade_get_verified(db, sample_product):
    facade = ProductFacade(db)
    products = facade.get_verified_products()
    assert len(products) == 1

def test_customer_facade_register(db):
    facade = CustomerFacade(db)
    dto = facade.register(name="New Customer", mobile="09120001122", consent=1)
    assert dto.name == "New Customer"
    assert dto.mobile == "09120001122"

def test_customer_facade_duplicate_mobile(db):
    facade = CustomerFacade(db)
    facade.register(name="First", mobile="09120003344", consent=1)
    with pytest.raises(BusinessRuleError):
        facade.register(name="Second", mobile="09120003344", consent=1)

def test_case_facade_create_and_find(db, sample_customer):
    facade = CaseFacade(db)
    case = facade.create(customer_id=sample_customer.customer_id)
    assert case.case_id.startswith("CASE_")
    cases = facade.find_by_customer(sample_customer.customer_id)
    assert len(cases) >= 1

def test_recommendation_facade_generate(db, sample_product, sample_customer, sample_inventory):
    from app.models.product_knowledge import ProductKnowledge
    from app.models.evidence import Evidence

    pk = ProductKnowledge(
        product_knowledge_id="PK_TEST_001",
        product_id=sample_product.product_id,
        known_use_cases="oily skin care, daily protection",
        claimed_benefits="oil control"
    )
    db.add(pk)

    ev = Evidence(
        evidence_id="EV_TEST_001",
        product_id=sample_product.product_id,
        source_type="OFFICIAL_MANUFACTURER",
        source_reference="TEST-SOURCE",
        claim="Test claim for oily skin",
        claim_type="FACT",
        evidence_status="SUPPORTED"
    )
    db.add(ev)
    db.commit()

    case_facade = CaseFacade(db)
    case = case_facade.create(customer_id=sample_customer.customer_id)
    rec_facade = RecommendationFacade(db)
    recs = rec_facade.generate(case.case_id, {"concerns": "oily skin care"})
    assert len(recs) >= 1
    assert recs[0].case_id == case.case_id


def test_inventory_facade_get_by_product(db, sample_product, sample_inventory):
    facade = InventoryFacade(db)
    dto = facade.get_by_product(sample_product.product_id)
    assert dto.quantity_available == 10
    assert dto.stock_status == "AVAILABLE"

def test_sale_facade_create_sale(db, sample_product, sample_customer, sample_inventory):
    """C-01: SaleFacade requires explicit fx_rate_usd_to_irr and unit_price_usd."""
    facade = SaleFacade(db)
    items = [
        {
            "product_id": sample_product.product_id,
            "quantity": 2,
            "unit_price_usd": 0.5,
        }
    ]
    sale = facade.create_sale(
        sample_customer.customer_id,
        items,
        fx_rate_usd_to_irr=1_000_000.0,
    )
    assert sale.total_amount_toman == 100000
    assert len(sale.items) == 1

def test_sale_facade_insufficient_stock(db, sample_product, sample_customer, sample_inventory):
    facade = SaleFacade(db)
    items = [
        {
            "product_id": sample_product.product_id,
            "quantity": 20,
            "unit_price_usd": 0.5,
        }
    ]
    with pytest.raises(BusinessRuleError):
        facade.create_sale(
            sample_customer.customer_id,
            items,
            fx_rate_usd_to_irr=1_000_000.0,
        )
