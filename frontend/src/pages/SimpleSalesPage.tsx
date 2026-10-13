import { FormEvent, useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  createSale,
  getInventoryByProduct,
  listManageableProducts,
  searchCustomers,
} from "../api/client";
import type { CustomerSearchResult, ProductDTO, SaleDTO } from "../types/api";

/**
 * Focused operator sales screen — no consultation chrome, no kitchen-sink nav.
 */
export default function SimpleSalesPage() {
  const adminToken =
    typeof sessionStorage !== "undefined" ? sessionStorage.getItem("hbi_admin_access_token") : null;

  const [query, setQuery] = useState("");
  const [results, setResults] = useState<CustomerSearchResult[]>([]);
  const [searchBusy, setSearchBusy] = useState(false);
  const [customer, setCustomer] = useState<CustomerSearchResult | null>(null);

  const [products, setProducts] = useState<ProductDTO[]>([]);
  const [productId, setProductId] = useState("");
  const [qty, setQty] = useState(1);
  const [stock, setStock] = useState<number | null>(null);
  const [price, setPrice] = useState<number | null>(null);

  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastSale, setLastSale] = useState<SaleDTO | null>(null);

  const loadProducts = useCallback(async () => {
    if (!adminToken) return;
    try {
      const data = await listManageableProducts(adminToken);
      const active = (Array.isArray(data) ? data : []).filter(
        (p) => String(p.status ?? "").trim().toUpperCase() === "ACTIVE"
      );
      setProducts(active);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }, [adminToken]);

  useEffect(() => {
    void loadProducts();
  }, [loadProducts]);

  useEffect(() => {
    if (!adminToken || !productId) {
      setStock(null);
      setPrice(null);
      return;
    }
    let cancelled = false;
    void (async () => {
      try {
        const inv = await getInventoryByProduct(productId, adminToken);
        if (cancelled) return;
        const available = (inv.quantity_available ?? 0) - (inv.quantity_reserved ?? 0);
        setStock(available);
        setPrice(inv.sale_price_usd ?? null);
      } catch {
        if (!cancelled) {
          setStock(null);
          setPrice(null);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [adminToken, productId]);

  async function onSearch(e: FormEvent) {
    e.preventDefault();
    setError(null);
    if (!adminToken) {
      setError("نشست مدیر فعال نیست. دوباره وارد شوید.");
      return;
    }
    const q = query.trim();
    if (!q) {
      setResults([]);
      return;
    }
    setSearchBusy(true);
    try {
      const found = await searchCustomers(q, adminToken);
      setResults(Array.isArray(found) ? found : []);
    } catch (err) {
      setResults([]);
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setSearchBusy(false);
    }
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLastSale(null);
    if (!adminToken) {
      setError("نشست مدیر فعال نیست.");
      return;
    }
    if (!customer?.customer_id) {
      setError("ابتدا مشتری را انتخاب کنید.");
      return;
    }
    if (!productId) {
      setError("کالا را انتخاب کنید.");
      return;
    }
    if (qty < 1) {
      setError("تعداد باید حداقل ۱ باشد.");
      return;
    }
    setBusy(true);
    try {
      const sale = await createSale(
        {
          customer_id: customer.customer_id,
          items: [{ product_id: productId, quantity: qty }],
        },
        adminToken
      );
      setLastSale(sale);
      try {
        const inv = await getInventoryByProduct(productId, adminToken);
        setStock((inv.quantity_available ?? 0) - (inv.quantity_reserved ?? 0));
      } catch {
        /* ignore */
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  if (!adminToken) {
    return (
      <section className="pro-panel" dir="rtl" style={{ padding: "1.5rem" }}>
        <p>برای ثبت فروش باید با حساب مدیر وارد شده باشید.</p>
        <Link to="/login">صفحه ورود</Link>
      </section>
    );
  }

  return (
    <section className="pro-panel" dir="rtl" style={{ maxWidth: 720, margin: "0 auto", padding: "1.25rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "1rem", flexWrap: "wrap" }}>
        <h1 style={{ margin: 0 }}>ثبت فروش</h1>
        <Link className="pro-nav-btn" to="/">
          ← داشبورد
        </Link>
      </div>
      <p className="pro-lead">فروش مستقیم — بدون نیاز به مشاوره قبلی.</p>

      {error ? (
        <div className="pro-alert" role="alert">
          {error}
        </div>
      ) : null}

      {lastSale ? (
        <div className="pro-alert" role="status" style={{ background: "#e8f5e9" }}>
          فروش ثبت شد. شناسه: {String(lastSale.sale_id ?? "—")}
        </div>
      ) : null}

      <form onSubmit={onSearch} className="pro-actions" style={{ marginBottom: "1rem" }}>
        <label style={{ display: "block", marginBottom: "0.35rem" }}>جست‌وجوی مشتری (نام یا موبایل)</label>
        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
          <input
            className="pro-input"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="نام یا شماره موبایل…"
            style={{ flex: 1, minWidth: 180 }}
          />
          <button type="submit" className="pro-btn-primary" disabled={searchBusy}>
            {searchBusy ? "…" : "جست‌وجو"}
          </button>
        </div>
      </form>

      {results.length > 0 ? (
        <ul style={{ listStyle: "none", padding: 0, margin: "0 0 1rem" }}>
          {results.map((c) => (
            <li key={c.customer_id} style={{ marginBottom: "0.35rem" }}>
              <button
                type="button"
                className={customer?.customer_id === c.customer_id ? "pro-btn-primary" : "pro-nav-btn"}
                onClick={() => {
                  setCustomer(c);
                  setResults([]);
                  setQuery(c.name ?? c.mobile ?? c.customer_id);
                }}
              >
                {(c.name ?? "بدون نام") + " — " + (c.mobile ?? "بدون موبایل") + " (" + c.customer_id + ")"}
              </button>
            </li>
          ))}
        </ul>
      ) : null}

      {customer ? (
        <p>
          مشتری انتخاب‌شده: <strong>{customer.name ?? customer.customer_id}</strong>
          {customer.mobile ? ` — ${customer.mobile}` : ""}
        </p>
      ) : null}

      <form onSubmit={onSubmit}>
        <div style={{ marginBottom: "0.75rem" }}>
          <label style={{ display: "block", marginBottom: "0.35rem" }}>کالا</label>
          <select
            className="pro-input"
            value={productId}
            onChange={(e) => setProductId(e.target.value)}
            style={{ width: "100%" }}
          >
            <option value="">انتخاب کالا…</option>
            {products.map((p) => (
              <option key={p.product_id} value={p.product_id}>
                {(p.product_name ?? p.product_id) + " — " + (p.brand ?? "")}
              </option>
            ))}
          </select>
        </div>

        <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginBottom: "0.75rem" }}>
          <div>
            <label style={{ display: "block", marginBottom: "0.35rem" }}>تعداد</label>
            <input
              className="pro-input"
              type="number"
              min={1}
              value={qty}
              onChange={(e) => setQty(Math.max(1, Number(e.target.value) || 1))}
              style={{ width: 100 }}
            />
          </div>
          <div>
            <label style={{ display: "block", marginBottom: "0.35rem" }}>موجودی</label>
            <div>{stock == null ? "—" : stock}</div>
          </div>
          <div>
            <label style={{ display: "block", marginBottom: "0.35rem" }}>قیمت (USD)</label>
            <div>{price == null ? "—" : price}</div>
          </div>
        </div>

        <button type="submit" className="pro-btn-primary" disabled={busy || !customer || !productId}>
          {busy ? "در حال ثبت…" : "ثبت فروش"}
        </button>
      </form>
    </section>
  );
}
