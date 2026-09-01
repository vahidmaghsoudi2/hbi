import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  listProducts,
  pilotToken,
  customerIntake,
  createGuest,
  generateRecommendations,
  createSale,
  getTotalSales,
} from "../api/client";
import ProductIntakePanel from "./ProductIntakePanel";
import type {
  ProductDTO,
  RecommendationDTO,
  PilotTokenRequest,
  CustomerIntakeRequest,
  GuestCreateRequest,
  SaleDTO,
} from "../types/api";

const CONCERN_OPTIONS = [
  { id: "spf", value: "ضدآفتاب", label: "ضدآفتاب / SPF" },
  { id: "hydrate", value: "آبرسان", label: "آبرسانی پوست" },
  { id: "spot", value: "لک صورت", label: "لک و تیرگی" },
  { id: "sensitive", value: "پوست حساس", label: "حساسیت / قرمزی" },
  { id: "hair", value: "مراقبت مو", label: "مراقبت مو" },
  { id: "scalp", value: "پوست سر", label: "پوست سر" },
  { id: "antiage", value: "ضدچروک", label: "ضدچروک" },
  { id: "oil", value: "کنترل چربی", label: "پوست چرب" },
] as const;

const SKIN_OPTIONS = ["خشک", "چرب", "مختلط", "معمولی", "حساس"] as const;

type Panel = "consult" | "profile" | "catalog" | "intake" | "results" | "sales" | "about";

export default function NewHomePage() {
  const [active, setActive] = useState<Panel>("consult");
  const [token, setToken] = useState<string | null>(() => sessionStorage.getItem("hbi_access_token"));
  const [customerId, setCustomerId] = useState<string | null>(() => sessionStorage.getItem("hbi_customer_id"));
  const [caseId, setCaseId] = useState<string | null>(() => sessionStorage.getItem("hbi_case_id"));
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
  const [saleProductId, setSaleProductId] = useState("");
  const [saleQty, setSaleQty] = useState(1);
  const [salePrice, setSalePrice] = useState(0);
  const [saleBusy, setSaleBusy] = useState(false);
  const [lastSale, setLastSale] = useState<SaleDTO | null>(null);
  const [totalSales, setTotalSales] = useState<number | null>(null);
  const [editProduct, setEditProduct] = useState<ProductDTO | null>(null);

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

  const refreshSalesTotal = useCallback(async () => {
    if (!token) {
      setTotalSales(null);
      return;
    }
    try {
      const res = await getTotalSales(token);
      setTotalSales(res.total_sales ?? 0);
    } catch {
      setTotalSales(null);
    }
  }, [token]);

  useEffect(() => {
    if (active === "sales") void refreshSalesTotal();
  }, [active, refreshSalesTotal]);

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
    if (!currentToken) {
      const guest = (await createGuest({
        name: displayName,
        consent: consent ? 1 : 0,
        concerns: concernsForGuest || undefined,
      })) as { customer_id?: string };
      if (!guest?.customer_id) throw new Error("ایجاد پروفایل مهمان ناموفق بود.");
      sessionStorage.setItem("hbi_customer_id", guest.customer_id);
      setCustomerId(guest.customer_id);
      const pair = await pilotToken({ customer_id: guest.customer_id } as PilotTokenRequest);
      sessionStorage.setItem("hbi_access_token", pair.access_token);
      sessionStorage.setItem("hbi_refresh_token", pair.refresh_token);
      currentToken = pair.access_token;
      setToken(currentToken);
    }
    return currentToken as string;
  }

  async function runFullFlow(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setStatusMsg(null);
    setRecDone(false);
    setRecs([]);
    if (!name.trim()) return setError("نام الزامی است.");
    if (!consent) return setError("رضایت ذخیره اطلاعات را تأیید کنید.");
    if (!concernsText) return setError("حداقل یک موضوع یا نوع پوست را انتخاب کنید.");
    setBusy(true);
    try {
      const currentToken = await ensureSession(name.trim(), concernsText);
      sessionStorage.setItem("hbi_concerns", concernsText);
      const intake = (await customerIntake(
        {
          name: name.trim(),
          mobile: isGuest || !mobile.trim() ? undefined : mobile.trim(),
          concerns: concernsText,
          consent: 1,
          skin_profile: skin.length ? skin.join(",") : undefined,
          guest: isGuest || !mobile.trim(),
          open_case: true,
        } as CustomerIntakeRequest,
        currentToken
      )) as { case?: { case_id?: string }; customer?: { customer_id?: string } };
      if (intake?.customer?.customer_id) {
        sessionStorage.setItem("hbi_customer_id", intake.customer.customer_id);
        setCustomerId(intake.customer.customer_id);
      }
      const newCaseId = intake?.case?.case_id;
      if (!newCaseId) throw new Error("پرونده مشاوره ساخته نشد.");
      sessionStorage.setItem("hbi_case_id", newCaseId);
      setCaseId(newCaseId);
      setStatusMsg("مراجعه ثبت شد. در حال دریافت پیشنهاد…");
      const list = await generateRecommendations(
        { case_id: newCaseId, customer_profile: { concerns: concernsText, skin_type: skin.join(",") || undefined } },
        currentToken
      );
      setRecs(Array.isArray(list) ? list : []);
      setRecDone(true);
      setStatusMsg(list?.length ? `${list.length} پیشنهاد آماده است.` : "پیشنهادی با شواهد کافی یافت نشد.");
      setActive("results");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  function clearSession() {
    ["hbi_access_token", "hbi_refresh_token", "hbi_customer_id", "hbi_case_id", "hbi_concerns"].forEach((k) =>
      sessionStorage.removeItem(k)
    );
    setToken(null);
    setCustomerId(null);
    setCaseId(null);
    setRecs([]);
    setRecDone(false);
    setStatusMsg("نشست پاک شد.");
  }

  async function onSaleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    if (!token || !customerId) return setError("ابتدا مشاوره را ثبت کنید.");
    if (!saleProductId.trim()) return setError("محصول را انتخاب کنید.");
    if (saleQty < 1) return setError("تعداد نامعتبر است.");
    setSaleBusy(true);
    try {
      const sale = await createSale(
        {
          customer_id: customerId,
          items: [{ product_id: saleProductId.trim(), quantity: saleQty, unit_price_toman: salePrice }],
        },
        token
      );
      setLastSale(sale);
      setStatusMsg(`فروش ثبت شد: ${sale.sale_id ?? "OK"}`);
      await refreshSalesTotal();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setSaleBusy(false);
    }
  }

  const nav: [Panel, string][] = [
    ["consult", "مشاوره"],
    ["profile", "پروفایل"],
    ["catalog", "محصولات"],
    ["intake", "ورود محصول"],
    ["results", "پیشنهادها"],
    ["sales", "فروش"],
    ["about", "درباره HBI"],
  ];

  return (
    <div className="home-root pro-home">
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
            {nav.map(([id, label]) => (
              <button key={id} type="button" className={active === id ? "pro-nav-btn on" : "pro-nav-btn"} onClick={() => go(id)}>
                {label}
              </button>
            ))}
            <Link to="/accounting" className="pro-nav-btn">
              حسابداری
            </Link>
          </nav>
        </div>
      </header>

      <main className="pro-main">
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

        {active === "consult" && (
          <section className="pro-panel">
            <h1>فرم مشاوره سریع</h1>
            <p className="pro-lead">پروفایل، پرونده و پیشنهاد روی همین صفحه ساخته می‌شود.</p>
            <form className="pro-form" onSubmit={runFullFlow}>
              <fieldset className="pro-fieldset">
                <legend>۱) هویت</legend>
                <div className="pro-grid-2">
                  <div>
                    <label className="pro-label" htmlFor="name">نام *</label>
                    <input id="name" className="pro-input" value={name} onChange={(e) => setName(e.target.value)} placeholder="نام مشتری" />
                  </div>
                  <div>
                    <label className="pro-label" htmlFor="mobile">موبایل</label>
                    <input id="mobile" className="pro-input" value={mobile} onChange={(e) => setMobile(e.target.value)} placeholder="09…" disabled={isGuest} />
                  </div>
                </div>
                <label className="pro-check">
                  <input type="checkbox" checked={isGuest} onChange={(e) => setIsGuest(e.target.checked)} />
                  مراجعه مهمان (بدون موبایل)
                </label>
                <label className="pro-check">
                  <input type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} />
                  رضایت ذخیره اطلاعات
                </label>
              </fieldset>
              <fieldset className="pro-fieldset">
                <legend>۲) موضوع مشاوره</legend>
                <div className="pro-checks">
                  {CONCERN_OPTIONS.map((c) => (
                    <label key={c.id} className="pro-check-card">
                      <input type="checkbox" checked={concerns.includes(c.value)} onChange={() => toggleIn(concerns, c.value, setConcerns)} />
                      <span>{c.label}</span>
                    </label>
                  ))}
                </div>
              </fieldset>
              <fieldset className="pro-fieldset">
                <legend>۳) نوع پوست</legend>
                <div className="pro-checks pro-checks-inline">
                  {SKIN_OPTIONS.map((s) => (
                    <label key={s} className="pro-check-card sm">
                      <input type="checkbox" checked={skin.includes(s)} onChange={() => toggleIn(skin, s, setSkin)} />
                      <span>{s}</span>
                    </label>
                  ))}
                </div>
              </fieldset>
              <fieldset className="pro-fieldset">
                <legend>۴) توضیح</legend>
                <textarea className="pro-input pro-textarea" value={note} onChange={(e) => setNote(e.target.value)} rows={3} placeholder="نکته اختیاری…" />
                {concernsText ? (
                  <p className="pro-summary">
                    خلاصه: <strong>{concernsText}</strong>
                  </p>
                ) : null}
              </fieldset>
              <div className="pro-actions">
                <button type="submit" className="pro-btn-primary" disabled={busy}>
                  {busy ? "در حال اجرا…" : "ثبت مراجعه + دریافت پیشنهاد"}
                </button>
                <button type="button" className="pro-btn-secondary" onClick={() => go("catalog")}>
                  محصولات
                </button>
              </div>
            </form>
          </section>
        )}

        {active === "profile" && (
          <section className="pro-panel">
            <h1>پروفایل و نشست</h1>
            <dl className="pro-dl">
              <div>
                <dt>مشتری</dt>
                <dd>{customerId ?? "—"}</dd>
              </div>
              <div>
                <dt>پرونده</dt>
                <dd>{caseId ?? "—"}</dd>
              </div>
              <div>
                <dt>توکن</dt>
                <dd>{token ? "فعال" : "ندارد"}</dd>
              </div>
              <div>
                <dt>concerns</dt>
                <dd>{sessionStorage.getItem("hbi_concerns") ?? "—"}</dd>
              </div>
            </dl>
            <div className="pro-actions">
              <button type="button" className="pro-btn-secondary" onClick={clearSession}>
                پاک کردن نشست
              </button>
              <button type="button" className="pro-btn-primary" onClick={() => go("consult")}>
                مشاوره
              </button>
            </div>
          </section>
        )}

        {active === "catalog" && (
          <section className="pro-panel">
            <div className="pro-panel-head">
              <h1>محصولات</h1>
              <button type="button" className="pro-btn-secondary" onClick={() => void loadProducts()}>
                نوسازی
              </button>
            </div>
            {catalogLoading && <p className="pro-muted">بارگذاری…</p>}
            {catalogError && <div className="pro-alert">{catalogError}</div>}
            <div className="pro-product-grid">
              {products.map((p) => (
                <article key={p.product_id} className="pro-product-card">
                  <h3>{p.product_name}</h3>
                  <p className="pro-muted">{p.brand}</p>
                  <div className="pro-tags">
                    <span className="pro-tag">{p.identity_status}</span>
                  </div>
                  <code className="pro-code">{p.product_id}</code>
                  <div className="pro-actions" style={{ marginTop: "0.6rem" }}>
                    <button
                      type="button"
                      className="pro-btn-secondary"
                      onClick={() => {
                        setEditProduct(p);
                        go("intake");
                      }}
                    >
                      ویرایش
                    </button>
                  </div>
                </article>
              ))}
            </div>
          </section>
        )}

        {active === "intake" && (
          <ProductIntakePanel
            editProduct={editProduct}
            onCancelEdit={() => setEditProduct(null)}
            onRegistered={() => {
              setEditProduct(null);
              void loadProducts();
              go("catalog");
            }}
          />
        )}

        {active === "results" && (
          <section className="pro-panel">
            <h1>پیشنهادها</h1>
            {!recDone && <p className="pro-muted">هنوز پیشنهادی گرفته نشده — از مشاوره شروع کنید.</p>}
            {recDone && recs.length === 0 && (
              <div className="pro-empty">
                <strong>مورد منطبقی یافت نشد.</strong>
                <p>شواهد کافی نبود؛ سیستم حدس نمی‌زند.</p>
              </div>
            )}
            <div className="pro-rec-list">
              {recs.map((r, i) => (
                <article key={r.recommendation_id || `${r.product_id}-${i}`} className="pro-rec-card">
                  <div className="pro-rec-rank">#{i + 1}</div>
                  <div>
                    <h3>{r.product_id}</h3>
                    <p className="pro-muted">
                      {r.eligibility_status ?? r.eligibility ?? "—"}
                      {r.final_score != null || r.ranking_score != null ? ` · ${r.final_score ?? r.ranking_score}` : ""}
                    </p>
                    {(r.reasoning || r.ranking_reasons) && <p className="pro-reason">{r.reasoning || r.ranking_reasons}</p>}
                  </div>
                </article>
              ))}
            </div>
          </section>
        )}

        {active === "sales" && (
          <section className="pro-panel" id="sales">
            <h1>ثبت فروش</h1>
            <p className="pro-lead">API: POST /api/v1/sales/ و GET /api/v1/sales/total — نیاز به نشست فعال.</p>
            {!token || !customerId ? (
              <div className="pro-empty">
                <strong>ابتدا مشاوره را ثبت کنید.</strong>
                <button type="button" className="pro-btn-primary" onClick={() => go("consult")}>
                  رفتن به مشاوره
                </button>
              </div>
            ) : (
              <form className="pro-form" onSubmit={onSaleSubmit}>
                <fieldset className="pro-fieldset">
                  <legend>مشتری</legend>
                  <p className="pro-muted">
                    <code>{customerId}</code>
                  </p>
                  <p className="pro-muted">جمع فروش: {totalSales === null ? "—" : totalSales.toLocaleString("fa-IR")}</p>
                </fieldset>
                <fieldset className="pro-fieldset">
                  <legend>اقلام</legend>
                  <label className="pro-label" htmlFor="sale-product">
                    محصول
                  </label>
                  <select id="sale-product" className="pro-input" value={saleProductId} onChange={(e) => setSaleProductId(e.target.value)}>
                    <option value="">— انتخاب از کاتالوگ —</option>
                    {products.map((p) => (
                      <option key={p.product_id} value={p.product_id}>
                        {p.product_name} ({p.brand})
                      </option>
                    ))}
                  </select>
                  <label className="pro-label" htmlFor="sale-manual">
                    یا product_id دستی
                  </label>
                  <input id="sale-manual" className="pro-input" value={saleProductId} onChange={(e) => setSaleProductId(e.target.value)} />
                  <div className="pro-grid-2">
                    <div>
                      <label className="pro-label" htmlFor="sale-qty">
                        تعداد
                      </label>
                      <input id="sale-qty" className="pro-input" type="number" min={1} value={saleQty} onChange={(e) => setSaleQty(Number(e.target.value) || 1)} />
                    </div>
                    <div>
                      <label className="pro-label" htmlFor="sale-price">
                        قیمت واحد (تومان)
                      </label>
                      <input id="sale-price" className="pro-input" type="number" min={0} value={salePrice} onChange={(e) => setSalePrice(Number(e.target.value) || 0)} />
                    </div>
                  </div>
                  <p className="pro-summary">
                    مبلغ: <strong>{(saleQty * salePrice).toLocaleString("fa-IR")}</strong> تومان
                  </p>
                </fieldset>
                <div className="pro-actions">
                  <button type="submit" className="pro-btn-primary" disabled={saleBusy}>
                    {saleBusy ? "در حال ثبت…" : "ثبت فروش"}
                  </button>
                  <button type="button" className="pro-btn-secondary" onClick={() => void refreshSalesTotal()}>
                    بروزرسانی جمع
                  </button>
                </div>
              </form>
            )}
            {lastSale && (
              <div className="pro-rec-card" style={{ marginTop: "1rem" }}>
                <div className="pro-rec-rank">✓</div>
                <div>
                  <h3>آخرین فروش</h3>
                  <p className="pro-muted">
                    {String(lastSale.sale_id ?? "—")} · {Number(lastSale.total_amount_toman ?? 0).toLocaleString("fa-IR")} تومان
                  </p>
                </div>
              </div>
            )}
          </section>
        )}

        {active === "about" && (
          <section className="pro-panel">
            <h1>مسیر HBI روی این صفحه</h1>
            <ol className="pro-ol">
              <li>پروفایل مشتری (intake / guest)</li>
              <li>پرونده Case</li>
              <li>موتور توصیه generate</li>
              <li>کاتالوگ محصولات</li>
              <li>ثبت فروش و کنترل موجودی</li>
            </ol>
          </section>
        )}
      </main>
      <footer className="pro-footer">HBI · گالری مقصودی · مشاوره تا فروش در یک صفحه</footer>
    </div>
  );
}
