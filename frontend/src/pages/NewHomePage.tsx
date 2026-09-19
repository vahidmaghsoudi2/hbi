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
  listSalesByCustomer,
  getCustomerById,
  searchCustomers,
  getInventoryByProduct,
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
  const [purchaseHistory, setPurchaseHistory] = useState<SaleDTO[]>([]);
  const [historyBusy, setHistoryBusy] = useState(false);
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
      setPurchaseHistory([]);
      setHistoryBusy(true);
      try {
        const hist = await listSalesByCustomer(customer.customer_id, pair.access_token);
        setPurchaseHistory(Array.isArray(hist) ? hist : []);
      } catch {
        setPurchaseHistory([]);
      } finally {
        setHistoryBusy(false);
      }
      setStatusMsg("مشتری قبلی انتخاب شد. سابقه خرید بارگذاری شد؛ مشکل امروز را ثبت کنید.");
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
      if (profile.mobile) setMobile(profile.mobile);
      if (profile.concerns) {
        const saved = profile.concerns.split(",").map((x) => x.trim()).filter(Boolean);
        setConcerns((prev) => prev.length ? prev : CONCERN_OPTIONS.filter((x) => saved.includes(x.value)).map((x) => x.value));
      }
      if (profile.skin_profile) {
        setSkin((prev) => prev.length ? prev : profile.skin_profile!.split(",").map((x) => x.trim()).filter(Boolean));
      }
    } catch {
      // keep session usable
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
    setPurchaseHistory([]);
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
          {statusMsg ? (<><span className="sep">|</span><span className="ok">{statusMsg}</span></>) : null}
          {error ? (<><span className="sep">|</span><span className="err">{error}</span></>) : null}
          <button type="button" className="pro-btn-secondary" onClick={startNewCustomer}>مشتری جدید</button>
        </div>

        {active === "previous" && (
          <section className="pro-panel">
            <h1>مشتری قبلی / جست‌وجو</h1>
            <p className="pro-lead">مشتری را پیدا کنید، سابقه او را بارگذاری کنید و سپس مشکل امروز را در یک پرونده جدید ثبت کنید.</p>
            <form className="pro-actions" onSubmit={(e) => { e.preventDefault(); void searchPreviousCustomers(); }}>
              <input className="pro-input" value={customerSearch} onChange={(e) => setCustomerSearch(e.target.value)} placeholder="نام مشتری…" aria-label="جست‌وجوی مشتری قبلی" />
              <button type="submit" className="pro-btn-primary" disabled={customerSearchBusy}>{customerSearchBusy ? "در حال جست‌وجو…" : "جست‌وجو"}</button>
            </form>
            {customerSearchResults.length > 0 ? (
              <div className="pro-product-grid" style={{ marginTop: "1rem" }}>
                {customerSearchResults.map((customer) => (
                  <article key={customer.customer_id} className="pro-product-card">
                    <h3>{customer.name}</h3>
                    <p className="pro-muted">{customer.mobile ?? "موبایل ثبت نشده"}</p>
                    <p className="pro-muted">{customer.concerns ?? "سابقه دغدغه ثبت نشده"}</p>
                    <button type="button" className="pro-btn-primary" onClick={() => void selectPreviousCustomer(customer)} disabled={busy}>انتخاب مشتری</button>
                  </article>
                ))}
              </div>
            ) : customerSearch.trim() && !customerSearchBusy ? (
              <div className="pro-empty"><strong>مشتری‌ای با این نام پیدا نشد.</strong></div>
            ) : null}
            {historyBusy ? <p className="pro-muted">در حال بارگذاری سابقه خرید…</p> : null}
            {purchaseHistory.length > 0 ? (
              <div className="pro-rec-list" style={{ marginTop: "1rem" }}>
                <h2>سابقه خرید</h2>
                {purchaseHistory.map((sale) => (
                  <article key={sale.sale_id} className="pro-rec-card">
                    <div>
                      <h3>{sale.sale_id}</h3>
                      <p className="pro-muted">مبلغ: {sale.total_amount_toman ?? "—"}</p>
                      <ul>
                        {(sale.items ?? []).map((it, idx) => (
                          <li key={`${sale.sale_id}-${it.product_id}-${idx}`}>
                            {it.product_id} × {it.quantity}
                            {it.recommendation_id ? ` · Rec: ${it.recommendation_id}` : " · بدون پیوند پیشنهاد"}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </article>
                ))}
              </div>
            ) : customerId && !historyBusy ? (
              <p className="pro-muted" style={{ marginTop: "1rem" }}>سابقه خرید ثبت‌شده‌ای برای این مشتری نیست.</p>
            ) : null}
          </section>
        )}

        {active === "consult" && (
          <section className="pro-panel">
            <h1>فرم مشاوره سریع</h1>
            {purchaseHistory.length > 0 ? (
              <div className="pro-rec-list" style={{ marginBottom: "1rem" }}>
                <h2>سابقه خرید مشتری</h2>
                {purchaseHistory.map((sale) => (
                  <article key={sale.sale_id} className="pro-rec-card">
                    <div>
                      <h3>{sale.sale_id}</h3>
                      <ul>
                        {(sale.items ?? []).map((it, idx) => (
                          <li key={`${sale.sale_id}-${it.product_id}-${idx}`}>
                            {it.product_id} × {it.quantity}
                            {it.recommendation_id ? ` · Rec: ${it.recommendation_id}` : ""}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </article>
                ))}
              </div>
            ) : null}
            <p className="pro-lead">پروفایل، پرونده و پیشنهاد روی همین صفحه ساخته می‌شود.</p>
            <form className="pro-form" onSubmit={runFullFlow}>
              <fieldset className="pro-fieldset">
                <legend>۱) هویت</legend>
                <div className="pro-grid-2">
                  <div>
                    <label className="pro-label" htmlFor="name">نام *</label>
                    <input id="name" className="pro-input" value={name} onChange={(e) => setName(e.target.value)} />
                  </div>
                  <div>
                    <label className="pro-label" htmlFor="mobile">موبایل *</label>
                    <input id="mobile" className="pro-input" value={mobile} onChange={(e) => setMobile(e.target.value)} />
                  </div>
                </div>
              </fieldset>
              <fieldset className="pro-fieldset">
                <legend>۲) موضوع</legend>
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
                <textarea className="pro-input pro-textarea" value={note} onChange={(e) => setNote(e.target.value)} rows={3} />
              </fieldset>
              <div className="pro-actions">
                <button type="submit" className="pro-btn-primary" disabled={busy}>{busy ? "در حال اجرا…" : "ثبت مراجعه + دریافت پیشنهاد"}</button>
              </div>
            </form>
          </section>
        )}

        {active === "profile" && (
          <section className="pro-panel">
            <h1>پروفایل مشتری فعال</h1>
            <button type="button" className="pro-btn-primary" onClick={() => void saveActiveProfile()} disabled={profileSaving}>{profileSaving ? "…" : "ذخیره پروفایل"}</button>
            <button type="button" className="pro-btn-secondary" onClick={clearSession}>مشتری جدید</button>
          </section>
        )}

        {active === "catalog" && (
          <section className="pro-panel">
            <h1>محصولات</h1>
            {catalogLoading ? <p>…</p> : catalogError ? <p className="err">{catalogError}</p> : (
              <div className="pro-product-grid">{products.map((p) => (<article key={p.product_id} className="pro-product-card"><h3>{p.product_name}</h3><p className="pro-muted">{p.product_id}</p></article>))}</div>
            )}
          </section>
        )}

        {active === "intake" && (
          <ProductIntakePanel token={token} onEnsureSession={ensureProductSession} editProduct={editProduct} onCancelEdit={() => setEditProduct(null)} onRegistered={() => { setEditProduct(null); void loadProducts(); }} />
        )}

        {active === "results" && (
          <section className="pro-panel">
            <h1>پیشنهادها</h1>
            {!recDone && <p className="pro-muted">هنوز پیشنهادی گرفته نشده.</p>}
            {recDone && recs.length === 0 && <div className="pro-empty"><strong>مورد منطبقی یافت نشد.</strong></div>}
            <div className="pro-rec-list">
              {recs.map((r, i) => (
                <article key={r.recommendation_id || `${r.product_id}-${i}`} className="pro-rec-card">
                  <div className="pro-rec-rank">#{i + 1}</div>
                  <div>
                    <h3>{r.product_id}</h3>
                    <p className="pro-muted">{r.eligibility_status ?? r.eligibility ?? "—"}</p>
                    <button type="button" className="pro-btn-primary" onClick={() => selectRecommendationForSale(r)}>انتخاب این پیشنهاد برای فروش</button>
                  </div>
                </article>
              ))}
            </div>
          </section>
        )}

        {active === "sales" && (
          <section className="pro-panel" id="sales">
            <h1>فروش</h1>
            <form className="pro-form" onSubmit={onSaleSubmit}>
              <label className="pro-label" htmlFor="sale-manual">شناسه محصول</label>
              <input id="sale-manual" className="pro-input" value={saleProductId} onChange={(e) => { setSaleProductId(e.target.value); setSelectedRecommendationId(null); }} />
              <label className="pro-label" htmlFor="sale-qty">تعداد</label>
              <input id="sale-qty" type="number" className="pro-input" value={saleQty} min={1} onChange={(e) => setSaleQty(Number(e.target.value) || 1)} />
              <label className="pro-label" htmlFor="sale-fx">نرخ ارز</label>
              <input id="sale-fx" type="number" className="pro-input" value={saleFxRate} onChange={(e) => setSaleFxRate(Number(e.target.value) || 1)} />
              <p className="pro-muted">قیمت: {salePrice ?? "—"} · موجودی: {saleStock ?? "—"}</p>
              <button type="submit" className="pro-btn-primary" disabled={saleBusy}>{saleBusy ? "…" : "ثبت فروش"}</button>
            </form>
            {lastSale ? <p className="ok">آخرین فروش: {lastSale.sale_id}</p> : null}
            {totalSales != null ? <p>جمع فروش نشست: {totalSales}</p> : null}
          </section>
        )}

        {active === "about" && (
          <section className="pro-panel">
            <h1>درباره HBI</h1>
            <p className="pro-lead">سیستم پیشنهاد و فروش با رد تصمیم Recommendation → Sale.</p>
          </section>
        )}
      </main>
    </div>
  );
}
