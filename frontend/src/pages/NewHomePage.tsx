import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listProducts, pilotToken, customerIntake, createGuest } from "../api/client";
import type { ProductDTO, PilotTokenRequest, CustomerIntakeRequest, GuestCreateRequest } from "../types/api";

export default function NewHomePage() {
  const [token, setToken] = useState<string | null>(() => sessionStorage.getItem("hbi_access_token"));
  const [customerId, setCustomerId] = useState<string | null>(() => sessionStorage.getItem("hbi_customer_id"));

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

  const handleIntake = async (e: React.FormEvent) => {
    e.preventDefault();
    setIntakeError(null);
    setIntakeBusy(true);
    try {
      let currentToken = token;
      let currentCustomerId = customerId;

      if (!currentToken) {
        // ابتدا ساخت مهمان
        const guestBody: GuestCreateRequest = {
          name: name.trim(),
          consent: 1,
          concerns: concerns.trim(),
        };
        const guestResult: any = await createGuest(guestBody);
        if (!guestResult?.customer_id) {
          throw new Error("ساخت مهمان ناموفق بود.");
        }
        currentCustomerId = guestResult.customer_id;
        sessionStorage.setItem("hbi_customer_id", currentCustomerId);
        setCustomerId(currentCustomerId);

        // دریافت توکن با customer_id مهمان
        const tokenBody: PilotTokenRequest = { customer_id: currentCustomerId };
        const tokenResp = await pilotToken(tokenBody);
        sessionStorage.setItem("hbi_access_token", tokenResp.access_token);
        sessionStorage.setItem("hbi_refresh_token", tokenResp.refresh_token);
        currentToken = tokenResp.access_token;
        setToken(currentToken);
      }

      // ثبت مراجعه
      const intakeBody: CustomerIntakeRequest = {
        name: name.trim(),
        concerns: concerns.trim(),
        consent: 1,
        open_case: true,
      };
      const result: any = await customerIntake(intakeBody, currentToken);
      if (result?.case?.case_id) {
        sessionStorage.setItem("hbi_case_id", result.case.case_id);
        if (result?.customer?.customer_id) {
          sessionStorage.setItem("hbi_customer_id", result.customer.customer_id);
          setCustomerId(result.customer.customer_id);
        }
      }
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

      {!intakeResult && (
        <div className="card">
          <h2>شروع مراجعه</h2>
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
        <a className="btn secondary" href="mailto:consultation@hbi.local">درخواست مشاوره</a>
      </div>
    </section>
  );
}
