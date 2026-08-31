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

/** گزینه‌های قابل‌فهم برای مشتری گالری — نه اصطلاح فنی */
const NEEDS = [
  { value: "ضدآفتاب", label: "ضدآفتاب", hint: "محافظت در برابر آفتاب" },
  { value: "آبرسان", label: "آبرسانی پوست", hint: "خشکی و کمبود رطوبت" },
  { value: "لک صورت", label: "لک و تیرگی", hint: "یکنواخت‌تر شدن پوست" },
  { value: "مراقبت مو", label: "مراقبت مو", hint: "تقویت و سلامت مو" },
  { value: "پوست حساس", label: "پوست حساس", hint: "قرمزی و تحریک" },
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
  const [extraNote, setExtraNote] = useState("");
  const [selected, setSelected] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState(false);

  const [products, setProducts] = useState<ProductDTO[]>([]);
  const [catalogNote, setCatalogNote] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await listProducts();
        if (!cancelled) setProducts(Array.isArray(data) ? data.slice(0, 6) : []);
      } catch {
        if (!cancelled)
          setCatalogNote(
            "فهرست محصولات فعلاً در دسترس نیست (سرور را روشن کنید)."
          );
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const concernsText = useMemo(() => {
    const parts = [...selected];
    if (extraNote.trim()) parts.push(extraNote.trim());
    return parts.join(", ");
  }, [selected, extraNote]);

  function toggle(value: string) {
    setSelected((prev) =>
      prev.includes(value) ? prev.filter((v) => v !== value) : [...prev, value]
    );
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    if (!name.trim()) {
      setError("لطفاً نام خود را بنویسید.");
      return;
    }
    if (!concernsText) {
      setError("حداقل یک موضوع از دکمه‌های بالا انتخاب کنید.");
      return;
    }
    setBusy(true);
    try {
      let currentToken = token;
      let currentCustomerId = customerId;

      if (!currentToken) {
        const guestBody: GuestCreateRequest = {
          name: name.trim(),
          consent: 1,
          concerns: concernsText,
        };
        const guest = (await createGuest(guestBody)) as { customer_id?: string };
        if (!guest?.customer_id) throw new Error("ثبت مراجعه انجام نشد.");
        currentCustomerId = guest.customer_id;
        sessionStorage.setItem("hbi_customer_id", currentCustomerId);
        setCustomerId(currentCustomerId);

        const tokenBody: PilotTokenRequest = { customer_id: currentCustomerId };
        const pair = await pilotToken(tokenBody);
        sessionStorage.setItem("hbi_access_token", pair.access_token);
        sessionStorage.setItem("hbi_refresh_token", pair.refresh_token);
        currentToken = pair.access_token;
        setToken(currentToken);
      }

      sessionStorage.setItem("hbi_concerns", concernsText);

      const intakeBody: CustomerIntakeRequest = {
        name: name.trim(),
        concerns: concernsText,
        consent: 1,
        open_case: true,
      };
      const result = (await customerIntake(
        intakeBody,
        currentToken as string
      )) as {
        case?: { case_id?: string };
        customer?: { customer_id?: string };
      };
      if (result?.case?.case_id) {
        sessionStorage.setItem("hbi_case_id", result.case.case_id);
      }
      if (result?.customer?.customer_id) {
        sessionStorage.setItem("hbi_customer_id", result.customer.customer_id);
        setCustomerId(result.customer.customer_id);
      }
      setDone(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="home-root">
      {/* —— نوار بالا —— */}
      <header className="hm-top">
        <div className="hm-wrap hm-top-inner">
          <div>
            <div className="hm-logo">گالری مقصودی</div>
            <div className="hm-logo-sub">مراقبت پوست و مو · انتخاب آگاهانه</div>
          </div>
          <Link className="hm-link" to="/catalog">
            فهرست محصولات
          </Link>
        </div>
      </header>

      {/* —— پیام اصلی —— */}
      <section className="hm-hero hm-wrap">
        <p className="hm-eyebrow">این صفحه برای چیست؟</p>
        <h1>
          بگویید امروز به چه چیزی نیاز دارید؛
          <br />
          <span className="hm-accent">ما محصول مناسب را از روی شواهد پیشنهاد می‌دهیم.</span>
        </h1>
        <p className="hm-lead">
          سه قدم ساده: انتخاب موضوع → نوشتن نام → دیدن پیشنهاد.
          اگر محصول مطمئنی نباشد، چیزی به‌زور نشان داده نمی‌شود.
        </p>
      </section>

      {/* —— مسیر واضح —— */}
      <section className="hm-wrap hm-path" aria-label="مراحل">
        <div className="hm-path-item">
          <span className="hm-num">۱</span>
          <span>موضوع را انتخاب کنید</span>
        </div>
        <div className="hm-path-item">
          <span className="hm-num">۲</span>
          <span>نام خود را بنویسید</span>
        </div>
        <div className="hm-path-item">
          <span className="hm-num">۳</span>
          <span>پیشنهاد محصول را ببینید</span>
        </div>
      </section>

      {/* —— فرم اصلی —— */}
      <section className="hm-wrap hm-main">
        {done ? (
          <div className="hm-card hm-success">
            <h2>مراجعه شما ثبت شد</h2>
            <p>
              حالا می‌توانید پیشنهادهای مرتبط با «{concernsText}» را ببینید.
              اگر موردی پیدا نشود، صفحه خالی می‌ماند — این یعنی سیستم حدس نمی‌زند.
            </p>
            <button
              type="button"
              className="hm-btn-primary"
              onClick={() => navigate("/recommendation")}
            >
              نمایش پیشنهادها
            </button>
            <button
              type="button"
              className="hm-btn-ghost"
              onClick={() => setDone(false)}
            >
              شروع دوباره
            </button>
          </div>
        ) : (
          <form className="hm-card" onSubmit={onSubmit}>
            <h2 className="hm-step-title">
              <span className="hm-num">۱</span> امروز برای چه موضوعی آمده‌اید؟
            </h2>
            <p className="hm-help">می‌توانید چند مورد را انتخاب کنید.</p>
            <div className="hm-chips">
              {NEEDS.map((n) => {
                const on = selected.includes(n.value);
                return (
                  <button
                    key={n.value}
                    type="button"
                    className={on ? "hm-chip hm-chip-on" : "hm-chip"}
                    onClick={() => toggle(n.value)}
                    aria-pressed={on}
                  >
                    <strong>{n.label}</strong>
                    <small>{n.hint}</small>
                  </button>
                );
              })}
            </div>

            <h2 className="hm-step-title">
              <span className="hm-num">۲</span> نام شما
            </h2>
            <input
              className="hm-input"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="مثلاً سارا"
              autoComplete="name"
            />

            <label className="hm-label" htmlFor="note">
              توضیح اضافه (اختیاری)
            </label>
            <textarea
              id="note"
              className="hm-input hm-textarea"
              value={extraNote}
              onChange={(e) => setExtraNote(e.target.value)}
              placeholder="اگر نکته‌ای دارید کوتاه بنویسید…"
              rows={2}
            />

            {concernsText ? (
              <p className="hm-summary">
                خلاصه درخواست شما: <strong>{concernsText}</strong>
              </p>
            ) : null}

            {error ? (
              <div className="hm-error" role="alert">
                {error}
              </div>
            ) : null}

            <button type="submit" className="hm-btn-primary" disabled={busy}>
              {busy ? "در حال ثبت…" : "۳ — ثبت و رفتن به پیشنهاد محصول"}
            </button>
          </form>
        )}
      </section>

      {/* —— محصولات: فقط برای آشنایی، نه جعبه فنی —— */}
      <section className="hm-wrap hm-catalog">
        <h2>نمونه‌ای از محصولات موجود در گالری</h2>
        <p className="hm-help">
          این‌ها از فهرست واقعی سیستم خوانده می‌شوند؛ برای پیشنهاد شخصی از فرم
          بالا استفاده کنید.
        </p>
        {catalogNote ? <p className="hm-help">{catalogNote}</p> : null}
        <div className="hm-grid">
          {products.map((p) => (
            <article key={p.product_id} className="hm-prod">
              <h3>{p.product_name}</h3>
              <p>{p.brand}</p>
            </article>
          ))}
        </div>
        <Link className="hm-link-center" to="/catalog">
          مشاهده همه محصولات →
        </Link>
      </section>

      <footer className="hm-foot">
        <div className="hm-wrap">
          گالری مقصودی · پیشنهاد بر اساس شواهد محصول · بدون ادعای پزشکی ساختگی
        </div>
      </footer>
    </div>
  );
}
