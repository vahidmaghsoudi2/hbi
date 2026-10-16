"""Runtime: FastAPI lifespan must create schema so products/guest do not 500."""
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def fresh_sqlite(tmp_path, monkeypatch):
    db_file = tmp_path / "hbi_runtime.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_file}")
    monkeypatch.setenv("HBI_ENV", "development")
    # Re-import engine binding after env change is hard; call init_db via lifespan path.
    # Use app as configured: lifespan calls init_db on enter.
    from importlib import reload
    import app.database as database
    reload(database)
    import app.main as main
    # Point main's get_db users at reloaded engine by reloading routers is heavy;
    # instead invoke init_db then TestClient against current app with override.
    database.init_db()
    from app.main import app
    from app.core.deps import get_db

    Session = database.SessionLocal

    def _ov():
        db = Session()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    app.dependency_overrides[get_db] = _ov
    app.dependency_overrides[database.get_db] = _ov
    with TestClient(app, raise_server_exceptions=True) as client:
        yield client
    app.dependency_overrides.clear()


def test_products_not_500_after_schema(fresh_sqlite):
    r = fresh_sqlite.get("/api/v1/products/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_guest_not_500_after_schema(fresh_sqlite):
    r = fresh_sqlite.post(
        "/api/v1/customers/guest",
        json={"name": "Runtime Test", "consent": 1, "concerns": "ضدآفتاب"},
    )
    assert r.status_code == 201
    assert r.json().get("customer_id")



def test_legacy_customer_schema_adds_family_name_without_rewriting_history(tmp_path, monkeypatch):
    from sqlalchemy import create_engine, inspect
    import app.database as database

    legacy_path = tmp_path / "legacy_customer.db"
    legacy_engine = create_engine(f"sqlite:///{legacy_path}")
    with legacy_engine.begin() as conn:
        conn.exec_driver_sql(
            'CREATE TABLE "Customer" (customer_id VARCHAR PRIMARY KEY, name VARCHAR NOT NULL, mobile VARCHAR)'
        )
        conn.exec_driver_sql(
            'INSERT INTO "Customer" (customer_id, name, mobile) VALUES (?, ?, ?)',
            ("CUST_LEGACY_1", "Legacy Display Name", "09130009999"),
        )

    monkeypatch.setattr(database, "engine", legacy_engine)
    database._ensure_customer_family_name_column()

    columns = {column["name"] for column in inspect(legacy_engine).get_columns("Customer")}
    assert "family_name" in columns
    with legacy_engine.connect() as conn:
        row = conn.exec_driver_sql(
            'SELECT name, family_name, mobile FROM "Customer" WHERE customer_id = ?',
            ("CUST_LEGACY_1",),
        ).one()
    assert row.name == "Legacy Display Name"
    assert row.family_name is None
    assert row.mobile == "09130009999"
    legacy_engine.dispose()
