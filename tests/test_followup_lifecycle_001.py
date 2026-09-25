from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

TEST_DB = Path(__file__).resolve().parents[1] / "data" / "hbi_followup_lifecycle_001.db"


@pytest.fixture()
def client(monkeypatch):
    if TEST_DB.exists():
        try:
            TEST_DB.unlink()
        except PermissionError:
            pass
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{TEST_DB}")
    monkeypatch.setenv("HBI_ENV", "development")

    import importlib
    import app.database as database
    importlib.reload(database)
    database.init_db()

    from app.core.deps import get_db
    from app.main import app
    from app.models.case import Case
    from app.models.customer import Customer
    from app.models.feedback import Feedback
    from app.models.product import Product
    from app.models.recommendation import Recommendation

    Session = sessionmaker(bind=database.engine)
    session = Session()
    session.add_all([
        Customer(customer_id="CUST-FU-1", name="Followup Owner", consent_to_store_data=1),
        Customer(customer_id="CUST-FU-2", name="Followup Other", consent_to_store_data=1),
        Case(case_id="CASE-FU-1", customer_id="CUST-FU-1", case_type="OPEN"),
        Case(case_id="CASE-FU-2", customer_id="CUST-FU-2", case_type="OPEN"),
        Product(
            product_id="PROD-FU-1", brand="HBI", product_name="Followup Test",
            identity_status="VERIFIED", status="ACTIVE", qa_verdict="VALID",
        ),
        Recommendation(
            recommendation_id="REC-FU-1", case_id="CASE-FU-1", product_id="PROD-FU-1",
            eligibility_status="ELIGIBLE",
        ),
        Recommendation(
            recommendation_id="REC-FU-2", case_id="CASE-FU-2", product_id="PROD-FU-1",
            eligibility_status="ELIGIBLE",
        ),
        Feedback(feedback_id="FB-FU-1", case_id="CASE-FU-1", source="CUSTOMER"),
        Feedback(feedback_id="FB-FU-2", case_id="CASE-FU-2", source="CUSTOMER"),
    ])
    session.commit()
    session.close()

    def override_db():
        db = Session()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    database.engine.dispose()
    if TEST_DB.exists():
        try:
            TEST_DB.unlink()
        except PermissionError:
            pass


def headers(customer_id):
    from app.core.auth import create_access_token
    return {"Authorization": f"Bearer {create_access_token({'sub': customer_id})}"}


def create_followup(client, h=None):
    h = h or headers("CUST-FU-1")
    when = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    response = client.post(
        "/api/v1/followups",
        headers=h,
        json={"case_id": "CASE-FU-1", "scheduled_at": when},
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_followup_auth_and_case_ownership(client):
    r = client.get("/api/v1/followups/case/CASE-FU-1")
    assert r.status_code == 401
    r = client.get("/api/v1/followups/case/CASE-FU-1", headers=headers("CUST-FU-2"))
    assert r.status_code == 403
    r = client.get("/api/v1/followups/case/CASE-NOT-FOUND", headers=headers("CUST-FU-1"))
    assert r.status_code == 404


def test_followup_trace_validation(client):
    h = headers("CUST-FU-1")
    when = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    r = client.post("/api/v1/followups", headers=h, json={"case_id": "CASE-FU-1", "recommendation_id": "NOPE", "scheduled_at": when})
    assert r.status_code == 422
    r = client.post("/api/v1/followups", headers=h, json={"case_id": "CASE-FU-1", "recommendation_id": "REC-FU-2", "scheduled_at": when})
    assert r.status_code == 422
    r = client.post("/api/v1/followups", headers=h, json={"case_id": "CASE-FU-1", "feedback_id": "FB-FU-2", "scheduled_at": when})
    assert r.status_code == 422


def test_followup_full_lifecycle_and_terminal_guard(client):
    h = headers("CUST-FU-1")
    follow_up = create_followup(client, h)
    assert follow_up["status"] == "SCHEDULED"
    assert follow_up["recommendation_id"] is None

    listed = client.get("/api/v1/followups/case/CASE-FU-1", headers=h)
    assert listed.status_code == 200
    assert listed.json()[0]["follow_up_id"] == follow_up["follow_up_id"]

    new_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    rescheduled = client.patch(
        f"/api/v1/followups/{follow_up['follow_up_id']}?case_id=CASE-FU-1",
        headers=h,
        json={"scheduled_at": new_time},
    )
    assert rescheduled.status_code == 200, rescheduled.text
    assert rescheduled.json()["status"] == "SCHEDULED"
    assert rescheduled.json()["scheduled_at"].startswith(new_time[:16])

    completed = client.post(
        f"/api/v1/followups/{follow_up['follow_up_id']}/complete?case_id=CASE-FU-1",
        headers=h,
    )
    assert completed.status_code == 200
    assert completed.json()["status"] == "COMPLETED"

    blocked = client.patch(
        f"/api/v1/followups/{follow_up['follow_up_id']}?case_id=CASE-FU-1",
        headers=h,
        json={"scheduled_at": new_time},
    )
    assert blocked.status_code == 409


def test_followup_cancel_lifecycle(client):
    h = headers("CUST-FU-1")
    follow_up = create_followup(client, h)
    cancelled = client.post(
        f"/api/v1/followups/{follow_up['follow_up_id']}/cancel?case_id=CASE-FU-1",
        headers=h,
    )
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "CANCELLED"

    blocked = client.post(
        f"/api/v1/followups/{follow_up['follow_up_id']}/complete?case_id=CASE-FU-1",
        headers=h,
    )
    assert blocked.status_code == 409


def test_followup_rejects_foreign_followup_and_preserves_trace(client):
    h1 = headers("CUST-FU-1")
    h2 = headers("CUST-FU-2")
    follow_up = create_followup(client, h1)
    r = client.get("/api/v1/followups/case/CASE-FU-2", headers=h2)
    assert r.status_code == 200
    assert r.json() == []
    r = client.patch(
        f"/api/v1/followups/{follow_up['follow_up_id']}?case_id=CASE-FU-2",
        headers=h2,
        json={"scheduled_at": (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()},
    )
    assert r.status_code == 403
