from sqlalchemy.engine import Engine
from sqlalchemy import event
import os
from pathlib import Path

BASE_DIR = Path(r"E:\HBI")
REPOS_DIR = BASE_DIR / "app" / "repositories"
TESTS_DIR = BASE_DIR / "tests"

REPOS_DIR.mkdir(parents=True, exist_ok=True)
TESTS_DIR.mkdir(parents=True, exist_ok=True)

# ==================== Repository Files ====================

files = {}

files["__init__.py"] = '''from .base import BaseRepository
from .product_repository import ProductRepository
from .customer_repository import CustomerRepository
from .case_repository import CaseRepository
from .recommendation_repository import RecommendationRepository
from .inventory_repository import InventoryRepository
from .sale_repository import SaleRepository
from .sale_item_repository import SaleItemRepository

__all__ = [
    "BaseRepository",
    "ProductRepository",
    "CustomerRepository",
    "CaseRepository",
    "RecommendationRepository",
    "InventoryRepository",
    "SaleRepository",
    "SaleItemRepository",
]
'''

files["base.py"] = '''from typing import TypeVar, Generic, Type, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    """Repository پایه با عملیات CRUD عمومی"""

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def create(self, **kwargs) -> ModelType:
        try:
            instance = self.model(**kwargs)
            self.db.add(instance)
            self.db.flush()
            return instance
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to create {self.model.__name__}: {e}")

    def get_by_id(self, id: str) -> Optional[ModelType]:
        pk_column = self.model.__table__.primary_key.columns[0]
        return self.db.query(self.model).filter(pk_column == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def update(self, id: str, **kwargs) -> Optional[ModelType]:
        try:
            instance = self.get_by_id(id)
            if not instance:
                return None
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            self.db.flush()
            return instance
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to update {self.model.__name__}: {e}")

    def delete(self, id: str) -> bool:
        try:
            instance = self.get_by_id(id)
            if not instance:
                return False
            self.db.delete(instance)
            self.db.flush()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to delete {self.model.__name__}: {e}")

    def count(self) -> int:
        return self.db.query(self.model).count()

    def filter_by(self, **kwargs) -> List[ModelType]:
        return self.db.query(self.model).filter_by(**kwargs).all()
'''

files["product_repository.py"] = '''from typing import List
from sqlalchemy.orm import Session
from app.models.product import Product
from app.repositories.base import BaseRepository

class ProductRepository(BaseRepository[Product]):
    def __init__(self, db: Session):
        super().__init__(Product, db)

    def find_by_brand(self, brand: str) -> List[Product]:
        return self.db.query(Product).filter(Product.brand.ilike(f"%{brand}%")).all()

    def find_by_identity_status(self, status: str) -> List[Product]:
        return self.db.query(Product).filter(Product.identity_status == status).all()

    def find_by_qa_verdict(self, verdict: str) -> List[Product]:
        return self.db.query(Product).filter(Product.qa_verdict == verdict).all()

    def get_with_inventory(self, product_id: str):
        return self.db.query(Product).filter(Product.product_id == product_id).first()
'''

files["customer_repository.py"] = '''from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.repositories.base import BaseRepository

class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, db: Session):
        super().__init__(Customer, db)

    def find_by_mobile(self, mobile: str) -> Optional[Customer]:
        return self.db.query(Customer).filter(Customer.mobile == mobile).first()

    def find_by_name(self, name: str) -> List[Customer]:
        return self.db.query(Customer).filter(Customer.name.ilike(f"%{name}%")).all()

    def get_with_cases(self, customer_id: str):
        return self.db.query(Customer).filter(Customer.customer_id == customer_id).first()
'''

files["case_repository.py"] = '''from typing import List
from sqlalchemy.orm import Session
from app.models.case import Case
from app.repositories.base import BaseRepository

class CaseRepository(BaseRepository[Case]):
    def __init__(self, db: Session):
        super().__init__(Case, db)

    def find_by_customer(self, customer_id: str) -> List[Case]:
        return self.db.query(Case).filter(Case.customer_id == customer_id).all()

    def find_by_case_type(self, case_type: str) -> List[Case]:
        return self.db.query(Case).filter(Case.case_type == case_type).all()

    def get_with_recommendations(self, case_id: str):
        return self.db.query(Case).filter(Case.case_id == case_id).first()
'''

files["recommendation_repository.py"] = '''from typing import List
from sqlalchemy.orm import Session
from app.models.recommendation import Recommendation
from app.repositories.base import BaseRepository

class RecommendationRepository(BaseRepository[Recommendation]):
    def __init__(self, db: Session):
        super().__init__(Recommendation, db)

    def find_by_case(self, case_id: str) -> List[Recommendation]:
        return self.db.query(Recommendation).filter(Recommendation.case_id == case_id).all()

    def find_by_product(self, product_id: str) -> List[Recommendation]:
        return self.db.query(Recommendation).filter(Recommendation.product_id == product_id).all()

    def find_eligible(self) -> List[Recommendation]:
        return self.db.query(Recommendation).filter(Recommendation.eligibility_status == "ELIGIBLE").all()
'''

files["inventory_repository.py"] = '''from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.inventory import Inventory
from app.repositories.base import BaseRepository

class InventoryRepository(BaseRepository[Inventory]):
    def __init__(self, db: Session):
        super().__init__(Inventory, db)

    def find_by_product(self, product_id: str) -> Optional[Inventory]:
        return self.db.query(Inventory).filter(Inventory.product_id == product_id).first()

    def find_available(self) -> List[Inventory]:
        return self.db.query(Inventory).filter(Inventory.stock_status == "AVAILABLE").all()

    def update_quantity(self, product_id: str, quantity: int) -> Optional[Inventory]:
        inventory = self.find_by_product(product_id)
        if inventory:
            inventory.quantity_available = quantity
            self.db.flush()
        return inventory
'''

files["sale_repository.py"] = '''from typing import List
from sqlalchemy.orm import Session
from app.models.sale import Sale
from app.repositories.base import BaseRepository

class SaleRepository(BaseRepository[Sale]):
    def __init__(self, db: Session):
        super().__init__(Sale, db)

    def find_by_customer(self, customer_id: str) -> List[Sale]:
        return self.db.query(Sale).filter(Sale.customer_id == customer_id).all()

    def find_with_items(self, sale_id: str):
        return self.db.query(Sale).filter(Sale.sale_id == sale_id).first()

    def get_total_sales(self) -> int:
        result = self.db.query(Sale.total_amount_toman).all()
        return sum([r[0] for r in result]) if result else 0
'''

files["sale_item_repository.py"] = '''from typing import List
from sqlalchemy.orm import Session
from app.models.sale_item import SaleItem
from app.repositories.base import BaseRepository

class SaleItemRepository(BaseRepository[SaleItem]):
    def __init__(self, db: Session):
        super().__init__(SaleItem, db)

    def find_by_sale(self, sale_id: str) -> List[SaleItem]:
        return self.db.query(SaleItem).filter(SaleItem.sale_id == sale_id).all()

    def find_by_product(self, product_id: str) -> List[SaleItem]:
        return self.db.query(SaleItem).filter(SaleItem.product_id == product_id).all()
'''

# نوشتن فایل‌های repositories
for filename, content in files.items():
    file_path = REPOS_DIR / filename
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created: {file_path}")

# ==================== Test File ====================

test_content = '''import pytest
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
'''

test_path = TESTS_DIR / "test_repositories.py"
with open(test_path, "w", encoding="utf-8") as f:
    f.write(test_content)
print(f"Created: {test_path}")

print()
print("=" * 60)
print("All Repository files + tests created successfully!")
print("=" * 60)
print()
print("Now run the tests with this command:")
print("cd /d E:\\HBI")
print("pytest tests\\test_repositories.py -v")