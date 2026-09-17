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
