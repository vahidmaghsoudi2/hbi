"""Targeted regression contract for isolated Sales customer-search results.

This intentionally tests state ownership, not generic menu navigation.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOMEPAGE = ROOT / "frontend" / "src" / "pages" / "NewHomePage.tsx"


def test_sales_customer_search_uses_dedicated_results_state():
    src = HOMEPAGE.read_text(encoding="utf-8")
    assert 'const [customerSearchResults, setCustomerSearchResults]' in src
    assert 'const [saleCustomerSearchResults, setSaleCustomerSearchResults]' in src

    start = src.index("async function searchSaleCustomers")
    end = src.index("\n  function chooseSaleCustomer", start)
    sales_search = src[start:end]
    assert "setSaleCustomerSearchResults" in sales_search
    assert "setCustomerSearchResults" not in sales_search

    sales_picker_start = src.index("setSaleCustomerSearchResults", src.index("function chooseSaleCustomer"))
    assert "saleCustomerSearchResults.map((customer)" in src
    assert "customerSearchResults.map((customer)" in src
    assert sales_picker_start > 0
