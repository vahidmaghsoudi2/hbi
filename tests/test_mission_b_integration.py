import json

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.models.customer import Customer
from app.models.case import Case
from app.models.product import Product
from app.models.recommendation import Recommendation
from app.services.recommendation_outcome_service import RecommendationOutcomeService


@pytest.fixture()
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    session.add(Customer(customer_id="C1", name="Test Customer"))
    session.add(Case(case_id="CASE1", customer_id="C1"))
    session.add(Product(product_id="P1", brand="B", product_name="Prod", identity_status="VERIFIED", status="ACTIVE"))
    session.commit()
    yield session
    session.close()


def test_record_outcome_and_list(db):
    svc = RecommendationOutcomeService(db)
    row = svc.record_outcome(
        case_id="CASE1",
        product_id="P1",
        outcome_type="accepted",
        actor_id="C1",
        notes="customer liked",
        follow_up_status="SCHEDULED",
        follow_up_notes="call in 7d",
    )
    db.commit()
    assert row.outcome_type == "ACCEPTED"
    assert row.follow_up_status == "SCHEDULED"
    listed = svc.list_by_case("CASE1")
    assert len(listed) == 1
    assert listed[0].outcome_id == row.outcome_id


def test_invalid_outcome_rejected(db):
    svc = RecommendationOutcomeService(db)
    with pytest.raises(ValueError):
        svc.record_outcome(case_id="CASE1", product_id="P1", outcome_type="LOVED", actor_id="C1")


def test_specialist_override_preserves_prior(db):
    svc = RecommendationOutcomeService(db)
    case = svc.apply_specialist_override(
        case_id="CASE1",
        actor_id="OP1",
        reason="clinical judgment",
        override_action="FORCE_REVIEW",
        product_id="P1",
    )
    db.commit()
    data = json.loads(case.operator_override)
    assert data["actor_id"] == "OP1"
    assert data["action"] == "FORCE_REVIEW"
    assert data["reason"] == "clinical judgment"
    assert data["prior_override"] is None

    case2 = svc.apply_specialist_override(
        case_id="CASE1",
        actor_id="OP2",
        reason="second look",
        override_action="ACCEPT_ALTERNATIVE",
    )
    db.commit()
    data2 = json.loads(case2.operator_override)
    assert data2["prior_override"] is not None
    assert "OP1" in data2["prior_override"]


def test_gallery_returns_recommendations(db):
    db.add(
        Recommendation(
            recommendation_id="R1",
            case_id="CASE1",
            product_id="P1",
            eligibility_status="ELIGIBLE",
            ranking_score=0.8,
        )
    )
    db.commit()
    svc = RecommendationOutcomeService(db)
    gallery = svc.gallery_for_case("CASE1")
    assert len(gallery) == 1
    assert gallery[0]["product_id"] == "P1"
    assert gallery[0]["eligibility_status"] == "ELIGIBLE"
