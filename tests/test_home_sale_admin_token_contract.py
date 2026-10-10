"""Static contract: sale write requires Admin token (client layer).

No runtime DB. Source files are the truth until E2E is recorded separately.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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


def test_client_create_sale_uses_admin_session_token():
    src = CLIENT.read_text(encoding="utf-8")
    idx = src.find("export function createSale")
    assert idx > 0
    block = src[idx : idx + 900]
    assert "hbi_admin_access_token" in block
    assert "adminToken" in block
    assert "ADMIN" in src[max(0, idx - 300) : idx + 80]
    assert "نشست مشتری برای ثبت فروش کافی نیست" in block or "حساب مدیر" in block


def test_client_documents_admin_requirement_for_create_sale():
    src = CLIENT.read_text(encoding="utf-8")
    idx = src.find("export function createSale")
    assert idx > 0
    assert "ADMIN" in src[max(0, idx - 300) : idx + 80]
