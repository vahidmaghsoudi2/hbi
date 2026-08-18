from sqlalchemy.engine import Engine
from sqlalchemy import event
import os
from pathlib import Path

BASE_DIR = Path(r"E:\HBI")
INTERFACE_DIR = BASE_DIR / "app" / "interface"
TESTS_DIR = BASE_DIR / "tests"

INTERFACE_DIR.mkdir(parents=True, exist_ok=True)
TESTS_DIR.mkdir(parents=True, exist_ok=True)

files = {}

# ==================== interface/__init__.py ====================
files["__init__.py"] = '''from .errors import InterfaceError, NotFoundError, ValidationError, BusinessRuleError
from .dto import (
    ProductDTO, CustomerDTO, CaseDTO, RecommendationDTO,
    InventoryDTO, SaleDTO, SaleItemDTO
)
from .facades import (
    ProductFacade, CustomerFacade, CaseFacade,
    RecommendationFacade, InventoryFacade, SaleFacade
)

__all__ = [
    "InterfaceError", "NotFoundError", "ValidationError", "BusinessRuleError",
    "ProductDTO", "CustomerDTO", "CaseDTO", "RecommendationDTO",
    "InventoryDTO", "SaleDTO", "SaleItemDTO",
    "ProductFacade", "CustomerFacade", "CaseFacade",
    "RecommendationFacade", "InventoryFacade", "SaleFacade",
]
'''

# ==================== interface/errors.py ====================
files["errors.py"] = '''class InterfaceError(Exception):
    """Base exception for Interface Layer"""
    pass

class NotFoundError(InterfaceError):
    """Resource not found"""
    pass

class ValidationError(InterfaceError):
    """Input validation failed"""
    pass

class BusinessRuleError(InterfaceError):
    """Business rule violation raised from Service Layer"""
    pass
'''

# ==================== interface/dto.py ====================
files["dto.py"] = '''from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class ProductDTO:
    product_id: str
    brand: str
    product_name: str
    identity_status: str
    qa_verdict: str
    variant: Optional[str] = None
    size_value: Optional[float] = None
    size_unit: Optional[str] = None

@dataclass
class CustomerDTO:
    customer_id: str
    name: str
    mobile: Optional[str] = None
    consent_to_store_data: int = 0

@dataclass
class CaseDTO:
    case_id: str
    customer_id: str
    case_type: str

@dataclass
class RecommendationDTO:
    recommendation_id: str
    case_id: str
    product_id: str
    need_match_score: Optional[float] = None
    eligibility_status: Optional[str] = None
    ranking_score: Optional[float] = None
    ranking_reasons: Optional[str] = None

@dataclass
class InventoryDTO:
    inventory_id: str
    product_id: str
    quantity_available: int
    quantity_reserved: int
    stock_status: str
    sale_price_toman: Optional[int] = None

@dataclass
class SaleItemDTO:
    sale_item_id: str
    sale_id: str
    product_id: str
    quantity: int
    unit_price_toman: int

@dataclass
class SaleDTO:
    sale_id: str
    customer_id: str
    total_amount_toman: int
    items: Optional[List[SaleItemDTO]] = None
'''

# ==================== interface/facades.py ====================
files["facades.py"] = '''from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from app.services.product_service import ProductService
from app.services.customer_service import CustomerService
from app.services.case_service import CaseService
from app.services.recommendation_service import RecommendationService
from app.services.inventory_service import InventoryService
from app.services.sale_service import SaleService
from app.interface.dto import (
    ProductDTO, CustomerDTO, CaseDTO, RecommendationDTO,
    InventoryDTO, SaleDTO, SaleItemDTO
)
from app.interface.errors import NotFoundError, ValidationError, BusinessRuleError

def _to_product_dto(p) -> ProductDTO:
    return ProductDTO(
        product_id=p.product_id,
        brand=p.brand,
        product_name=p.product_name,
        identity_status=p.identity_status,
        qa_verdict=p.qa_verdict,
        variant=p.variant,
        size_value=p.size_value,
        size_unit=p.size_unit
    )

def _to_customer_dto(c) -> CustomerDTO:
    return CustomerDTO(
        customer_id=c.customer_id,
        name=c.name,
        mobile=c.mobile,
        consent_to_store_data=c.consent_to_store_data
    )

def _to_case_dto(c) -> CaseDTO:
    return CaseDTO(
        case_id=c.case_id,
        customer_id=c.customer_id,
        case_type=c.case_type
    )

def _to_recommendation_dto(r) -> RecommendationDTO:
    return RecommendationDTO(
        recommendation_id=r.recommendation_id,
        case_id=r.case_id,
        product_id=r.product_id,
        need_match_score=r.need_match_score,
        eligibility_status=r.eligibility_status,
        ranking_score=r.ranking_score,
        ranking_reasons=r.ranking_reasons
    )

def _to_inventory_dto(i) -> InventoryDTO:
    return InventoryDTO(
        inventory_id=i.inventory_id,
        product_id=i.product_id,
        quantity_available=i.quantity_available,
        quantity_reserved=i.quantity_reserved,
        stock_status=i.stock_status,
        sale_price_toman=i.sale_price_toman
    )

class ProductFacade:
    def __init__(self, db: Session):
        self.service = ProductService(db)

    def get_by_id(self, product_id: str) -> ProductDTO:
        product = self.service.get_by_id(product_id)
        if not product:
            raise NotFoundError(f"Product {product_id} not found")
        return _to_product_dto(product)

    def find_by_brand(self, brand: str) -> List[ProductDTO]:
        products = self.service.find_by_brand(brand)
        return [_to_product_dto(p) for p in products]

    def get_verified_products(self) -> List[ProductDTO]:
        products = self.service.get_verified_products()
        return [_to_product_dto(p) for p in products]

class CustomerFacade:
    def __init__(self, db: Session):
        self.service = CustomerService(db)

    def register(self, name: str, mobile: Optional[str] = None, consent: int = 0) -> CustomerDTO:
        try:
            customer = self.service.register_customer(
                name=name,
                mobile=mobile,
                consent_to_store_data=consent
            )
            return _to_customer_dto(customer)
        except ValueError as e:
            raise BusinessRuleError(str(e))

    def find_by_mobile(self, mobile: str) -> CustomerDTO:
        customer = self.service.find_by_mobile(mobile)
        if not customer:
            raise NotFoundError(f"Customer with mobile {mobile} not found")
        return _to_customer_dto(customer)

class CaseFacade:
    def __init__(self, db: Session):
        self.service = CaseService(db)

    def create(self, customer_id: str, case_type: str = "OPEN") -> CaseDTO:
        case = self.service.create_case(customer_id=customer_id, case_type=case_type)
        return _to_case_dto(case)

    def find_by_customer(self, customer_id: str) -> List[CaseDTO]:
        cases = self.service.find_by_customer(customer_id)
        return [_to_case_dto(c) for c in cases]

    def close(self, case_id: str) -> CaseDTO:
        case = self.service.close_case(case_id)
        if not case:
            raise NotFoundError(f"Case {case_id} not found")
        return _to_case_dto(case)

class RecommendationFacade:
    def __init__(self, db: Session):
        self.service = RecommendationService(db)

    def generate(self, case_id: str, customer_profile: Dict) -> List[RecommendationDTO]:
        recommendations = self.service.generate_recommendations(case_id, customer_profile)
        return [_to_recommendation_dto(r) for r in recommendations]

    def find_by_case(self, case_id: str) -> List[RecommendationDTO]:
        recommendations = self.service.find_by_case(case_id)
        return [_to_recommendation_dto(r) for r in recommendations]

class InventoryFacade:
    def __init__(self, db: Session):
        self.service = InventoryService(db)

    def get_by_product(self, product_id: str) -> InventoryDTO:
        inventory = self.service.find_by_product(product_id)
        if not inventory:
            raise NotFoundError(f"Inventory for product {product_id} not found")
        return _to_inventory_dto(inventory)

    def find_available(self) -> List[InventoryDTO]:
        items = self.service.find_available()
        return [_to_inventory_dto(i) for i in items]

class SaleFacade:
    def __init__(self, db: Session):
        self.service = SaleService(db)

    def create_sale(self, customer_id: str, items: List[Dict]) -> SaleDTO:
        try:
            sale = self.service.create_sale(customer_id, items)
            sale_items = self.service.get_sale_items(sale.sale_id)
            item_dtos = [
                SaleItemDTO(
                    sale_item_id=si.sale_item_id,
                    sale_id=si.sale_id,
                    product_id=si.product_id,
                    quantity=si.quantity,
                    unit_price_toman=si.unit_price_toman
                ) for si in sale_items
            ]
            return SaleDTO(
                sale_id=sale.sale_id,
                customer_id=sale.customer_id,
                total_amount_toman=sale.total_amount_toman,
                items=item_dtos
            )
        except ValueError as e:
            raise BusinessRuleError(str(e))

    def get_total_sales(self) -> int:
        return self.service.get_total_sales()
'''

# ==================== interface/cli.py ====================
files["cli.py"] = '''"""
Simple CLI entry point for HBI Interface Layer
Usage examples (from project root):
    python -m app.interface.cli
"""
from app.database import SessionLocal, init_db
from app.interface.facades import (
    ProductFacade, CustomerFacade, CaseFacade,
    RecommendationFacade, InventoryFacade, SaleFacade
)

def main():
    print("=" * 50)
    print("HBI Interface Layer - CLI")
    print("=" * 50)

    init_db()
    db = SessionLocal()

    try:
        product_facade = ProductFacade(db)
        customer_facade = CustomerFacade(db)
        case_facade = CaseFacade(db)
        recommendation_facade = RecommendationFacade(db)
        inventory_facade = InventoryFacade(db)
        sale_facade = SaleFacade(db)

        print("\\nFacades loaded successfully:")
        print("  - ProductFacade")
        print("  - CustomerFacade")
        print("  - CaseFacade")
        print("  - RecommendationFacade")
        print("  - InventoryFacade")
        print("  - SaleFacade")
        print("\\nInterface Layer is ready.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
'''

# Write interface files
for filename, content in files.items():
    path = INTERFACE_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created: {path}")

# ==================== tests/test_interface.py ====================
test_content = '''import pytest
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
        session.rollback()
        session.close()

@pytest.fixture
def sample_product(db):
    repo = ProductRepository(db)
    return repo.create(
        product_id="P001",
        brand="TestBrand",
        product_name="Test Product",
        identity_status="VERIFIED",
        qa_verdict="VALID"
    )

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
    case_facade = CaseFacade(db)
    case = case_facade.create(customer_id=sample_customer.customer_id)
    rec_facade = RecommendationFacade(db)
    recs = rec_facade.generate(case.case_id, {"skin_type": "oily"})
    assert len(recs) >= 1
    assert recs[0].case_id == case.case_id

def test_inventory_facade_get_by_product(db, sample_product, sample_inventory):
    facade = InventoryFacade(db)
    dto = facade.get_by_product(sample_product.product_id)
    assert dto.quantity_available == 10
    assert dto.stock_status == "AVAILABLE"

def test_sale_facade_create_sale(db, sample_product, sample_customer, sample_inventory):
    facade = SaleFacade(db)
    items = [{"product_id": sample_product.product_id, "quantity": 2, "unit_price_toman": 50000}]
    sale = facade.create_sale(sample_customer.customer_id, items)
    assert sale.total_amount_toman == 100000
    assert len(sale.items) == 1

def test_sale_facade_insufficient_stock(db, sample_product, sample_customer, sample_inventory):
    facade = SaleFacade(db)
    items = [{"product_id": sample_product.product_id, "quantity": 20, "unit_price_toman": 50000}]
    with pytest.raises(BusinessRuleError):
        facade.create_sale(sample_customer.customer_id, items)
'''

test_path = TESTS_DIR / "test_interface.py"
with open(test_path, "w", encoding="utf-8") as f:
    f.write(test_content)
print(f"Created: {test_path}")

print()
print("=" * 60)
print("GATE 6-4B Interface Layer created successfully!")
print("=" * 60)
print()
print("Now run the tests:")
print("cd /d E:\\HBI")
print("python -m pytest tests\\test_interface.py -v")