import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  listProducts,
  listManageableProducts,
  pilotToken,
  pilotOperatorToken,
  customerIntake,
  createGuest,
  generateRecommendations,
  createSale,
  getTotalSales,
  getCustomerById,
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
  const [profileSaving, setProfileSaving] = useState(false);

  const loadProducts = useCallback(async () => {
    setCatalogLoading(true);
    setCatalogError(null);
    try {
      const operatorToken = await ensureProductSession();
      if (!operatorToken) throw new Error("نشست اپراتور برای مشاهده محصولات در دسترس نیست.");
      const data = await listManageableProducts(operatorToken);
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
        consent: 0,
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

  async function ensureProductSession(): Promise<string | null> {
    const cached = sessionStorage.getItem("hbi_operator_access_token");
    if (cached) return cached;
    const pair = await pilotOperatorToken();
    sessionStorage.setItem("hbi_operator_access_token", pair.access_token);
    return pair.access_token;
  }

  async function loadActiveCustomerProfile() {
    if (!token || !customerId) return;
    try {
      const profile = (await getCustomerById(customerId, token)) as { name?: string; mobile?: string | null; concerns?: string | null; skin_profile?: string | null };
      if (profile.name) setName(profile.name);
      if (profile.mobile) {
        setMobile(profile.mobile);
      }
      if (profile.concerns) {
        const saved = profile.concerns.split(",").map((x) => x.trim()).filter(Boolean);
        setConcerns((prev) => prev.length ? prev : CONCERN_OPTIONS.filter((x) => saved.includes(x.value)).map((x) => x.value));
      }
      if (profile.skin_profile) {
        setSkin((prev) => prev.length ? prev : profile.skin_profile!.split(",").map((x) => x.trim()).filter(Boolean));
      }
    } catch {
      // The active session remains usable even if profile hydration fails.
    }
  }

  useEffect(() => {
    void loadActiveCustomerProfile();
  }, [token, customerId]);

  async function saveActiveProfile() {
    setError(null);
    setStatusMsg(null);
    if (!name.trim()) return setError("نام الزامی است.");
    if (!mobile.trim()) return setError("شماره موبایل الزامی است.");
    setProfileSaving(true);
    try {
      const currentToken = await ensureSession(name.trim(), concernsText);
      const intake = (await customerIntake({
        name: name.trim(),
        mobile: mobile.trim() || undefined,
        concerns: concernsText || undefined,
        consent: 0,
        skin_profile: skin.length ? skin.join(",") : undefined,
        guest: false,
        open_case: false,
      } as CustomerIntakeRequest, currentToken)) as { customer?: { customer_id?: string } };
      const resolvedId = intake?.customer?.customer_id ?? sessionStorage.getItem("hbi_customer_id");
      if (resolvedId) {
        sessionStorage.setItem("hbi_customer_id", resolvedId);
        setCustomerId(resolvedId);
      }
      sessionStorage.setItem("hbi_concerns", concernsText);
      setStatusMsg("پروفایل مشتری فعال ذخیره شد. همین مشتری در مشاوره، پرونده و فروش استفاده می‌شود.");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setProfileSaving(false);
    }
  }

  function startNewCustomer() {
    ["hbi_access_token", "hbi_refresh_token", "hbi_customer_id", "hbi_case_id", "hbi_concerns"].forEach((k) => sessionStorage.removeItem(k));
    setToken(null);
    setCustomerId(null);
    setCaseId(null);
    setName("");
    setMobile("");
    setConcerns([]);
    setSkin([]);
    setNote("");
    setRecs([]);
    setRecDone(false);
    setStatusMsg("مشتری جدید آماده ثبت است. نشست محصولات/اپراتور دست‌نخورده باقی ماند.");
    setActive("profile");
  }

  async function runFullFlow(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setStatusMsg(null);
    setRecDone(false);
    setRecs([]);
    if (!name.trim()) return setError("نام الزامی است.");
    if (!mobile.trim()) return setError("شماره موبایل الزامی است.");
    if (!concernsText) return setError("حداقل یک موضوع یا نوع پوست را انتخاب کنید.");
    setBusy(true);
    try {
      const currentToken = await ensureSession(name.trim(), concernsText);
      sessionStorage.setItem("hbi_concerns", concernsText);
      const intake = (await customerIntake(
        {
          name: name.trim(),
          mobile: mobile.trim() || undefined,
          concerns: concernsText,
          consent: 0,
          skin_profile: skin.length ? skin.join(",") : undefined,
          guest: false,
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
    startNewCustomer();
    setStatusMsg("نشست مشتری پاک شد. نشست اپراتور محصولات حفظ شده است.");
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
                    <input id="mobile" className="pro-input" value={mobile} onChange={(e) => setMobile(e.target.value)} placeholder="09…" />
                  </div>
                </div>
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
            <div className="pro-panel-head">
              <div>
                <h1>پروفایل مشتری</h1>
                <p className="pro-lead">این مشتری فعال، مرجع مشترک مشاوره، پرونده، پیشنهاد و فروش است.</p>
              </div>
              <button type="button" className="pro-btn-secondary" onClick={startNewCustomer}>مشتری جدید</button>
            </div>
            <fieldset className="pro-fieldset">
              <legend>اطلاعات مشتری فعال</legend>
              <div className="pro-grid-2">
                <div><label className="pro-label" htmlFor="profile-name">نام *</label><input id="profile-name" className="pro-input" value={name} onChange={(e) => setName(e.target.value)} /></div>
                <div><label className="pro-label" htmlFor="profile-mobile">موبایل</label><input id="profile-mobile" className="pro-input" value={mobile} onChange={(e) => setMobile(e.target.value)} placeholder="09…" /></div>
              </div>
            </fieldset>
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
              <button type="button" className="pro-btn-primary" disabled={profileSaving} onClick={() => void saveActiveProfile()}>
                {profileSaving ? "در حال ذخیره…" : "ذخیره پروفایل مشتری"}
              </button>
              <button type="button" className="pro-btn-secondary" onClick={() => go("consult")}>مشاوره همین مشتری</button>
              <button type="button" className="pro-btn-secondary" onClick={clearSession}>مشتری جدید</button>
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
            token={token}
            onEnsureSession={ensureProductSession}
            editProduct={editProduct}
            onCancelEdit={() => setEditProduct(null)}
            onRegistered={() => {
              setEditProduct(null);
              void loadProducts();
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
              <li>پروفایل مشتری (intake)</li>
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
