import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import {
  listProducts,
  pilotToken,
  customerIntake,
  createGuest,
  generateRecommendations,
} from "../api/client";
import type {
  ProductDTO,
  RecommendationDTO,
  PilotTokenRequest,
  CustomerIntakeRequest,
  GuestCreateRequest,
} from "../types/api";

/** موضوعات مشاوره — چک‌باکس‌های واقعی مسیر HBI */
const CONCERN_OPTIONS = [
  { id: "spf", value: "ضدآفتاب", label: "ضدآفتاب / SPF" },
  { id: "hydrate", value: "آبرسان", label: "آبرسانی و رطوبت پوست" },
  { id: "spot", value: "لک صورت", label: "لک، تیرگی، یکنواختی" },
  { id: "sensitive", value: "پوست حساس", label: "حساسیت / قرمزی" },
  { id: "hair", value: "مراقبت مو", label: "مراقبت و تقویت مو" },
  { id: "scalp", value: "پوست سر", label: "پوست سر / شوره" },
  { id: "antiage", value: "ضدچروک", label: "خطوط و چروک" },
  { id: "oil", value: "کنترل چربی", label: "پوست چرب / جوش" },
] as const;

const SKIN_OPTIONS = [
  { id: "dry", label: "خشک" },
  { id: "oily", label: "چرب" },
  { id: "combo", label: "مختلط" },
  { id: "normal", label: "معمولی" },
  { id: "sensitive_skin", label: "حساس" },
] as const;

type Panel = "consult" | "profile" | "catalog" | "results" | "about";

export default function NewHomePage() {
  const [active, setActive] = useState<Panel>("consult");

  const [token, setToken] = useState<string | null>(() =>
    sessionStorage.getItem("hbi_access_token")
  );
  const [customerId, setCustomerId] = useState<string | null>(() =>
    sessionStorage.getItem("hbi_customer_id")
  );
  const [caseId, setCaseId] = useState<string | null>(() =>
    sessionStorage.getItem("hbi_case_id")
  );

  const [name, setName] = useState("");
  const [mobile, setMobile] = useState("");
  const [isGuest, setIsGuest] = useState(true);
  const [consent, setConsent] = useState(true);
  const [concerns, setConcerns] = useState<string[]>([]);
  const [skin, setSkin] = useState<string[]>([]);
  const [note, setNote] = useState("");

  const [busy, setBusy] = useState(false);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [products, setProducts] = useState<ProductDTO[]>([]);
  const [catalogError, setCatalogError] = useState<string | null>(null);
  const [catalogLoading, setCatalogLoading] = useState(true);

  const [recs, setRecs] = useState<RecommendationDTO[]>([]);
  const [recDone, setRecDone] = useState(false);

  const loadProducts = useCallback(async () => {
    setCatalogLoading(true);
    setCatalogError(null);
    try {
      const data = await listProducts();
      setProducts(Array.isArray(data) ? data : []);
    } catch (e) {
      setCatalogError(e instanceof Error ? e.message : String(e));
      setProducts([]);
    } finally {
      setCatalogLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadProducts();
  }, [loadProducts]);

  const concernsText = useMemo(() => {
    const parts = [...concerns, ...skin.map((s) => `پوست ${s}`)];
    if (note.trim()) parts.push(note.trim());
    return parts.join(", ");
  }, [concerns, skin, note]);

  function toggleIn(list: string[], value: string, setter: (v: string[]) => void) {
    setter(list.includes(value) ? list.filter((x) => x !== value) : [...list, value]);
  }

  function go(panel: Panel) {
    setActive(panel);
    setError(null);
  }

  async function ensureSession(displayName: string, concernsForGuest: string) {
    let currentToken = token;
    let currentCustomerId = customerId;

    if (!currentToken) {
      const guestBody: GuestCreateRequest = {
        name: displayName,
        consent: consent ? 1 : 0,
        concerns: concernsForGuest || undefined,
      };
      const guest = (await createGuest(guestBody)) as { customer_id?: string };
      if (!guest?.customer_id) throw new Error("ایجاد پروفایل مهمان ناموفق بود.");
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
    return { currentToken: currentToken as string, currentCustomerId };
  }

  async function runFullFlow(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setStatusMsg(null);
    setRecDone(false);
    setRecs([]);

    if (!name.trim()) {
      setError("نام الزامی است.");
      return;
    }
    if (!consent) {
      setError("برای ثبت مراجعه، رضایت ذخیره اطلاعات را تأیید کنید.");
      return;
    }
    if (!concernsText) {
      setError("حداقل یک موضوع مشاوره یا نوع پوست را انتخاب کنید.");
      return;
    }

    setBusy(true);
    try {
      const { currentToken } = await ensureSession(name.trim(), concernsText);
      sessionStorage.setItem("hbi_concerns", concernsText);

      const intakeBody: CustomerIntakeRequest = {
        name: name.trim(),
        mobile: isGuest || !mobile.trim() ? undefined : mobile.trim(),
        concerns: concernsText,
        consent: 1,
        skin_profile: skin.length ? skin.join(",") : undefined,
        guest: isGuest || !mobile.trim(),
        open_case: true,
      };

      const intake = (await customerIntake(intakeBody, currentToken)) as {
        case?: { case_id?: string };
        customer?: { customer_id?: string };
        recommendation_profile?: { concerns?: string };
      };

      const newCaseId = intake?.case?.case_id;
      if (intake?.customer?.customer_id) {
        sessionStorage.setItem("hbi_customer_id", intake.customer.customer_id);
        setCustomerId(intake.customer.customer_id);
      }
      if (!newCaseId) throw new Error("پرونده مشاوره (Case) ساخته نشد.");
      sessionStorage.setItem("hbi_case_id", newCaseId);
      setCaseId(newCaseId);

      setStatusMsg("مراجعه و پرونده ثبت شد. در حال دریافت پیشنهاد…");

      const profile = {
        concerns: concernsText,
        skin_type: skin.join(",") || undefined,
      };
      const list = await generateRecommendations(
        { case_id: newCaseId, customer_profile: profile },
        currentToken
      );
      setRecs(Array.isArray(list) ? list : []);
      setRecDone(true);
      setStatusMsg(
        list?.length
          ? `${list.length} پیشنهاد بر اساس شواهد آماده است.`
          : "پیشنهادی با شواهد کافی یافت نشد (رفتار صحیح سیستم — بدون حدس)."
      );
      setActive("results");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  function clearSession() {
    sessionStorage.removeItem("hbi_access_token");
    sessionStorage.removeItem("hbi_refresh_token");
    sessionStorage.removeItem("hbi_customer_id");
    sessionStorage.removeItem("hbi_case_id");
    sessionStorage.removeItem("hbi_concerns");
    setToken(null);
    setCustomerId(null);
    setCaseId(null);
    setRecs([]);
    setRecDone(false);
    setStatusMsg("نشست پاک شد.");
  }

  return (
    <div className="home-root pro-home">
      {/* ===== منوی اصلی ===== */}
      <header className="pro-header">
        <div className="pro-header-inner">
          <div className="pro-brand">
            <span className="pro-brand-mark">HBI</span>
            <div>
              <div className="pro-brand-title">گالری مقصودی</div>
              <div className="pro-brand-sub">هوش زیبایی و مراقبت · یک صفحه کامل</div>
            </div>
          </div>
          <nav className="pro-nav" aria-label="بخش‌های صفحه">
            {(
              [
                ["consult", "مشاوره"],
                ["profile", "پروفایل"],
                ["catalog", "محصولات"],
                ["results", "پیشنهادها"],
                ["about", "درباره HBI"],
              ] as [Panel, string][]
            ).map(([id, label]) => (
              <button
                key={id}
                type="button"
                className={active === id ? "pro-nav-btn on" : "pro-nav-btn"}
                onClick={() => go(id)}
              >
                {label}
              </button>
            ))}
          </nav>
        </div>
      </header>

      <main className="pro-main">
        {/* نوار وضعیت زنده */}
        <div className="pro-status-bar">
          <span className={token ? "dot on" : "dot"} />
          <span>{token ? "نشست فعال" : "نشست ندارد"}</span>
          <span className="sep">|</span>
          <span>مشتری: {customerId ?? "—"}</span>
          <span className="sep">|</span>
          <span>پرونده: {caseId ?? "—"}</span>
          {statusMsg ? (
            <>
              <span className="sep">|</span>
              <span className="pro-status-msg">{statusMsg}</span>
            </>
          ) : null}
        </div>

        {error ? (
          <div className="pro-alert" role="alert">
            {error}
          </div>
        ) : null}

        {/* ===== پنل مشاوره ===== */}
        {active === "consult" && (
          <section className="pro-panel" id="consult">
            <h1>فرم مشاوره سریع</h1>
            <p className="pro-lead">
              با تکمیل این بخش، پروفایل مشتری، پرونده (Case) و پیشنهاد محصول روی
              همین صفحه ساخته می‌شود.
            </p>

            <form className="pro-form" onSubmit={runFullFlow}>
              <fieldset className="pro-fieldset">
                <legend>۱) هویت مراجعه</legend>
                <div className="pro-grid-2">
                  <div>
                    <label className="pro-label" htmlFor="name">
                      نام <abbr title="الزامی">*</abbr>
                    </label>
                    <input
                      id="name"
                      className="pro-input"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      placeholder="نام مشتری"
                      autoComplete="name"
                    />
                  </div>
                  <div>
                    <label className="pro-label" htmlFor="mobile">
                      موبایل (اختیاری)
                    </label>
                    <input
                      id="mobile"
                      className="pro-input"
                      value={mobile}
                      onChange={(e) => setMobile(e.target.value)}
                      placeholder="09…"
                      disabled={isGuest}
                      inputMode="tel"
                    />
                  </div>
                </div>
                <label className="pro-check">
                  <input
                    type="checkbox"
                    checked={isGuest}
                    onChange={(e) => setIsGuest(e.target.checked)}
                  />
                  مراجعه مهمان (بدون موبایل)
                </label>
                <label className="pro-check">
                  <input
                    type="checkbox"
                    checked={consent}
                    onChange={(e) => setConsent(e.target.checked)}
                  />
                  رضایت به ذخیره اطلاعات مراجعه برای مشاوره و پیگیری
                </label>
              </fieldset>

              <fieldset className="pro-fieldset">
                <legend>۲) موضوع مشاوره (چک‌باکس)</legend>
                <div className="pro-checks">
                  {CONCERN_OPTIONS.map((c) => (
                    <label key={c.id} className="pro-check-card">
                      <input
                        type="checkbox"
                        checked={concerns.includes(c.value)}
                        onChange={() => toggleIn(concerns, c.value, setConcerns)}
                      />
                      <span>{c.label}</span>
                    </label>
                  ))}
                </div>
              </fieldset>

              <fieldset className="pro-fieldset">
                <legend>۳) نوع پوست (اختیاری)</legend>
                <div className="pro-checks pro-checks-inline">
                  {SKIN_OPTIONS.map((s) => (
                    <label key={s.id} className="pro-check-card sm">
                      <input
                        type="checkbox"
                        checked={skin.includes(s.label)}
                        onChange={() => toggleIn(skin, s.label, setSkin)}
                      />
                      <span>{s.label}</span>
                    </label>
                  ))}
                </div>
              </fieldset>

              <fieldset className="pro-fieldset">
                <legend>۴) توضیح آزاد</legend>
                <textarea
                  className="pro-input pro-textarea"
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                  rows={3}
                  placeholder="نکته‌ای که فروشنده یا مشتری می‌خواهد ثبت شود…"
                />
                {concernsText ? (
                  <p className="pro-summary">
                    خلاصه ارسالی به موتور توصیه: <strong>{concernsText}</strong>
                  </p>
                ) : null}
              </fieldset>

              <div className="pro-actions">
                <button type="submit" className="pro-btn-primary" disabled={busy}>
                  {busy
                    ? "در حال اجرا…"
                    : "ثبت مراجعه + دریافت پیشنهاد روی همین صفحه"}
                </button>
                <button
                  type="button"
                  className="pro-btn-secondary"
                  onClick={() => go("catalog")}
                >
                  فقط مشاهده محصولات
                </button>
              </div>
            </form>
          </section>
        )}

        {/* ===== پروفایل / نشست ===== */}
        {active === "profile" && (
          <section className="pro-panel">
            <h1>پروفایل و نشست جاری</h1>
            <p className="pro-lead">
              اطلاعات از session مرورگر و API واحد پروفایل مشتری خوانده می‌شود.
            </p>
            <dl className="pro-dl">
              <div>
                <dt>شناسه مشتری</dt>
                <dd>{customerId ?? "هنوز ثبت نشده"}</dd>
              </div>
              <div>
                <dt>شناسه پرونده (Case)</dt>
                <dd>{caseId ?? "—"}</dd>
              </div>
              <div>
                <dt>توکن دسترسی</dt>
                <dd>{token ? "فعال (در sessionStorage)" : "ندارد"}</dd>
              </div>
              <div>
                <dt>آخرین concerns</dt>
                <dd>{sessionStorage.getItem("hbi_concerns") ?? "—"}</dd>
              </div>
              <div>
                <dt>نام فرم</dt>
                <dd>{name || "—"}</dd>
              </div>
            </dl>
            <div className="pro-actions">
              <button type="button" className="pro-btn-secondary" onClick={clearSession}>
                پاک کردن نشست
              </button>
              <button type="button" className="pro-btn-primary" onClick={() => go("consult")}>
                بازگشت به مشاوره
              </button>
            </div>
          </section>
        )}

        {/* ===== کاتالوگ ===== */}
        {active === "catalog" && (
          <section className="pro-panel">
            <div className="pro-panel-head">
              <h1>محصولات تأییدشده</h1>
              <button type="button" className="pro-btn-secondary" onClick={() => void loadProducts()}>
                نوسازی فهرست
              </button>
            </div>
            <p className="pro-lead">منبع: GET /api/v1/products/ — بدون داده جعلی</p>
            {catalogLoading && <p className="pro-muted">در حال بارگذاری…</p>}
            {catalogError && (
              <div className="pro-alert">
                اتصال برقرار نشد. Backend را روی پورت ۸۰۰۰ بررسی کنید.
                <div className="pro-muted">{catalogError}</div>
              </div>
            )}
            {!catalogLoading && !catalogError && products.length === 0 && (
              <p className="pro-muted">محصولی برای نمایش نیست.</p>
            )}
            <div className="pro-product-grid">
              {products.map((p) => (
                <article key={p.product_id} className="pro-product-card">
                  <h3>{p.product_name}</h3>
                  <p className="pro-muted">{p.brand}</p>
                  <div className="pro-tags">
                    <span className="pro-tag">{p.identity_status}</span>
                    {p.qa_verdict ? <span className="pro-tag">{p.qa_verdict}</span> : null}
                  </div>
                  <code className="pro-code">{p.product_id}</code>
                </article>
              ))}
            </div>
          </section>
        )}

        {/* ===== نتایج توصیه ===== */}
        {active === "results" && (
          <section className="pro-panel">
            <h1>پیشنهادهای این مراجعه</h1>
            <p className="pro-lead">
              خروجی موتور توصیه برای پرونده فعلی — روی همین صفحه، بدون خروج.
            </p>
            {!recDone && (
              <p className="pro-muted">
                هنوز پیشنهادی گرفته نشده. از منوی «مشاوره» فرم را تکمیل و ارسال
                کنید.
              </p>
            )}
            {recDone && recs.length === 0 && (
              <div className="pro-empty">
                <strong>مورد منطبقی یافت نشد.</strong>
                <p>
                  این حالت عادی است وقتی شواهد محصول با نیاز هم‌خوان نیست —
                  سیستم چیزی اختراع نمی‌کند.
                </p>
                <button type="button" className="pro-btn-primary" onClick={() => go("consult")}>
                  تغییر موضوعات و تلاش دوباره
                </button>
              </div>
            )}
            <div className="pro-rec-list">
              {recs.map((r, i) => (
                <article key={r.recommendation_id || `${r.product_id}-${i}`} className="pro-rec-card">
                  <div className="pro-rec-rank">#{i + 1}</div>
                  <div>
                    <h3>{r.product_id}</h3>
                    <p className="pro-muted">
                      وضعیت: {r.eligibility_status ?? r.eligibility ?? "—"}
                      {(r.final_score != null || r.ranking_score != null) && (
                        <> · امتیاز: {r.final_score ?? r.ranking_score}</>
                      )}
                    </p>
                    {(r.reasoning || r.ranking_reasons) && (
                      <p className="pro-reason">{r.reasoning || r.ranking_reasons}</p>
                    )}
                  </div>
                </article>
              ))}
            </div>
          </section>
        )}

        {/* ===== درباره ===== */}
        {active === "about" && (
          <section className="pro-panel">
            <h1>HBI روی این صفحه چه می‌کند؟</h1>
            <ol className="pro-ol">
              <li>
                <strong>پروفایل مشتری:</strong> نام، رضایت، موضوعات، نوع پوست →
                API intake / guest
              </li>
              <li>
                <strong>پرونده مشاوره (Case):</strong> با open_case ساخته می‌شود
              </li>
              <li>
                <strong>موتور توصیه:</strong> generate با customer_profile.concerns
              </li>
              <li>
                <strong>کاتالوگ:</strong> محصولات تأییدشده از backend
              </li>
              <li>
                <strong>شفافیت:</strong> لیست خالی = نبود شواهد کافی، نه باگ
              </li>
            </ol>
            <p className="pro-muted">
              امتیازدهی و Seed محصول تغییر داده نمی‌شوند؛ این صفحه فقط رابط
              یکپارچه همان قابلیت‌هاست.
            </p>
          </section>
        )}
      </main>

      <footer className="pro-footer">
        HBI · گالری مقصودی · مشاوره مبتنی بر شواهد · یک صفحه برای کل مسیر
      </footer>
    </div>
  );
}
