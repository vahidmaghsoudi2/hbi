"""Vertical-slice: seed from product records → RecommendationService.generate_recommendations.

Does not invent evidence rows. Evidence list may be empty (engine still runs).
"""
import os
from pathlib import Path

import pytest
from sqlalchemy.orm import sessionmaker

# Isolated test DB
TEST_DB = Path(__file__).resolve().parents[1] / "data" / "hbi_vertical_slice_test.db"


@pytest.fixture()
def db_session(monkeypatch):
    if TEST_DB.exists():
        TEST_DB.unlink()
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{TEST_DB}")

    # Re-bind engine after env change
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


def test_seed_loads_four_verified_products(db_session):
    from app.models.product import Product

    products = db_session.query(Product).filter_by(identity_status="VERIFIED").all()
    assert len(products) == 4
    ids = {p.product_id for p in products}
    assert "ISDIN-FUSIONWATERMAGIC-50ML" in ids
    assert "ISDIN-FOTOUTRA100-50ML" in ids


def test_recommendation_vertical_slice_runs(db_session):
    from app.services.recommendation_service import RecommendationService

    svc = RecommendationService(db_session)
    # concerns overlap category keywords where possible (Persian tokens from records)
    profile = {"concerns": "ضدآفتاب, صورت, روزانه"}
    recs = svc.generate_recommendations("CASE-VS-001", profile)
    # May be empty if scores < 0.5 without evidence — still must not crash
    assert isinstance(recs, list)
    # At least inventory-backed products were considered (no exception path)
    from app.models.inventory import Inventory

    inv_count = db_session.query(Inventory).filter(Inventory.quantity_available > 0).count()
    assert inv_count == 4
