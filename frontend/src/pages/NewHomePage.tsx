import { FormEvent, useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  listProducts,
  pilotToken,
  customerIntake,
  createGuest,
} from "../api/client";
import type {
  ProductDTO,
  PilotTokenRequest,
  CustomerIntakeRequest,
  GuestCreateRequest,
} from "../types/api";

const NEED_OPTIONS = [
  { id: "spf", label: "ضدآفتاب", value: "ضدآفتاب" },
  { id: "hydrate", label: "آبرسان / مرطوب‌کننده", value: "آبرسان" },
  { id: "hair", label: "مراقبت مو", value: "مراقبت مو" },
  { id: "spot", label: "لک / یکنواختی پوست", value: "لک صورت" },
  { id: "sensitive", label: "پوست حساس", value: "پوست حساس" },
] as const;

export default function NewHomePage() {
  const navigate = useNavigate();
  const [token, setToken] = useState<string | null>(() =>
    sessionStorage.getItem("hbi_access_token")
  );
  const [customerId, setCustomerId] = useState<string | null>(() =>
    sessionStorage.getItem("hbi_customer_id")
  );

  const [name, setName] = useState("");
  const [concerns, setConcerns] = useState("");
  const [selectedNeeds, setSelectedNeeds] = useState<string[]>([]);
  const [intakeError, setIntakeError] = useState<string | null>(null);
  const [intakeBusy, setIntakeBusy] = useState(false);
  const [intakeResult, setIntakeResult] = useState<Record<string, unknown> | null>(
    null
  );

  const [products, setProducts] = useState<ProductDTO[]>([]);
  const [productsLoading, setProductsLoading] = useState(true);
  const [productError, setProductError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await listProducts();
        if (!cancelled) setProducts(Array.isArray(data) ? data.slice(0, 8) : []);
      } catch (e) {
        if (!cancelled)
          setProductError(e instanceof Error ? e.message : String(e));
      } finally {
        if (!cancelled) setProductsLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const mergedConcerns = useMemo(() => {
    const fromChips = selectedNeeds.join(", ");
    const free = concerns.trim();
    if (fromChips && free) return `${fromChips}, ${free}`;
    return fromChips || free;
  }, [selectedNeeds, concerns]);

  function toggleNeed(value: string) {
    setSelectedNeeds((prev) =>
      prev.includes(value) ? prev.filter((v) => v !== value) : [...prev, value]
    );
  }

  async function handleIntake(e: FormEvent) {
    e.preventDefault();
    setIntakeError(null);
    if (!name.trim()) {
      setIntakeError("لطفاً نام را وارد کنید.");
      return;
    }
    if (!mergedConcerns) {
      setIntakeError("یک نیاز انتخاب کنید یا نگرانی امروز را بنویسید.");
      return;
    }
    setIntakeBusy(true);
    try {
      let currentToken = token;
      let currentCustomerId = customerId;

      if (!currentToken) {
        const guestBody: GuestCreateRequest = {
          name: name.trim(),
          consent: 1,
          concerns: mergedConcerns,
        };
        const guestResult = (await createGuest(guestBody)) as {
          customer_id?: string;
        };
        if (!guestResult?.customer_id) {
          throw new Error("ساخت مهمان ناموفق بود.");
        }
        currentCustomerId = guestResult.customer_id;
        sessionStorage.setItem("hbi_customer_id", currentCustomerId);
        setCustomerId(currentCustomerId);

        const tokenBody: PilotTokenRequest = {
          customer_id: currentCustomerId,
        };
        const tokenResp = await pilotToken(tokenBody);
        sessionStorage.setItem("hbi_access_token", tokenResp.access_token);
        sessionStorage.setItem("hbi_refresh_token", tokenResp.refresh_token);
        currentToken = tokenResp.access_token;
        setToken(currentToken);
      }

      sessionStorage.setItem("hbi_concerns", mergedConcerns);

      const intakeBody: CustomerIntakeRequest = {
        name: name.trim(),
        concerns: mergedConcerns,
        consent: 1,
        open_case: true,
      };
      const result = (await customerIntake(
        intakeBody,
        currentToken as string
      )) as {
        case?: { case_id?: string };
        customer?: { customer_id?: string };
        recommendation_profile?: Record<string, unknown>;
      };

      if (result?.case?.case_id) {
        sessionStorage.setItem("hbi_case_id", result.case.case_id);
      }
      if (result?.customer?.customer_id) {
        sessionStorage.setItem("hbi_customer_id", result.customer.customer_id);
        setCustomerId(result.customer.customer_id);
      }
      setIntakeResult(result as Record<string, unknown>);
    } catch (err) {
      setIntakeError(err instanceof Error ? err.message : String(err));
    } finally {
      setIntakeBusy(false);
    }
  }

  function goToRecommendation() {
    navigate("/recommendation");
  }

  return (
    <div className="home-root">
      <header className="header">
        <div className="container header-inner">
          <div className="brand">گالری مقصودی</div>
          <nav className="nav" aria-label="اصلی">
            <a href="#need">نیاز امروز</a>
            <a href="#approach">مسیر ما</a>
            <a href="#products">محصولات</a>
            <a href="#consult">مشاوره</a>
            <Link to="/catalog">کاتالوگ</Link>
          </nav>
          <a className="cta-primary" href="#consult">
            شروع مشاوره
          </a>
        </div>
      </header>

      <section className="hero">
        <div className="container">
          <h1>انتخاب آگاهانه در زیبایی و مراقبت</h1>
          <p className="hero-subtitle">
            تصمیم‌یار گالری مقصودی — بر پایه شواهد محصول، نه حدس و تبلیغ.
          </p>
          <div className="hero-actions">
            <a className="cta-hero" href="#consult">
              مشاوره سریع
            </a>
            <a className="cta-hero-secondary" href="#products">
              مشاهده محصولات تأییدشده
            </a>
          </div>
        </div>
      </section>

      <section className="trust">
        <div className="container trust-inner">
          <div className="trust-item">
            <span className="trust-icon" aria-hidden>
              ✓
            </span>
            فقط محصول تأییدشده
          </div>
          <div className="trust-item">
            <span className="trust-icon" aria-hidden>
              ✓
            </span>
            توصیه با دلیل و شواهد
          </div>
          <div className="trust-item">
            <span className="trust-icon" aria-hidden>
              ✓
            </span>
            بدون ادعای پزشکی ساختگی
          </div>
        </div>
      </section>

      <section className="need" id="need">
        <div className="container">
          <h2>امروز به چه چیزی فکر می‌کنید؟</h2>
          <div className="need-options">
            {NEED_OPTIONS.map((n) => (
              <button
                key={n.id}
                type="button"
                className={
                  selectedNeeds.includes(n.value)
                    ? "need-btn need-btn-active"
                    : "need-btn"
                }
                onClick={() => toggleNeed(n.value)}
                aria-pressed={selectedNeeds.includes(n.value)}
              >
                {n.label}
              </button>
            ))}
          </div>
          {selectedNeeds.length > 0 && (
            <p className="need-hint">
              انتخاب شما: <strong>{selectedNeeds.join(" · ")}</strong>
            </p>
          )}
        </div>
      </section>

      <section className="approach" id="approach">
        <div className="container">
          <h2>مسیر شفاف مشاوره</h2>
          <div className="approach-steps">
            <div className="step">
              <div className="step-num">۱</div>
              <h3>نیاز امروز</h3>
              <p>در کمتر از یک دقیقه هدف مراجعه ثبت می‌شود.</p>
            </div>
            <div className="step">
              <div className="step-num">۲</div>
              <h3>شواهد محصول</h3>
              <p>فقط گزینه‌هایی که در سیستم تأیید و موجودند.</p>
            </div>
            <div className="step">
              <div className="step-num">۳</div>
              <h3>پیشنهاد قابل توضیح</h3>
              <p>اگر منطبقی نباشد، صادقانه اعلام می‌شود — نه داده جعلی.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="products" id="products">
        <div className="container">
          <h2>نمونه‌ای از محصولات تأییدشده</h2>
          {productsLoading && (
            <p className="product-state">در حال بارگذاری کاتالوگ…</p>
          )}
          {productError && (
            <p className="product-state product-state-error">
              اتصال به سرور محصولات برقرار نشد. Backend را روی پورت ۸۰۰۰ بررسی
              کنید.
              <span className="product-state-detail">{productError}</span>
            </p>
          )}
          {!productsLoading && !productError && products.length === 0 && (
            <p className="product-state">
              در حال حاضر محصول تأییدشده‌ای برای نمایش عمومی نیست.
            </p>
          )}
          <div className="product-grid">
            {products.map((p) => (
              <article key={p.product_id} className="product-card">
                <h4>{p.product_name}</h4>
                <div className="product-brand">{p.brand}</div>
                <div className="product-status">
                  {p.identity_status}
                  {p.qa_verdict ? ` · ${p.qa_verdict}` : ""}
                </div>
                <Link className="product-link" to="/catalog">
                  جزئیات در کاتالوگ
                </Link>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="transparency">
        <div className="container">
          <h2>شفافیت</h2>
          <p>
            HBI پرونده پزشکی نیست و تشخیص درمان ارائه نمی‌دهد. پیشنهادها بر اساس
            داده محصول، موجودی و نیاز اعلام‌شده شماست. اگر شواهد کافی نباشد،
            سیستم محصولی ابداع نمی‌کند.
          </p>
        </div>
      </section>

      <section className="consultation" id="consult">
        <div className="container">
          <h2>شروع مشاوره در گالری</h2>
          <p>نام و نیاز امروز کافی است — موبایل اجباری نیست.</p>

          {intakeResult ? (
            <div className="consult-success">
              <p className="consult-success-title">مراجعه ثبت شد.</p>
              <p className="consult-success-meta">
                می‌توانید ادامه دهید و پیشنهادهای مبتنی بر شواهد را ببینید. اگر
                موردی نباشد، پیام خالی بودن نتیجه طبیعی است.
              </p>
              <div className="hero-actions" style={{ marginTop: "1.5rem" }}>
                <button type="button" className="cta-consult" onClick={goToRecommendation}>
                  مشاهده پیشنهادها
                </button>
                <button
                  type="button"
                  className="cta-hero-secondary"
                  onClick={() => setIntakeResult(null)}
                >
                  ثبت مراجعه دیگر
                </button>
              </div>
            </div>
          ) : (
            <form className="consult-form" onSubmit={handleIntake}>
              <label htmlFor="home-name">نام</label>
              <input
                id="home-name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="مثلاً سارا"
                autoComplete="name"
                required
              />

              <label htmlFor="home-concerns">توضیح کوتاه (اختیاری)</label>
              <textarea
                id="home-concerns"
                value={concerns}
                onChange={(e) => setConcerns(e.target.value)}
                placeholder="اگر چیزی فراتر از دکمه‌های بالا دارید بنویسید…"
                rows={3}
              />

              {mergedConcerns && (
                <p className="need-hint">
                  خلاصه نیاز ارسالی: <strong>{mergedConcerns}</strong>
                </p>
              )}

              {intakeError && (
                <div className="consult-error" role="alert">
                  {intakeError}
                </div>
              )}

              <button type="submit" className="cta-consult" disabled={intakeBusy}>
                {intakeBusy ? "در حال ثبت…" : "ثبت و ادامه"}
              </button>
            </form>
          )}
        </div>
      </section>

      <footer className="footer">
        <div className="container">
          گالری مقصودی · انتخاب آگاهانه · HBI Pilot
        </div>
      </footer>
    </div>
  );
}
