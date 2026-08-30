"""Customer Profile unit — isolated tests (no recommendation/scoring changes)."""
import pytest
from app.database import SessionLocal, init_db
from app.services.customer_service import CustomerService


@pytest.fixture()
def db():
    init_db()
    session = SessionLocal()
    try:
        yield session
        session.commit()
    finally:
        session.close()


def test_register_guest_and_profile(db):
    svc = CustomerService(db)
    g = svc.register_guest(name="مهمان تست", concerns="ضدآفتاب", consent_to_store_data=1)
    assert g.customer_id.startswith("CUST_GUEST_")
    assert g.mobile is None
    profile = svc.build_recommendation_profile(g)
    assert profile.get("concerns") == "ضدآفتاب"


def test_intake_new_and_update_concerns(db):
    svc = CustomerService(db)
    c1 = svc.record_intake(
        name="سارا",
        mobile="09129990001",
        concerns="آبرسان",
        consent=1,
    )
    assert c1.customer_id.startswith("CUST_")
    assert c1.concerns == "آبرسان"

    c2 = svc.record_intake(
        name="سارا",
        mobile="09129990001",
        concerns="ضدآفتاب, لک",
        consent=1,
    )
    assert c2.customer_id == c1.customer_id
    assert c2.concerns == "ضدآفتاب, لک"


def test_build_profile_prefers_explicit_concerns(db):
    svc = CustomerService(db)
    c = svc.record_intake(
        name="رضا",
        mobile="09129990002",
        concerns="مو",
        consent=0,
    )
    profile = svc.build_recommendation_profile(c, concerns="ضدآفتاب")
    assert profile["concerns"] == "ضدآفتاب"


def test_empty_profile_still_has_concerns_key(db):
    svc = CustomerService(db)
    profile = svc.build_recommendation_profile(None)
    assert "concerns" in profile
    assert profile["concerns"] == ""
