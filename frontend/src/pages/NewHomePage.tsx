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
  listRecommendationsByCase,
  createSale,
  getTotalSales,
  getCustomerById,
  searchCustomers,
  getInventoryByProduct,
  listSalesByCustomer,
} from "../api/client";
import ProductIntakePanel from "./ProductIntakePanel";
import type {
  ProductDTO,
  RecommendationDTO,
  PilotTokenRequest,
  CustomerIntakeRequest,
  GuestCreateRequest,
  CustomerSearchResult,
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

type Panel = "consult" | "previous" | "profile" | "catalog" | "intake" | "results" | "sales" | "about";

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
  const [selectedRecommendationId, setSelectedRecommendationId] = useState<string | null>(null);
  const [saleQty, setSaleQty] = useState(1);
  const [salePrice, setSalePrice] = useState<number | null>(null);
  const [saleStock, setSaleStock] = useState<number | null>(null);
  const [saleFxRate, setSaleFxRate] = useState(1);
  const [saleBusy, setSaleBusy] = useState(false);
  const [lastSale, setLastSale] = useState<SaleDTO | null>(null);
  const [totalSales, setTotalSales] = useState<number | null>(null);
  const [editProduct, setEditProduct] = useState<ProductDTO | null>(null);
  const [profileSaving, setProfileSaving] = useState(false);
  const [customerSearch, setCustomerSearch] = useState("");
  const [customerSearchResults, setCustomerSearchResults] = useState<CustomerSearchResult[]>([]);
  const [customerSearchBusy, setCustomerSearchBusy] = useState(false);

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

  async function searchPreviousCustomers() {
    const query = customerSearch.trim();
    if (!query) {
      setCustomerSearchResults([]);
      return;
    }
    setError(null);
    setCustomerSearchBusy(true);
    try {
      const operatorToken = await ensureProductSession();
      if (!operatorToken) throw new Error("نشست جست‌وجوی مشتری در دسترس نیست.");
      const found = await searchCustomers(query, operatorToken);
      setCustomerSearchResults(Array.isArray(found) ? found : []);
    } catch (err) {
      setCustomerSearchResults([]);
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setCustomerSearchBusy(false);
    }
  }

  async function selectPreviousCustomer(customer: CustomerSearchResult) {
    setError(null);
    setStatusMsg(null);
    setBusy(true);
    try {
      const pair = await pilotToken({ customer_id: customer.customer_id });
      sessionStorage.setItem("hbi_access_token", pair.access_token);
      sessionStorage.setItem("hbi_refresh_token", pair.refresh_token);
      sessionStorage.setItem("hbi_customer_id", customer.customer_id);
      sessionStorage.removeItem("hbi_case_id");
      setToken(pair.access_token);
      setCustomerId(customer.customer_id);
      setCaseId(null);
      setName(customer.name ?? "");
      setMobile(customer.mobile ?? "");
      setConcerns(customer.concerns ? customer.concerns.split(",").map((x) => x.trim()).filter(Boolean) : []);
      setSkin(customer.skin_profile ? customer.skin_profile.split(",").map((x) => x.trim()).filter(Boolean) : []);
      setNote("");
      setRecs([]);
      setRecDone(false);
      setSelectedRecommendationId(null);
      setSaleProductId("");
      setLastSale(null);
      try {
        const history = await listSalesByCustomer(customer.customer_id, pair.access_token);
        const count = Array.isArray(history) ? history.length : 0;
        setStatusMsg(`مشتری قبلی انتخاب شد. ${count} سابقه خرید بارگذاری شد؛ مشکل امروز را ثبت کنید.`);
      } catch {
        setStatusMsg("مشتری قبلی انتخاب شد. اطلاعات سابقه بارگذاری شد؛ مشکل امروز را ثبت کنید.");
      }
      setCustomerSearchResults([]);
      setActive("consult");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
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

  useEffect(() => {
    if (active !== "results") return;
    const storedCaseId = sessionStorage.getItem("hbi_case_id");
    if (storedCaseId && storedCaseId !== caseId) setCaseId(storedCaseId);
    if (!token || !storedCaseId) {
      setRecs([]);
      setRecDone(false);
      return;
    }
    let cancelled = false;
    void listRecommendationsByCase(storedCaseId, token)
      .then((list) => {
        if (cancelled) return;
        setRecs(Array.isArray(list) ? list : []);
        setRecDone(true);
      })
      .catch(() => {
        if (cancelled) return;
        setRecs([]);
        setRecDone(false);
      });
    return () => {
      cancelled = true;
    };
  }, [active, token, caseId]);

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
    setSelectedRecommendationId(null);
    setSaleProductId("");
    setLastSale(null);
    setStatusMsg("مشتری جدید آماده ثبت است. نشست محصولات/اپراتور دست‌نخورده باقی ماند.");
    setActive("profile");
  }

  function selectRecommendationForSale(r: RecommendationDTO) {
    setSaleProductId(r.product_id);
    setSelectedRecommendationId(r.recommendation_id);
    setStatusMsg(`پیشنهاد ${r.recommendation_id} برای فروش انتخاب شد.`);
    setActive("sales");
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

  useEffect(() => {
    if (!saleProductId || !token) {
      setSalePrice(null);
      setSaleStock(null);
      return;
    }
    let cancelled = false;
    void getInventoryByProduct(saleProductId, token)
      .then((inv) => {
        if (cancelled) return;
        setSalePrice(inv.sale_price_toman ?? null);
        setSaleStock(Math.max(0, (inv.quantity_available ?? 0) - (inv.quantity_reserved ?? 0)));
      })
      .catch(() => {
        if (cancelled) return;
        setSalePrice(null);
        setSaleStock(null);
      });
    return () => {
      cancelled = true;
    };
  }, [saleProductId, token]);

  async function onSaleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    if (!token || !customerId) return setError("ابتدا مشاوره را ثبت کنید.");
    if (!saleProductId.trim()) return setError("محصول را انتخاب کنید.");
    if (saleQty < 1) return setError("تعداد نامعتبر است.");
    if (salePrice == null) return setError("قیمت فروش این محصول از موجودی دریافت نشد.");
    if (saleStock != null && saleQty > saleStock) return setError(`موجودی قابل فروش: ${saleStock}`);
    setSaleBusy(true);
    try {
      const sale = await createSale(
        {
          customer_id: customerId,
          items: [{ product_id: saleProductId.trim(), quantity: saleQty, ...(selectedRecommendationId ? { recommendation_id: selectedRecommendationId } : {}) }],
          fx_rate_usd_to_irr: saleFxRate,
        },
        token
      );
      setLastSale(sale);
      setSelectedRecommendationId(null);
      setSaleProductId("");
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
    ["previous", "مشتری قبلی / جست‌وجو"],
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
              <span className="status-ok">{statusMsg}</span>
            </>
          ) : null}
          {error ? (
            <>
              <span className="sep">|</span>
              <span className="status-err">{error}</span>
            </>
          ) : null}
          <button type="button" className="pro-link-btn" onClick={clearSession}>
            پاک‌سازی نشست مشتری
          </button>
        </div>

        {active === "consult" && (
          <section className="pro-panel">
            <h1>مشاوره جدید</h1>
            <form onSubmit={runFullFlow} className="pro-form">
              <label>
                نام
                <input value={name} onChange={(e) => setName(e.target.value)} required />
              </label>
              <label>
                موبایل
                <input value={mobile} onChange={(e) => setMobile(e.target.value)} required />
              </label>
              <fieldset>
                <legend>موضوع / نگرانی</legend>
                <div className="chip-row">
                  {CONCERN_OPTIONS.map((c) => (
                    <button
                      key={c.id}
                      type="button"
                      className={concerns.includes(c.value) ? "chip on" : "chip"}
                      onClick={() => toggleIn(concerns, c.value, setConcerns)}
                    >
                      {c.label}
                    </button>
                  ))}
                </div>
              </fieldset>
              <fieldset>
                <legend>نوع پوست</legend>
                <div className="chip-row">
                  {SKIN_OPTIONS.map((s) => (
                    <button
                      key={s}
                      type="button"
                      className={skin.includes(s) ? "chip on" : "chip"}
                      onClick={() => toggleIn(skin, s, setSkin)}
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </fieldset>
              <label>
                یادداشت
                <textarea value={note} onChange={(e) => setNote(e.target.value)} rows={2} />
              </label>
              <button type="submit" disabled={busy}>
                {busy ? "در حال ثبت…" : "ثبت مشاوره و دریافت پیشنهاد"}
              </button>
            </form>
          </section>
        )}

        {active === "previous" && (
          <section className="pro-panel">
            <h1>مشتری قبلی / جست‌وجو</h1>
            <div className="pro-form">
              <label>
                جست‌وجوی نام یا موبایل
                <input
                  value={customerSearch}
                  onChange={(e) => setCustomerSearch(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), void searchPreviousCustomers())}
                />
              </label>
              <button type="button" disabled={customerSearchBusy} onClick={() => void searchPreviousCustomers()}>
                {customerSearchBusy ? "جست‌وجو…" : "جست‌وجو"}
              </button>
              <ul className="pro-list">
                {customerSearchResults.map((c) => (
                  <li key={c.customer_id}>
                    <button type="button" className="pro-link-btn" onClick={() => void selectPreviousCustomer(c)} disabled={busy}>
                      {c.name ?? c.customer_id} {c.mobile ? `· ${c.mobile}` : ""}
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          </section>
        )}

        {active === "profile" && (
          <section className="pro-panel">
            <h1>پروفایل مشتری فعال</h1>
            <form
              className="pro-form"
              onSubmit={(e) => {
                e.preventDefault();
                void saveActiveProfile();
              }}
            >
              <label>
                نام
                <input value={name} onChange={(e) => setName(e.target.value)} />
              </label>
              <label>
                موبایل
                <input value={mobile} onChange={(e) => setMobile(e.target.value)} />
              </label>
              <fieldset>
                <legend>موضوع / نگرانی</legend>
                <div className="chip-row">
                  {CONCERN_OPTIONS.map((c) => (
                    <button
                      key={c.id}
                      type="button"
                      className={concerns.includes(c.value) ? "chip on" : "chip"}
                      onClick={() => toggleIn(concerns, c.value, setConcerns)}
                    >
                      {c.label}
                    </button>
                  ))}
                </div>
              </fieldset>
              <fieldset>
                <legend>نوع پوست</legend>
                <div className="chip-row">
                  {SKIN_OPTIONS.map((s) => (
                    <button
                      key={s}
                      type="button"
                      className={skin.includes(s) ? "chip on" : "chip"}
                      onClick={() => toggleIn(skin, s, setSkin)}
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </fieldset>
              <button type="submit" disabled={profileSaving}>
                {profileSaving ? "ذخیره…" : "ذخیره پروفایل"}
              </button>
              <button type="button" className="pro-link-btn" onClick={startNewCustomer}>
                مشتری جدید
              </button>
            </form>
          </section>
        )}

        {active === "catalog" && (
          <section className="pro-panel">
            <h1>محصولات</h1>
            {catalogLoading ? <p>بارگذاری…</p> : null}
            {catalogError ? <p className="status-err">{catalogError}</p> : null}
            <ul className="pro-list">
              {products.map((p) => (
                <li key={p.product_id}>
                  {p.brand} · {p.product_name} [{p.qa_verdict ?? p.identity_status}]
                </li>
              ))}
            </ul>
            <button type="button" onClick={() => void loadProducts()}>
              تازه‌سازی
            </button>
          </section>
        )}

        {active === "intake" && (
          <section className="pro-panel">
            <h1>ورود محصول</h1>
            <ProductIntakePanel onSaved={() => void loadProducts()} editProduct={editProduct} onEditDone={() => setEditProduct(null)} />
          </section>
        )}

        {active === "results" && (
          <section className="pro-panel">
            <h1>پیشنهادها</h1>
            {!recDone ? <p>هنوز پیشنهادی دریافت نشده.</p> : null}
            <ul className="pro-list">
              {recs.map((r) => (
                <li key={r.recommendation_id}>
                  <div>
                    {r.product_id} · score={r.final_score ?? r.ranking_score} · {r.eligibility ?? r.eligibility_status}
                  </div>
                  <button type="button" className="pro-link-btn" onClick={() => selectRecommendationForSale(r)}>
                    انتخاب برای فروش
                  </button>
                </li>
              ))}
            </ul>
          </section>
        )}

        {active === "sales" && (
          <section className="pro-panel">
            <h1>فروش</h1>
            <p>مجموع فروش‌ها: {totalSales ?? "—"}</p>
            {lastSale ? <p className="status-ok">آخرین فروش: {lastSale.sale_id}</p> : null}
            <form onSubmit={onSaleSubmit} className="pro-form">
              <label>
                product_id
                <input value={saleProductId} onChange={(e) => setSaleProductId(e.target.value)} />
              </label>
              <label>
                تعداد
                <input type="number" min={1} value={saleQty} onChange={(e) => setSaleQty(Number(e.target.value) || 1)} />
              </label>
              <label>
                نرخ FX (IRR per USD)
                <input type="number" step="any" value={saleFxRate} onChange={(e) => setSaleFxRate(Number(e.target.value) || 1)} />
              </label>
              <p>قیمت واحد (تومان): {salePrice ?? "—"} · موجودی: {saleStock ?? "—"}</p>
              <button type="submit" disabled={saleBusy}>
                {saleBusy ? "ثبت…" : "ثبت فروش"}
              </button>
            </form>
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
