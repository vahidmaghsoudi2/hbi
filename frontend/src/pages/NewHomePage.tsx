import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listProducts, pilotToken, customerIntake } from "../api/client";
import type { ProductDTO, PilotTokenRequest, CustomerIntakeRequest } from "../types/api";

export default function NewHomePage() {
  const [token, setToken] = useState<string | null>(() => sessionStorage.getItem("hbi_access_token"));
  const [customerId, setCustomerId] = useState("");
  const [tokenError, setTokenError] = useState<string | null>(null);
  const [tokenBusy, setTokenBusy] = useState(false);

  const [name, setName] = useState("");
  const [concerns, setConcerns] = useState("");
  const [intakeError, setIntakeError] = useState<string | null>(null);
  const [intakeBusy, setIntakeBusy] = useState(false);
  const [intakeResult, setIntakeResult] = useState<any>(null);

  const [product, setProduct] = useState<ProductDTO | null>(null);
  const [productError, setProductError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const products = await listProducts();
        if (!cancelled && products.length > 0) setProduct(products[0]);
      } catch (e) {
        if (!cancelled) setProductError(e instanceof Error ? e.message : String(e));
      }
    })();
    return () => { cancelled = true; };
  }, []);

  const handleGetToken = async (e: React.FormEvent) => {
    e.preventDefault();
    setTokenError(null);
    setTokenBusy(true);
    try {
      const body: PilotTokenRequest = { customer_id: customerId.trim() };
      const resp = await pilotToken(body);
      sessionStorage.setItem("hbi_access_token", resp.access_token);
      sessionStorage.setItem("hbi_refresh_token", resp.refresh_token);
      setToken(resp.access_token);
    } catch (e) {
      setTokenError(e instanceof Error ? e.message : String(e));
    } finally {
      setTokenBusy(false);
    }
  };

  const handleIntake = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) { setIntakeError("ابتدا توکن دریافت کنید."); return; }
    setIntakeError(null);
    setIntakeBusy(true);
    try {
      const body: CustomerIntakeRequest = {
        name: name.trim(),
        concerns: concerns.trim(),
        consent: 1,
        open_case: true,
      };
      const result = await customerIntake(body, token);
      setIntakeResult(result);
    } catch (e) {
      setIntakeError(e instanceof Error ? e.message : String(e));
    } finally {
      setIntakeBusy(false);
    }
  };

  return (
    <section>
      <div className="hero">
        <h1>HBI — Health & Beauty Intelligence</h1>
        <p className="lead">تصمیم‌یار هوشمند پوست، مو و مراقبت شخصی</p>
        <div className="trust-strip">پشتیبانی‌شده توسط شواهد علمی واقعی</div>
      </div>

      {!token && (
        <div className="card">
          <h2>شروع سریع (Pilot)</h2>
          <p>برای استفاده از امکانات، ابتدا یک توکن آزمایشی دریافت کنید.</p>
          <form onSubmit={handleGetToken}>
            <label htmlFor="customer_id">شناسه مشتری</label>
            <input
              id="customer_id"
              value={customerId}
              onChange={(e) => setCustomerId(e.target.value)}
              placeholder="مثلاً CUST-123"
              required
            />
            <button type="submit" disabled={tokenBusy}>
              {tokenBusy ? "..." : "دریافت توکن"}
            </button>
            {tokenError && <div className="alert error">{tokenError}</div>}
          </form>
        </div>
      )}

      {token && !intakeResult && (
        <div className="card">
          <h2>چه کمکی نیاز دارید؟</h2>
          <p>اطلاعات خود را وارد کنید تا مسیر توصیه آغاز شود.</p>
          <form onSubmit={handleIntake}>
            <label htmlFor="name">نام</label>
            <input id="name" value={name} onChange={(e) => setName(e.target.value)} required />
            <label htmlFor="concerns">نگرانی‌ها / نیازها</label>
            <textarea id="concerns" value={concerns} onChange={(e) => setConcerns(e.target.value)} placeholder="مثلاً ضدآفتاب روزانه" required />
            <button type="submit" disabled={intakeBusy}>
              {intakeBusy ? "..." : "ثبت مراجعه"}
            </button>
            {intakeError && <div className="alert error">{intakeError}</div>}
          </form>
        </div>
      )}

      {intakeResult && (
        <div className="card">
          <h2>مراجعه ثبت شد</h2>
          <p><strong>customer_id:</strong> {intakeResult.customer?.customer_id}</p>
          <p><strong>case_id:</strong> {intakeResult.case?.case_id}</p>
          <Link className="btn" to="/recommendation">تولید Recommendation</Link>
        </div>
      )}

      <div className="card">
        <h2>نمونه محصول</h2>
        {productError && <div className="alert error">{productError}</div>}
        {!product && !productError && <div className="alert">در حال بارگذاری…</div>}
        {product && (
          <div>
            <strong>{product.product_name}</strong> — {product.brand}
            <br />
            <small>شناسه: {product.product_id}</small>
            <br />
            <small>وضعیت: {product.identity_status} | QA: {product.qa_verdict}</small>
          </div>
        )}
        <p><Link to="/catalog">مشاهده کاتالوگ کامل</Link></p>
      </div>

      <div className="card">
        <h2>مشاوره انسانی</h2>
        <p>در صورت نیاز به بررسی تخصصی، با مشاور ما در ارتباط باشید.</p>
        <a className="btn secondary" href="#" onClick={(e) => e.preventDefault()}>درخواست مشاوره</a>
      </div>
    </section>
  );
}
