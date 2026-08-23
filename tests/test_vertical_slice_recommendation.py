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
        TEST_DB.unlink()
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{TEST_DB}")

    import importlib
    import app.database as database

    importlib.reload(database)
    database.init_db()

    from scripts.seed_products_from_records import seed

    Session = sessionmaker(bind=database.engine)
    session = Session()
    seed(session)
    yield session
    session.close()
    if TEST_DB.exists():
        TEST_DB.unlink()


def test_seed_products_and_evidence(db_session):
    from app.models.product import Product
    from app.models.evidence import Evidence

    assert db_session.query(Product).filter_by(identity_status="VERIFIED").count() == 4
    assert db_session.query(Evidence).count() >= 4


def test_recommendation_with_evidence_persists(db_session):
    from app.services.recommendation_service import RecommendationService

    svc = RecommendationService(db_session)
    # Exact category tokens from PRODUCT_C_RECORD (no invention)
    profile = {"concerns": "ضدآفتاب روزانه صورت"}
    recs = svc.generate_recommendations("CASE-VS-002", profile)
    assert isinstance(recs, list)
    # With SECONDARY evidence_score=0.2 + inventory 1.0 + high need_match, score can pass 0.5
    assert len(recs) >= 1
