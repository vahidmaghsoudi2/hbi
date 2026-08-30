"""Vertical-slice: Product Record → Evidence → RecommendationService.

Sources: data/seed_products.json + data/seed_evidence.json (from SoT docs only).
"""
from pathlib import Path

import pytest
from sqlalchemy.orm import sessionmaker

TEST_DB = Path(__file__).resolve().parents[1] / "data" / "hbi_vertical_slice_test.db"


@pytest.fixture()
def db_session(monkeypatch):
    if TEST_DB.exists():
        try:
            TEST_DB.unlink()
        except PermissionError:
            pass  # Ignore Windows file lock
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{TEST_DB}")

    import importlib
    import app.database as database

    importlib.reload(database)
    database.init_db()

    from scripts.seed_products_from_records import seed
    from app.models.customer import Customer
    from app.models.case import Case

    Session = sessionmaker(bind=database.engine)
    session = Session()
    seed(session)
    # Minimal fixtures for Recommendation.case_id FK (not product data invention)
    if session.get(Customer, "CUST-VS-001") is None:
        session.add(Customer(customer_id="CUST-VS-001", name="VS Fixture"))
    if session.get(Case, "CASE-VS-002") is None:
        session.add(Case(case_id="CASE-VS-002", customer_id="CUST-VS-001"))
    session.commit()
    yield session
    session.close()
    try:
        database.engine.dispose()
    except Exception:
        pass
    if TEST_DB.exists():
        try:
            TEST_DB.unlink()
        except PermissionError:
            pass  # Ignore Windows file lock


def test_seed_products_and_evidence(db_session):
    from app.models.product import Product
    from app.models.evidence import Evidence

    assert db_session.query(Product).filter_by(identity_status="VERIFIED").count() == 4
    assert db_session.query(Evidence).count() >= 4


def test_recommendation_with_evidence_persists(db_session):
    from app.services.recommendation_service import RecommendationService

    svc = RecommendationService(db_session)
    profile = {"concerns": "ضدآفتاب روزانه صورت"}
    recs = svc.generate_recommendations("CASE-VS-002", profile)
    assert isinstance(recs, list)
    assert len(recs) >= 1
