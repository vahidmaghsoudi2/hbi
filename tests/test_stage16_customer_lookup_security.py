"""Stage-16 security: customer lookup role gates + HBI_ENV whitelist."""
import pytest

from app.core.auth import create_access_token, get_runtime_env
from app.models.user_role import ROLE_ADMIN, ROLE_EDITOR, ROLE_PO, UserRole
from app.models.customer import Customer


def _headers(subject_id: str):
    token = create_access_token({"sub": subject_id})
    return {"Authorization": f"Bearer {token}"}


def _grant(db_session, subject_id: str, role: str):
    db_session.add(
        UserRole(
            user_role_id=f"UR-{subject_id}-{role.replace('/', '-')}",
            subject_id=subject_id,
            role=role,
        )
    )
    db_session.commit()


def _seed_customer(db_session, customer_id: str = "CUST_A", mobile: str = "09121111111", family_name: str = "Testi"):
    row = Customer(
        customer_id=customer_id,
        name="Alpha",
        family_name=family_name,
        mobile=mobile,
        consent_to_store_data=0,
    )
    db_session.merge(row)
    db_session.commit()
    return customer_id


def test_runtime_env_accepts_whitelist(monkeypatch):
    monkeypatch.setenv("HBI_ENV", "development")
    assert get_runtime_env() == "development"
    monkeypatch.setenv("HBI_ENV", "PRODUCTION")
    assert get_runtime_env() == "production"


def test_runtime_env_rejects_prod_alias(monkeypatch):
    monkeypatch.setenv("HBI_ENV", "prod")
    with pytest.raises(RuntimeError, match="HBI_ENV"):
        get_runtime_env()


def test_search_requires_managerial_role(client, db_session):
    _seed_customer(db_session)
    assert client.get("/api/v1/customers/search?q=Testi").status_code == 401
    assert client.get(
        "/api/v1/customers/search?q=Testi",
        headers=_headers("CUST_A"),
    ).status_code == 403

    _grant(db_session, "po-user", ROLE_PO)
    r = client.get(
        "/api/v1/customers/search?q=Testi",
        headers=_headers("po-user"),
    )
    assert r.status_code == 200, r.text
    assert any(item.get("family_name") == "Testi" for item in r.json())
    assert any(item.get("mobile") == "09121111111" for item in r.json())


def test_search_allows_editor_and_admin(client, db_session):
    _seed_customer(db_session)
    _grant(db_session, "ed", ROLE_EDITOR)
    _grant(db_session, "ad", ROLE_ADMIN)
    assert client.get(
        "/api/v1/customers/search?q=Testi", headers=_headers("ed")
    ).status_code == 200
    assert client.get(
        "/api/v1/customers/search?q=Testi", headers=_headers("ad")
    ).status_code == 200


def test_get_by_id_self_vs_other(client, db_session):
    _seed_customer(db_session, "CUST_A", "09121111111")
    _seed_customer(db_session, "CUST_B", "09122222222", family_name="Other")

    self_ok = client.get(
        "/api/v1/customers/id/CUST_A", headers=_headers("CUST_A")
    )
    assert self_ok.status_code == 200, self_ok.text

    other = client.get(
        "/api/v1/customers/id/CUST_B", headers=_headers("CUST_A")
    )
    assert other.status_code == 403

    _grant(db_session, "mgr", ROLE_ADMIN)
    mgr = client.get(
        "/api/v1/customers/id/CUST_B", headers=_headers("mgr")
    )
    assert mgr.status_code == 200, mgr.text


def test_mobile_lookup_managerial_only(client, db_session):
    _seed_customer(db_session, "CUST_A", "09121111111")
    assert client.get(
        "/api/v1/customers/mobile/09121111111", headers=_headers("CUST_A")
    ).status_code == 403

    _grant(db_session, "po-user", ROLE_PO)
    r = client.get(
        "/api/v1/customers/mobile/09121111111", headers=_headers("po-user")
    )
    assert r.status_code == 200, r.text
    assert r.json().get("mobile") == "09121111111"
