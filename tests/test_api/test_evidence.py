from sqlalchemy.engine import Engine
from sqlalchemy import event
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.deps import get_db, get_current_customer_id
from app.models.base import Base
from app.models.product import Product
from app.models.customer import Customer

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_evidence.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


async def mock_get_current_customer_id():
    return "C001"


@pytest.fixture(autouse=True)
def override_deps():
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_customer_id] = mock_get_current_customer_id
    yield
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        db.add(Product(product_id="P001", brand="TestBrand", product_name="Test Product", identity_status="VERIFIED"))
        db.add(Customer(customer_id="C001", name="Test User", consent_to_store_data=1))
        db.commit()
    finally:
        db.close()
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_create_evidence():
    r = client.post("/api/v1/evidence/", json={"product_id": "P001", "claim": "Contains salicylic acid", "source_type": "PEER_REVIEWED", "source_reference": "DOI:1234", "claim_type": "FACT", "field": "ingredients"})
    assert r.status_code == 201
    assert r.json()["claim_id"].startswith("EV-P001-")


def test_create_evidence_rejects_manufacturer_to_fact():
    r = client.post("/api/v1/evidence/", json={"product_id": "P001", "claim": "Cures acne", "source_type": "MANUFACTURER", "source_reference": "MFR-001", "claim_type": "FACT", "field": "benefits"})
    assert r.status_code == 422


def test_list_evidence():
    client.post("/api/v1/evidence/", json={"product_id": "P001", "claim": "Ev1", "source_type": "PEER_REVIEWED", "source_reference": "R1"})
    client.post("/api/v1/evidence/", json={"product_id": "P001", "claim": "Ev2", "source_type": "PEER_REVIEWED", "source_reference": "R2"})
    r = client.get("/api/v1/evidence/")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_verify_evidence():
    c = client.post("/api/v1/evidence/", json={"product_id": "P001", "claim": "Test", "source_type": "PEER_REVIEWED", "source_reference": "R3"})
    eid = c.json()["evidence_id"]
    r = client.post(f"/api/v1/evidence/{eid}/verify", json={"verdict": "VERIFIED"})
    assert r.status_code == 200
    assert r.json()["qa_status"] == "VERIFIED"


def test_detect_conflicts():
    client.post("/api/v1/evidence/", json={"product_id": "P001", "claim": "SPF 30", "source_type": "PEER_REVIEWED", "source_reference": "R4", "field": "spf"})
    client.post("/api/v1/evidence/", json={"product_id": "P001", "claim": "SPF 50", "source_type": "MANUFACTURER", "source_reference": "R5", "field": "spf"})
    r = client.get("/api/v1/evidence/conflicts/P001")
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_resolve_conflict():
    client.post("/api/v1/evidence/", json={"product_id": "P001", "claim": "SPF 30", "source_type": "PEER_REVIEWED", "source_reference": "R4", "field": "spf"})
    c2 = client.post("/api/v1/evidence/", json={"product_id": "P001", "claim": "SPF 50", "source_type": "MANUFACTURER", "source_reference": "R5", "field": "spf"})
    eid = c2.json()["evidence_id"]
    r = client.post(f"/api/v1/evidence/{eid}/resolve", json={"resolution": "Manufacturer is newer"})
    assert r.status_code == 200
    data = r.json()
    assert data["conflict_status"] == "NONE"
    assert "RESOLVED" in data["notes"]


def test_product_knowledge_get():
    client.post("/api/v1/evidence/", json={"product_id": "P001", "claim": "salicylic acid", "source_type": "PEER_REVIEWED", "source_reference": "R6", "field": "ingredients"})
    client.post("/api/v1/evidence/", json={"product_id": "P001", "claim": "reduces acne", "source_type": "MANUFACTURER", "source_reference": "R7", "field": "claimed_benefits"})
    client.post("/api/v1/evidence/knowledge/P001/refresh")
    r = client.get("/api/v1/evidence/knowledge/P001")
    assert r.status_code == 200
    data = r.json()
    assert data.get("ingredients") is not None
    assert "salicylic acid" in data["ingredients"]


def test_unknown_handling():
    r = client.post("/api/v1/evidence/", json={"product_id": "P001", "claim": "Unknown", "source_type": "PEER_REVIEWED", "source_reference": "UNK", "claim_type": "UNKNOWN"})
    assert r.status_code == 201
    assert r.json()["claim_type"] == "UNKNOWN"
