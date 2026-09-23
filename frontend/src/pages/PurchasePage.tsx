import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listManageableProducts, stockInInventory, getCurrentFx } from "../api/client";
import type { ProductDTO } from "../types/api";

type StockInResult = {
  inventory?: Record<string, unknown>;
  movement?: Record<string, unknown>;
  before_quantity?: number;
};

export default function PurchasePage() {
  const [adminToken, setAdminToken] = useState<string | null>(() =>
    sessionStorage.getItem("hbi_admin_access_token")
  );
  const [products, setProducts] = useState<ProductDTO[]>([]);
  const [productId, setProductId] = useState("");
  const [quantity, setQuantity] = useState("1");
  const [purchasePriceUsd, setPurchasePriceUsd] = useState("");
  const [fxRate, setFxRate] = useState<number | null>(null);
  const [note, setNote] = useState("");
  const [referenceId, setReferenceId] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingProducts, setLoadingProducts] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [result, setResult] = useState<StockInResult | null>(null);

  async function load() {
    const token = sessionStorage.getItem("hbi_admin_access_token");
    setAdminToken(token);
    if (!token) return;
    setLoadingProducts(true);
    setError(null);
    try {
      const [items, fx] = await Promise.all([
        listManageableProducts(token),
        getCurrentFx(),
      ]);
      setProducts(Array.isArray(items) ? items : []);
      setFxRate(fx.fx_rate_usd_to_irr);
      if (fx.fx_rate_usd_to_irr == null) {
        setError("نرخ عملیاتی ارز در دسترس نیست؛ ثبت خرید متوقف است.");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setProducts([]);
      setFxRate(null);
    } finally {
      setLoadingProducts(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setStatus(null);
    setResult(null);

    const token = sessionStorage.getItem("hbi_admin_access_token");
    if (!token) {
      setError("برای ثبت خرید نشست Admin لازم است.");
      return;
    }
    if (!productId) {
      setError("محصول را انتخاب کنید.");
      return;
    }
    const quantityValue = Number(quantity);
    const priceValue = Number(purchasePriceUsd);
    if (!Number.isInteger(quantityValue) || quantityValue <= 0) {
      setError("تعداد باید یک عدد صحیح مثبت باشد.");
      return;
    }
    if (!Number.isFinite(priceValue) || priceValue < 0) {
      setError("قیمت خرید دلاری نامعتبر است.");
      return;
    }
    if (fxRate == null || fxRate <= 0) {
      setError("نرخ عملیاتی ارز در دسترس نیست؛ ثبت خرید متوقف است.");
      return;
    }

    setLoading(true);
    try {
      const response = await stockInInventory(
        {
          product_id: productId,
          quantity: quantityValue,
          purchase_price_usd: priceValue,
          fx_rate_usd_to_irr: fxRate,
          note: note.trim() || undefined,
          reference_type: referenceId.trim() ? "PURCHASE" : undefined,
          reference_id: referenceId.trim() || undefined,
        },
        token
      );
      setResult(response);
      setStatus("خرید/ورود کالا با موفقیت ثبت شد.");
      setQuantity("1");
      setPurchasePriceUsd("");
      setNote("");
      setReferenceId("");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="home-root pro-home">
      <header className="pro-header">
        <div className="pro-header-inner">
          <div className="pro-brand">
            <span className="pro-brand-mark">HBI</span>
            <div>
              <div className="pro-brand-title">گالری مقصودی</div>
              <div className="pro-brand-sub">ثبت خرید و ورود کالا</div>
            </div>
          </div>
          <nav className="pro-nav" aria-label="بخش‌های خرید">
            <Link to="/" className="pro-nav-btn">خانه HBI</Link>
            <Link to="/accounting" className="pro-nav-btn">حسابداری</Link>
          </nav>
        </div>
      </header>

      <main className="pro-main">
        <section className="pro-panel">
          <div className="pro-panel-head">
            <div>
              <h1>خرید / ورود کالا</h1>
              <p className="pro-lead">
                این فرم مستقیماً از عملیات واقعی Stock-In استفاده می‌کند.
                خرید مستقل از مشاوره و فروش ثبت می‌شود.
              </p>
            </div>
            <span className="pro-status-msg">{adminToken ? "Admin فعال" : "Admin لازم است"}</span>
          </div>

          {!adminToken ? (
            <div className="pro-alert" role="alert">
              نشست Admin در این مرورگر وجود ندارد. ابتدا نشست مدیریتی را ایجاد کنید، سپس این صفحه را نوسازی کنید.
            </div>
          ) : null}

          {error ? <div className="pro-alert" role="alert">{error}</div> : null}
          {status ? <div className="pro-status-bar"><span className="dot on" /><span className="pro-status-msg">{status}</span></div> : null}

          <form className="pro-form" onSubmit={submit}>
            <fieldset className="pro-fieldset">
              <legend>۱) کالا</legend>
              <label className="pro-label" htmlFor="purchase-product">محصول *</label>
              <select
                id="purchase-product"
                className="pro-input"
                value={productId}
                onChange={(e) => setProductId(e.target.value)}
                disabled={!adminToken || loadingProducts || loading}
              >
                <option value="">انتخاب محصول…</option>
                {products.map((p) => (
                  <option key={p.product_id} value={p.product_id}>
                    {p.product_name} · {p.brand} · {p.product_id}
                  </option>
                ))}
              </select>
              {!loadingProducts && adminToken && products.length === 0 ? (
                <p className="pro-muted">محصولی برای انتخاب وجود ندارد.</p>
              ) : null}
            </fieldset>

            <fieldset className="pro-fieldset">
              <legend>۲) خرید</legend>
              <div className="pro-grid-2">
                <div>
                  <label className="pro-label" htmlFor="purchase-quantity">تعداد *</label>
                  <input
                    id="purchase-quantity"
                    className="pro-input"
                    type="number"
                    min="1"
                    step="1"
                    value={quantity}
                    onChange={(e) => setQuantity(e.target.value.replace(/[^0-9]/g, ""))}
                    disabled={!adminToken || loading}
                  />
                </div>
                <div>
                  <label className="pro-label" htmlFor="purchase-price">قیمت خرید هر واحد (USD) *</label>
                  <input
                    id="purchase-price"
                    className="pro-input"
                    type="number"
                    min="0"
                    step="0.01"
                    value={purchasePriceUsd}
                    onChange={(e) => setPurchasePriceUsd(e.target.value)}
                    placeholder="مثلاً 12.50"
                    disabled={!adminToken || loading}
                  />
                </div>
              </div>
              <p className="pro-summary">
                نرخ عملیاتی ارز: <strong>{fxRate == null ? "در دسترس نیست" : fxRate.toLocaleString("en-US") + " IRR / USD"}</strong>
              </p>
            </fieldset>

            <fieldset className="pro-fieldset">
              <legend>۳) ثبت مرجع</legend>
              <div className="pro-grid-2">
                <div>
                  <label className="pro-label" htmlFor="purchase-reference">شناسه فاکتور / مرجع</label>
                  <input
                    id="purchase-reference"
                    className="pro-input"
                    value={referenceId}
                    onChange={(e) => setReferenceId(e.target.value)}
                    placeholder="اختیاری"
                    disabled={!adminToken || loading}
                  />
                </div>
                <div>
                  <label className="pro-label" htmlFor="purchase-note">یادداشت</label>
                  <input
                    id="purchase-note"
                    className="pro-input"
                    value={note}
                    onChange={(e) => setNote(e.target.value)}
                    placeholder="اختیاری"
                    disabled={!adminToken || loading}
                  />
                </div>
              </div>
            </fieldset>

            <div className="pro-actions">
              <button type="submit" className="pro-btn-primary" disabled={!adminToken || loading || fxRate == null}>
                {loading ? "در حال ثبت…" : "ثبت خرید"}
              </button>
              <button type="button" className="pro-btn-secondary" onClick={() => void load()} disabled={loading}>
                نوسازی
              </button>
            </div>
          </form>

          {result ? (
            <section className="pro-panel" style={{ marginTop: "1rem" }}>
              <h2>نتیجه ثبت</h2>
              <p className="pro-muted">
                موجودی قبل از خرید: {String(result.before_quantity ?? "—")} ·
                موجودی بعد از خرید: {String(result.inventory?.quantity_available ?? "—")}
              </p>
              <p className="pro-muted">
                حرکت انبار: {String(result.movement?.movement_type ?? "—")} ·
                مبلغ تومان: {String(result.movement?.amount_toman ?? "—")}
              </p>
            </section>
          ) : null}
        </section>
      </main>
    </div>
  );
}
