"""Static contract: homepage sale write must use Admin token, not pilot/customer session.

No runtime DB. Source files are the truth until E2E is recorded separately.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "frontend" / "src" / "pages" / "NewHomePage.tsx"
CLIENT = ROOT / "frontend" / "src" / "api" / "client.ts"
SALES = ROOT / "app" / "api" / "routers" / "sales.py"


def test_backend_create_sale_requires_admin_role():
    src = SALES.read_text(encoding="utf-8")
    assert "require_any_role(ROLE_ADMIN)" in src
    assert "async def create_sale" in src


def test_backend_sales_total_is_customer_scoped():
    src = SALES.read_text(encoding="utf-8")
    assert "get_current_customer_id" in src
    assert "async def get_total_sales" in src


def test_homepage_sale_submit_uses_admin_access_token():
    src = HOME.read_text(encoding="utf-8")
    assert "function getAdminAccessToken" in src
    assert 'sessionStorage.getItem("hbi_admin_access_token")' in src
    assert "adminToken" in src
    assert "createSale(" in src
    block = src.split("async function onSaleSubmit")[1].split("function formatExclusionReason")[0]
    assert "createSale(" in block
    assert "adminToken" in block
    assert "حساب مدیر" in block


def test_homepage_does_not_call_create_sale_with_bare_session_token():
    src = HOME.read_text(encoding="utf-8")
    block = src.split("async function onSaleSubmit")[1].split("function formatExclusionReason")[0]
    assert "adminToken" in block
    # Auth header argument to createSale must be adminToken (not pilot session `token`).
    assert "adminToken" in block[block.index("createSale(") : block.index("createSale(") + 400]


def test_client_documents_admin_requirement_for_create_sale():
    src = CLIENT.read_text(encoding="utf-8")
    idx = src.find("export function createSale")
    assert idx > 0
    window = src[max(0, idx - 240) : idx + 80]
    assert "ADMIN" in window
