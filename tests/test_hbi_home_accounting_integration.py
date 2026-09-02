"""PHASE 13 — HBI Home → Accounting navigation (static source verification).

No data/hbi.db. No accounting business logic changes.
Uses repository source files as truth (frontend has no unit-test runner).
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend" / "src"


def test_app_registers_home_and_accounting_routes():
    app = (FRONTEND / "App.tsx").read_text(encoding="utf-8")
    assert 'path="/"' in app and "NewHomePage" in app
    assert 'path="/accounting"' in app and "AccountingHomePage" in app
    assert app.count('path="/accounting"') == 1
    assert app.count("AccountingHomePage") >= 2  # import + route element


def test_single_accounting_home_component():
    pages = list((FRONTEND / "pages").glob("*Accounting*"))
    names = sorted(p.name for p in pages)
    assert names == ["AccountingHomePage.tsx"]


def test_new_home_has_accounting_link_to_canonical_route():
    src = (FRONTEND / "pages" / "NewHomePage.tsx").read_text(encoding="utf-8")
    assert 'to="/accounting"' in src
    assert "حسابداری" in src
    assert "Link" in src and "react-router-dom" in src


def test_accounting_home_page_is_phase03_shell():
    src = (FRONTEND / "pages" / "AccountingHomePage.tsx").read_text(encoding="utf-8")
    assert "export default" in src
    assert "حسابداری" in src
    assert (FRONTEND / "styles" / "accounting.css").exists()
