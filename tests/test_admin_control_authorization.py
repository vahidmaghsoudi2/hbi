"""ADMIN-CONTROL-001 — Admin-only management reports and operational FX writes."""

from app.core.auth import create_access_token
from app.models.operational_fx_rate import OperationalFxRate
from app.models.user_role import ROLE_ADMIN, UserRole


def _headers(subject_id: str):
    token = create_access_token({"sub": subject_id})
    return {"Authorization": f"Bearer {token}"}


def _grant_admin(db_session, subject_id: str = "admin-user"):
    db_session.add(
        UserRole(
            user_role_id=f"ROLE-{subject_id}",
            subject_id=subject_id,
            role=ROLE_ADMIN,
        )
    )
    db_session.commit()


REPORT_CASES = [
    "/api/v1/reports/sales/period/today",
    "/api/v1/reports/sales/range?start=2026-09-20T00:00:00Z&end=2026-09-21T00:00:00Z",
    "/api/v1/reports/inventory",
    "/api/v1/reports/inventory/category/BOOST",
    "/api/v1/reports/inventory/low-stock",
    "/api/v1/reports/financial?start=2026-09-20T00:00:00Z&end=2026-09-21T00:00:00Z",
    "/api/v1/reports/categories",
]


def test_management_reports_require_admin(client, db_session):
    for path in REPORT_CASES:
        assert client.get(path).status_code == 401
        assert client.get(
            path, headers={"Authorization": "Bearer invalid-token"}
        ).status_code == 401
        assert client.get(path, headers=_headers("ordinary-user")).status_code == 403

    _grant_admin(db_session)
    for path in REPORT_CASES:
        response = client.get(path, headers=_headers("admin-user"))
        assert response.status_code == 200, (path, response.text)


def test_operational_fx_write_requires_admin_and_preserves_state(client, db_session):
    before = db_session.query(OperationalFxRate).count()
    payload = {"fx_rate_usd_to_irr": 1_500_000.0, "note": "authz regression test"}

    assert client.post("/api/v1/fx/operational", json=payload).status_code == 401
    assert client.post(
        "/api/v1/fx/operational",
        json=payload,
        headers={"Authorization": "Bearer invalid-token"},
    ).status_code == 401
    assert client.post(
        "/api/v1/fx/operational",
        json=payload,
        headers=_headers("ordinary-user"),
    ).status_code == 403

    db_session.expire_all()
    assert db_session.query(OperationalFxRate).count() == before

    _grant_admin(db_session)
    response = client.post(
        "/api/v1/fx/operational",
        json=payload,
        headers=_headers("admin-user"),
    )
    assert response.status_code == 200, response.text
    assert db_session.query(OperationalFxRate).count() == before + 1


def test_current_fx_read_remains_public_read_only(client):
    response = client.get("/api/v1/fx/current")
    assert response.status_code == 200
