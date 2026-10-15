import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  listSellableProducts,
  listManageableProducts,
  pilotToken,
  pilotOperatorToken,
  pilotPoToken,
  customerIntake,
  createGuest,
  generateRecommendations,
  listInternalEvaluationsByCase,
  createSale,
  getTotalSales,
  getCustomerById,
  searchCustomers,
  getInventoryByProduct,
  getCurrentFx,
  listSalesByCustomer,
  getSalesPeriod,
  getInventoryReport,
  getLowStockReport,
  getStockMovements,
} from "../api/client";
import ProductIntakePanel from "./ProductIntakePanel";
import ProductReviewPanel from "./ProductReviewPanel";
import type {
  ProductDTO,
  RecommendationDTO,
  PilotTokenRequest,
  CustomerIntakeRequest,
  GuestCreateRequest,
  CustomerSearchResult,
  SaleDTO,
  SalesReportDTO,
  InventoryReportRow,
  StockMovementDTO,
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
const CONSULTATION_LINES = [{ id: "SKIN", label: "پوست" }] as const;
const INITIAL_RECOMMENDATION_LIMIT = 5;

type Panel = "home" | "consult" | "previous" | "profile" | "catalog" | "review" | "intake" | "results" | "sales" | "about";
type MainSection = "home" | "customers" | "consultation" | "sales" | "products" | "inventory" | "purchases" | "reports";
type PageView = "main" | "section" | "content";

export default function NewHomePage() {
  const navigate = useNavigate();
  const [active, setActive] = useState<Panel>("home");
  const [pageView, setPageView] = useState<PageView>("main");
  const [mainSection, setMainSection] = useState<MainSection>("home");
  const [token, setToken] = useState<string | null>(() => sessionStorage.getItem("hbi_access_token"));
  const [customerId, setCustomerId] = useState<string | null>(() => sessionStorage.getItem("hbi_customer_id"));
  const [caseId, setCaseId] = useState<string | null>(() => sessionStorage.getItem("hbi_case_id"));
  const [name, setName] = useState("");
  const [mobile, setMobile] = useState("");
  const [consultationLine, setConsultationLine] = useState<string>("SKIN");
  const [concerns, setConcerns] = useState<string[]>([]);
  const [skin, setSkin] = useState<string[]>([]);
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [products, setProducts] = useState<ProductDTO[]>([]);
  const [sellableProducts, setSellableProducts] = useState<ProductDTO[]>([]);
  const [saleProductsError, setSaleProductsError] = useState<string | null>(null);
  const [saleCustomerSearch, setSaleCustomerSearch] = useState("");
  const [saleCustomerId, setSaleCustomerId] = useState<string | null>(null);
  const [saleCustomerLabel, setSaleCustomerLabel] = useState<string | null>(null);
  const [catalogError, setCatalogError] = useState<string | null>(null);
  const [catalogLoading, setCatalogLoading] = useState(true);
  const [recs, setRecs] = useState<RecommendationDTO[]>([]);
  const [recDone, setRecDone] = useState(false);
  const [showAllRecommendations, setShowAllRecommendations] = useState(false);
  const [saleProductId, setSaleProductId] = useState("");
  const [saleQty, setSaleQty] = useState(1);
  const [salePrice, setSalePrice] = useState<number | null>(null);
  const [saleStock, setSaleStock] = useState<number | null>(null);
  const [saleFxRate, setSaleFxRate] = useState<number | null>(null);
  const [saleBusy, setSaleBusy] = useState(false);
  const [lastSale, setLastSale] = useState<SaleDTO | null>(null);
  const [totalSales, setTotalSales] = useState<number | null>(null);
  const [editProduct, setEditProduct] = useState<ProductDTO | null>(null);
  const [profileSaving, setProfileSaving] = useState(false);
  const [customerSearch, setCustomerSearch] = useState("");
  const [customerSearchResults, setCustomerSearchResults] = useState<CustomerSearchResult[]>([]);
  const [purchaseHistory, setPurchaseHistory] = useState<SaleDTO[]>([]);
  const [customerSearchBusy, setCustomerSearchBusy] = useState(false);
  const [dashboardLoading, setDashboardLoading] = useState(false);
  const [dashboardError, setDashboardError] = useState<string | null>(null);
  const [dashboardSales, setDashboardSales] = useState<SalesReportDTO | null>(null);
  const [dashboardInventory, setDashboardInventory] = useState<InventoryReportRow[] | null>(null);
  const [dashboardLowStock, setDashboardLowStock] = useState<InventoryReportRow[] | null>(null);
  const [dashboardMovements, setDashboardMovements] = useState<StockMovementDTO[] | null>(null);

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

  const loadSellableProducts = useCallback(async () => {
    setSaleProductsError(null);
    try {
      const adminToken = sessionStorage.getItem("hbi_admin_access_token");
      if (!adminToken) throw new Error("برای دریافت کاتالوگ فروش، نشست مدیر لازم است.");
      const data = await listSellableProducts(adminToken);
      setSellableProducts(Array.isArray(data) ? data : []);
      if (!Array.isArray(data) || data.length === 0) {
        setSaleProductsError("محصول فعال، تأییدشده، دارای موجودی و قیمت فروش در دسترس نیست.");
      }
    } catch (err) {
      setSellableProducts([]);
      setSaleProductsError(err instanceof Error ? err.message : "دریافت کاتالوگ فروش ناموفق بود.");
    }
  }, []);

  useEffect(() => {
    void loadSellableProducts();
  }, [loadSellableProducts]);

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

  const refreshDashboard = useCallback(async () => {
    const adminToken = sessionStorage.getItem("hbi_admin_access_token");
    if (!adminToken) {
      setDashboardSales(null);
      setDashboardInventory(null);
      setDashboardLowStock(null);
      setDashboardMovements(null);
      setDashboardError("نشست مدیر موجود نیست؛ ابتدا وارد حساب مدیر شوید.");
      return;
    }

    setDashboardLoading(true);
    setDashboardError(null);
    const results = await Promise.allSettled([
      getSalesPeriod("today", adminToken),
      getInventoryReport(adminToken),
      getLowStockReport(5, adminToken),
      getStockMovements(adminToken, { limit: 5 }),
    ]);
    let failed = 0;
    if (results[0].status === "fulfilled") setDashboardSales(results[0].value);
    else { setDashboardSales(null); failed += 1; }
    if (results[1].status === "fulfilled") setDashboardInventory(results[1].value);
    else { setDashboardInventory(null); failed += 1; }
    if (results[2].status === "fulfilled") setDashboardLowStock(results[2].value);
    else { setDashboardLowStock(null); failed += 1; }
    if (results[3].status === "fulfilled") setDashboardMovements(results[3].value);
    else { setDashboardMovements(null); failed += 1; }
    setDashboardError(failed ? `${failed} بخش از خلاصه عملیاتی بارگذاری نشد؛ جزئیات را در گزارش‌ها بررسی کنید.` : null);
    setDashboardLoading(false);
  }, []);

  useEffect(() => {
    if (active === "home") void refreshDashboard();
  }, [active, refreshDashboard]);

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

  async function searchSaleCustomers() {
    const query = saleCustomerSearch.trim();
    if (!query) {
      setCustomerSearchResults([]);
      setError("برای جست‌وجوی مشتری، شماره موبایل یا نام را وارد کنید.");
      return;
    }
    setError(null);
    setCustomerSearchBusy(true);
    try {
      const operatorToken = await ensureProductSession();
      if (!operatorToken) throw new Error("نشست مدیر برای جست‌وجوی مشتری در دسترس نیست.");
      const found = await searchCustomers(query, operatorToken);
      setCustomerSearchResults(Array.isArray(found) ? found : []);
      if (!Array.isArray(found) || found.length === 0) setStatusMsg("مشتری مطابق جست‌وجو پیدا نشد؛ فروش مستقیم همچنان ممکن است.");
    } catch (err) {
      setCustomerSearchResults([]);
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setCustomerSearchBusy(false);
    }
  }

  function chooseSaleCustomer(customer: CustomerSearchResult) {
    setSaleCustomerId(customer.customer_id);
    setSaleCustomerLabel(`${customer.name ?? "بدون نام"} · ${customer.mobile ?? "بدون موبایل"}`);
    setCustomerSearchResults([]);
    setSaleCustomerSearch("");
    setError(null);
    setStatusMsg("مشتری فقط برای این فروش انتخاب شد؛ نشست مشاوره تغییر نکرد.");
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
      setShowAllRecommendations(false);
      setSaleProductId("");
      setLastSale(null);
      const history = await listSalesByCustomer(customer.customer_id, pair.access_token);
      setPurchaseHistory(Array.isArray(history) ? history : []);
      setStatusMsg(`مشتری انتخاب شد و ${history.length} خرید قبلی بارگذاری شد. برای شروع مشاوره، جداگانه وارد بخش مشاوره شوید.`);
      setCustomerSearchResults([]);
      setActive("previous");
      setPageView("content");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  function go(panel: Panel) {
    setActive(panel);
    setPageView("content");
    setError(null);
  }

  function openMainSection(next: MainSection) {
    setMainSection(next);
    setError(null);
    if (next === "home") {
      setActive("home");
      setPageView("content");
    } else {
      setPageView("section");
    }
  }

  function backToNavigation() {
    setError(null);
    setPageView(mainSection === "home" ? "main" : "section");
  }

  function logout() {
    sessionStorage.clear();
    navigate("/login", { replace: true });
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

  async function ensureReviewSession(): Promise<string | null> {
    const cached = sessionStorage.getItem("hbi_po_access_token");
    if (cached) return cached;
    const pair = await pilotPoToken();
    sessionStorage.setItem("hbi_po_access_token", pair.access_token);
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
    void (async () => {
      try {
        // The operator UI reads internal evaluation history through the
        // role-protected endpoint; the ordinary customer endpoint stays eligible-only.
        const operatorToken = await ensureProductSession();
        if (!operatorToken) throw new Error("نشست اپراتور در دسترس نیست.");
        const list = await listInternalEvaluationsByCase(storedCaseId, operatorToken);
        if (cancelled) return;
        setRecs(Array.isArray(list) ? list : []);
        setRecDone(true);
      } catch {
        if (cancelled) return;
        setRecs([]);
        setRecDone(false);
      }
    })();
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
    setConsultationLine("SKIN");
    setConcerns([]);
    setSkin([]);
    setNote("");
    setRecs([]);
    setRecDone(false);
    setSaleProductId("");
    setLastSale(null);
    setPurchaseHistory([]);
    setStatusMsg("مشتری جدید آماده ثبت است. نشست محصولات/اپراتور دست‌نخورده باقی ماند.");
    setActive("profile");
  }

  async function runFullFlow(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setStatusMsg(null);
    setRecDone(false);
    setRecs([]);
    setShowAllRecommendations(false);
    if (!name.trim()) return setError("نام الزامی است.");
    if (!mobile.trim()) return setError("شماره موبایل الزامی است.");
    if (!consultationLine) return setError("ابتدا لاین مشاوره را انتخاب کنید.");
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
          case_type: consultationLine,
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
      const operatorToken = await ensureProductSession();
      const evaluations = operatorToken
        ? await listInternalEvaluationsByCase(newCaseId, operatorToken)
        : list;
      const eligibleCount = (Array.isArray(evaluations) ? evaluations : []).filter(
        (r) => (r.eligibility_status ?? r.eligibility ?? "").trim().toUpperCase() === "ELIGIBLE"
      ).length;
      setRecs(Array.isArray(evaluations) ? evaluations : []);
      setShowAllRecommendations(false);
      setRecDone(true);
      setStatusMsg(eligibleCount ? `${eligibleCount} پیشنهاد واجد شرایط آماده است.` : "پیشنهاد واجد شرایطی با شواهد کافی یافت نشد.");
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
    if (!saleProductId) {
      setSalePrice(null);
      setSaleStock(null);
      return;
    }
    let cancelled = false;
    // Sale inventory reads use the Admin session, never a customer/pilot token.
    setSalePrice(null);
    setSaleFxRate(null);
    void Promise.resolve(sessionStorage.getItem("hbi_admin_access_token"))
      .then(async (adminToken) => {
        if (cancelled || !adminToken) throw new Error("برای دریافت قیمت و موجودی، نشست مدیر لازم است.");
        const [inv, fx] = await Promise.all([
          getInventoryByProduct(saleProductId, adminToken),
          getCurrentFx(),
        ]);
        if (fx.fx_rate_usd_to_irr == null) throw new Error("نرخ عملیاتی ارز در دسترس نیست؛ فروش متوقف شد.");
        if (inv.sale_price_usd == null) throw new Error("قیمت فروش دلاری محصول ثبت نشده است؛ فروش متوقف شد.");
        const priceToman = Math.round((inv.sale_price_usd * fx.fx_rate_usd_to_irr) / 10);
        return { inv, fxRate: fx.fx_rate_usd_to_irr, priceToman };
      })
      .then(({ inv, fxRate, priceToman }) => {
        if (cancelled) return;
        setSaleFxRate(fxRate);
        setSalePrice(priceToman);
        setSaleStock(Math.max(0, (inv.quantity_available ?? 0) - (inv.quantity_reserved ?? 0)));
      })
      .catch((err) => {
        if (cancelled) return;
        setSalePrice(null);
        setSaleFxRate(null);
        setSaleStock(null);
        setError(err instanceof Error ? err.message : String(err));
      });
    return () => {
      cancelled = true;
    };
  }, [saleProductId]);

  async function onSaleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    if (!sessionStorage.getItem("hbi_admin_access_token")) return setError("برای ثبت فروش ابتدا با حساب مدیر وارد شوید.");
    if (!saleProductId.trim()) return setError("محصول را انتخاب کنید.");
    if (saleQty < 1) return setError("تعداد نامعتبر است.");
    if (salePrice == null) return setError("قیمت فروش این محصول در دسترس نیست.");
    if (saleStock != null && saleQty > saleStock) return setError(`موجودی قابل فروش: ${saleStock}`);
    setSaleBusy(true);
    try {
      const fx = await getCurrentFx();
      if (fx.fx_rate_usd_to_irr == null) throw new Error("نرخ عملیاتی ارز در دسترس نیست؛ فروش متوقف شد.");
      const currentFxRate = fx.fx_rate_usd_to_irr;
      setSaleFxRate(currentFxRate);
      const adminToken = sessionStorage.getItem("hbi_admin_access_token");
      if (!adminToken) throw new Error("برای ثبت فروش ابتدا با حساب مدیر وارد شوید.");
      const sale = await createSale(
        {
          // Customer association is an explicit choice on this sale form, never session carry-over.
          customer_id: saleCustomerId,
          items: [{ product_id: saleProductId.trim(), quantity: saleQty }],
          fx_rate_usd_to_irr: currentFxRate,
        },
        adminToken
      );
      setLastSale(sale);
      setSaleProductId("");
      setSaleCustomerId(null);
      setSaleCustomerLabel(null);
      setStatusMsg(`فروش ثبت شد: ${sale.sale_id ?? "OK"}`);
      await refreshSalesTotal();
      try {
        if (!customerId || !token) return;
        const updatedHistory = await listSalesByCustomer(customerId, token);
        setPurchaseHistory(Array.isArray(updatedHistory) ? updatedHistory : []);
      } catch {
        // The sale is already committed; history refresh is best-effort.
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setSaleBusy(false);
    }
  }

  function formatExclusionReason(value: string | null | undefined) {
    const labels: Record<string, string> = {
      CRITICAL_PRODUCT_UNKNOWN: "اطلاعات حیاتی محصول نامشخص است",
      CRITICAL_CASE_UNKNOWN: "اطلاعات حیاتی پرونده نامشخص است",
      MEDICAL_CONTEXT_REVIEW_REQUIRED: "وجود زمینه پزشکی؛ نیازمند بررسی تخصصی",
      CLAIM_BOUNDARY_VIOLATION: "محدودیت ادعا نقض شده است",
      HIGH_CRITICAL_CONFLICT: "تعارض مهم یا بحرانی در شواهد",
      NO_CANONICAL_NEED: "نیاز استاندارد قابل تشخیص نیست",
      SKIN_CONSULTATION_EVIDENCE_MISSING: "شواهد مشاوره پوست کامل نیست",
      NO_APPROVED_EVIDENCE: "شواهد تأییدشده برای پیشنهاد وجود ندارد",
      INELIGIBLE_REASON_UNRESOLVED: "علت دقیق ردشدن نیازمند بررسی است",
    };
    const code = (value ?? "").trim();
    return (labels[code] ?? code) || "دلیل ثبت نشده";
  }

  function formatRecommendationStatus(value: string | null | undefined) {
    const normalized = (value ?? "").trim().toUpperCase();
    if (normalized === "ELIGIBLE") return "مناسب برای ادامه بررسی";
    if (normalized === "INELIGIBLE") return "برای این نیاز مناسب نیست";
    if (normalized === "READY") return "پیشنهاد آماده است";
    return value ?? "وضعیت مشخص نیست";
  }

  function formatRecommendationAvailability(value: string | null | undefined) {
    const normalized = (value ?? "").trim().toUpperCase();
    if (normalized === "AVAILABLE") return "موجود";
    if (normalized === "UNAVAILABLE") return "ناموجود";
    return value ?? "وضعیت موجودی مشخص نیست";
  }

  function formatMatchLevel(score: number | null | undefined) {
    if (score == null) return "ثبت نشده";
    if (score >= 0.8) return "بالا";
    if (score >= 0.5) return "متوسط";
    return "پایین";
  }

  function formatConfidenceLevel(score: number | null | undefined) {
    if (score == null) return "ثبت نشده";
    if (score >= 0.8) return "بالا";
    if (score >= 0.5) return "متوسط";
    return "محدود";
  }
  return (
    <div className="home-root pro-home">
      <header className="pro-header">
        <div className="pro-header-inner">
          <div className="pro-brand">
            <span className="pro-brand-mark">HBI</span>
            <div>
              <div className="pro-brand-title">گالری مقصودی</div>
              <div className="pro-brand-sub">هوش زیبایی و مراقبت · فضای کاری مدیر</div>
            </div>
          </div>
          <div className="pro-actions" style={{ alignItems: "center", justifyContent: "flex-end" }}>
            {pageView !== "main" ? (
              <button type="button" className="pro-btn-secondary" onClick={() => setPageView("main")}>منوی اصلی</button>
            ) : null}
            {pageView !== "main" ? (
              <button type="button" className="pro-btn-secondary" onClick={backToNavigation}>
                {pageView === "content" ? "بازگشت به بخش" : "بازگشت"}
              </button>
            ) : null}
            <button type="button" className="pro-btn-secondary" onClick={logout}>خروج از حساب مدیر</button>
          </div>
        </div>
      </header>

      <main className="pro-main">
        {pageView === "content" ? (
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
        ) : null}

        {error ? (
          <div className="pro-alert" role="alert">
            {error}
          </div>
        ) : null}

        {pageView === "main" && (
          <section className="pro-panel" aria-labelledby="main-menu-title">
            <h1 id="main-menu-title">فضای کاری مدیر</h1>
            <p className="pro-lead">یک حوزه را انتخاب کنید. زیرمنوها فقط پس از ورود به همان حوزه نمایش داده می‌شوند.</p>
            <div className="pro-product-grid">
              <article className="pro-product-card"><h2>خانه و داشبورد</h2><p className="pro-muted">نمای کلی عملیات و هشدارهای قابل اقدام.</p><button type="button" className="pro-btn-primary" onClick={() => openMainSection("home")}>بازکردن داشبورد</button></article>
              <article className="pro-product-card"><h2>مشتریان</h2><p className="pro-muted">پروفایل، جست‌وجو و سابقهٔ خرید مشتری.</p><button type="button" className="pro-btn-primary" onClick={() => openMainSection("customers")}>ورود به مشتریان</button></article>
              <article className="pro-product-card"><h2>مشاوره</h2><p className="pro-muted">ثبت مسئله، بررسی نیاز، پیشنهادها و تصمیم اپراتور.</p><button type="button" className="pro-btn-primary" onClick={() => openMainSection("consultation")}>ورود به مشاوره</button></article>
              <article className="pro-product-card"><h2>فروش</h2><p className="pro-muted">ثبت فروش؛ مشاوره پیش‌نیاز فروش مستقیم نیست.</p><button type="button" className="pro-btn-primary" onClick={() => openMainSection("sales")}>ورود به فروش</button></article>
              <article className="pro-product-card"><h2>مدیریت محصولات</h2><p className="pro-muted">فهرست، ورود اطلاعات و بررسی QA؛ مستقل از ورود فیزیکی موجودی.</p><button type="button" className="pro-btn-primary" onClick={() => openMainSection("products")}>ورود به مدیریت محصولات</button></article>
              <article className="pro-product-card"><h2>کالا و موجودی</h2><p className="pro-muted">مشاهده موجودی و گردش‌های انبار؛ جدا از مدیریت اطلاعات و تأیید محصول.</p><button type="button" className="pro-btn-primary" onClick={() => openMainSection("inventory")}>ورود به کالا و موجودی</button></article>
              <article className="pro-product-card"><h2>خرید</h2><p className="pro-muted">ثبت خرید و ورود فیزیکی موجودی.</p><button type="button" className="pro-btn-primary" onClick={() => openMainSection("purchases")}>ورود به خرید</button></article>
              <article className="pro-product-card"><h2>گزارش‌ها</h2><p className="pro-muted">مشاهدهٔ گزارش‌های عملیاتی و مالی موجود.</p><button type="button" className="pro-btn-primary" onClick={() => openMainSection("reports")}>ورود به گزارش‌ها</button></article>
            </div>
          </section>
        )}

        {pageView === "section" && (
          <section className="pro-panel" aria-labelledby="section-menu-title">
            <div className="pro-section-head">
              <h1 id="section-menu-title">{({
                customers: "مشتریان", consultation: "مشاوره", sales: "فروش",
                products: "مدیریت محصولات", inventory: "کالا و موجودی", purchases: "خرید",
                reports: "گزارش‌ها", home: "خانه و داشبورد",
              } as Record<MainSection, string>)[mainSection]}</h1>
              <button type="button" className="pro-btn-secondary" onClick={() => setPageView("main")}>بازگشت به منوی اصلی</button>
            </div>
            <p className="pro-lead">فقط عملیات مربوط به این حوزه در این صفحه قرار دارد.</p>
            <div className="pro-product-grid">
              {mainSection === "customers" ? <>
                <article className="pro-product-card"><h2>جست‌وجو و سابقه</h2><p className="pro-muted">یافتن مشتری و مشاهدهٔ سابقهٔ خرید.</p><button type="button" className="pro-btn-primary" onClick={() => go("previous")}>بازکردن جست‌وجوی مشتری</button></article>
                <article className="pro-product-card"><h2>پروفایل مشتری</h2><p className="pro-muted">ثبت یا تکمیل اطلاعات مشتری.</p><button type="button" className="pro-btn-primary" onClick={() => go("profile")}>بازکردن پروفایل مشتری</button></article>
              </> : null}
              {mainSection === "consultation" ? <>
                <article className="pro-product-card"><h2>مشاوره جدید</h2><p className="pro-muted">ثبت واقعیت مراجعه و مسئلهٔ مشتری.</p><button type="button" className="pro-btn-primary" onClick={() => go("consult")}>شروع مشاوره</button></article>
                <article className="pro-product-card"><h2>پیشنهادها و تصمیم اپراتور</h2><p className="pro-muted">بررسی نتایج و تصمیم‌گیری اپراتور.</p><button type="button" className="pro-btn-primary" onClick={() => go("results")}>بازکردن پیشنهادها</button></article>
              </> : null}
              {mainSection === "sales" ? <article className="pro-product-card"><h2>ثبت فروش و تاریخچه</h2><p className="pro-muted">ثبت فروش مستقیم بدون الزام به مشاورهٔ قبلی.</p><button type="button" className="pro-btn-primary" onClick={() => go("sales")}>بازکردن فروش</button></article> : null}
              {mainSection === "products" ? <>
                <article className="pro-product-card"><h2>فهرست محصولات</h2><p className="pro-muted">مشاهدهٔ محصولات قابل مدیریت.</p><button type="button" className="pro-btn-primary" onClick={() => go("catalog")}>بازکردن فهرست محصولات</button></article>
                <article className="pro-product-card"><h2>ورود و ویرایش محصول</h2><p className="pro-muted">ثبت مشخصات محصول؛ جدا از موجودی فیزیکی.</p><button type="button" className="pro-btn-primary" onClick={() => go("intake")}>ورود و ویرایش محصول</button></article>
                <article className="pro-product-card"><h2>بررسی و تأیید QA</h2><p className="pro-muted">بررسی شواهد و وضعیت تأیید محصول.</p><button type="button" className="pro-btn-primary" onClick={() => go("review")}>بازکردن بررسی QA</button></article>
              </> : null}
              {mainSection === "inventory" ? <>
                <article className="pro-product-card"><h2>موجودی کالا</h2><p className="pro-muted">موجودی قابل مشاهده و ارزش‌گذاری‌شده بر پایه آخرین قیمت خرید ثبت‌شده.</p><Link to="/accounting?section=inventory" className="pro-btn-primary">بازکردن گزارش موجودی</Link></article>
                <article className="pro-product-card"><h2>گردش کالا</h2><p className="pro-muted">بررسی گردش‌های ثبت‌شدهٔ ورود و خروج کالا.</p><Link to="/accounting?section=stock-flow" className="pro-btn-primary">بازکردن گردش کالا</Link></article>
              </> : null}
              {mainSection === "purchases" ? <article className="pro-product-card"><h2>خرید / ورود موجودی</h2><p className="pro-muted">ثبت خرید و ورود فیزیکی کالا.</p><Link to="/purchase" className="pro-btn-primary">بازکردن خرید و موجودی</Link></article> : null}
              {mainSection === "reports" ? <>
                <article className="pro-product-card"><h2>گزارش فروش</h2><p className="pro-muted">خلاصه فروش روز جاری.</p><Link to="/accounting?section=sales" className="pro-btn-primary">بازکردن گزارش فروش</Link></article>
                <article className="pro-product-card"><h2>گزارش موجودی</h2><p className="pro-muted">موجودی و ارزش کالاها.</p><Link to="/accounting?section=inventory" className="pro-btn-primary">بازکردن گزارش موجودی</Link></article>
                <article className="pro-product-card"><h2>گردش کالا</h2><p className="pro-muted">گزارش گردش‌های ثبت‌شدهٔ کالا.</p><Link to="/accounting?section=stock-flow" className="pro-btn-primary">بازکردن گردش کالا</Link></article>
                <article className="pro-product-card"><h2>گزارش مالی</h2><p className="pro-muted">خلاصه گزارش مالی موجود.</p><Link to="/accounting?section=finance-report" className="pro-btn-primary">بازکردن گزارش مالی</Link></article>
              </> : null}
            </div>
          </section>
        )}

        {pageView === "content" && active === "home" && (
          <section className="pro-panel">
            <h1>داشبورد HBI</h1>
            <p className="pro-lead">میانبرهای عملیات در اولویت‌اند. خلاصه‌ها و هشدارهای زیر از APIهای مدیریتی خوانده می‌شوند؛ دادهٔ ناموجود به‌صورت عدد ساختگی نمایش داده نمی‌شود.</p>

            <section aria-labelledby="dashboard-actions-title">
              <h2 id="dashboard-actions-title">اقدام سریع</h2>
              <div className="pro-product-grid">
                <article className="pro-product-card">
                  <h3>فروش مستقیم</h3>
                  <p className="pro-muted">ثبت فروش، مستقل از پروندهٔ مشاوره.</p>
                  <button type="button" className="pro-btn-primary" onClick={() => go("sales")}>ثبت فروش</button>
                </article>
                <article className="pro-product-card">
                  <h3>مشتریان</h3>
                  <p className="pro-muted">جست‌وجو، ایجاد پروفایل و سابقهٔ خرید.</p>
                  <div className="pro-actions">
                    <button type="button" className="pro-btn-primary" onClick={() => go("previous")}>جست‌وجوی مشتری</button>
                    <button type="button" className="pro-btn-secondary" onClick={() => go("profile")}>مشتری جدید</button>
                  </div>
                </article>
                <article className="pro-product-card">
                  <h3>مشاوره</h3>
                  <p className="pro-muted">ثبت مسئله، اعتبارسنجی نیاز و تصمیم اپراتور.</p>
                  <button type="button" className="pro-btn-primary" onClick={() => go("consult")}>شروع مشاوره</button>
                </article>
                <article className="pro-product-card">
                  <h3>ورود اطلاعات محصول</h3>
                  <p className="pro-muted">ثبت مشخصات محصول؛ جدا از ورود فیزیکی موجودی.</p>
                  <button type="button" className="pro-btn-primary" onClick={() => go("intake")}>ورود محصول</button>
                </article>
                <article className="pro-product-card">
                  <h3>بررسی و تأیید QA</h3>
                  <p className="pro-muted">بررسی وضعیت و موانع تأیید محصول.</p>
                  <button type="button" className="pro-btn-secondary" onClick={() => go("review")}>رفتن به بررسی QA</button>
                </article>
                <article className="pro-product-card">
                  <h3>خرید و ورود موجودی</h3>
                  <p className="pro-muted">ثبت ورود فیزیکی کالا و گردش انبار.</p>
                  <Link to="/purchase" className="pro-btn-secondary">ثبت خرید / ورود موجودی</Link>
                </article>
              </div>
            </section>

            <section aria-labelledby="dashboard-summary-title">
              <div className="pro-section-head">
                <h2 id="dashboard-summary-title">خلاصهٔ عملیات</h2>
                <button type="button" className="pro-btn-secondary" onClick={() => void refreshDashboard()} disabled={dashboardLoading}>
                  {dashboardLoading ? "در حال دریافت…" : "نوسازی داده‌ها"}
                </button>
              </div>
              {dashboardError && <p className="pro-error" role="status">{dashboardError}</p>}
              <div className="pro-product-grid">
                <article className="pro-product-card">
                  <h3>فروش امروز</h3>
                  <p className="pro-summary">{dashboardSales ? dashboardSales.sale_count.toLocaleString("fa-IR") : "—"} تراکنش</p>
                  <p className="pro-muted">{dashboardSales ? dashboardSales.revenue_toman.toLocaleString("fa-IR") + " تومان درآمد ثبت‌شده" : "دادهٔ فروش در دسترس نیست."}</p>
                  <Link to="/accounting" className="pro-btn-secondary">گزارش فروش</Link>
                </article>
                <article className="pro-product-card">
                  <h3>موجودی انبار</h3>
                  <p className="pro-summary">{dashboardInventory ? dashboardInventory.length.toLocaleString("fa-IR") : "—"} ردیف موجودی</p>
                  <p className="pro-muted">{dashboardInventory ? "بر اساس گزارش موجودی فعلی." : "دادهٔ موجودی در دسترس نیست."}</p>
                  <Link to="/accounting" className="pro-btn-secondary">مشاهدهٔ موجودی</Link>
                </article>
                <article className="pro-product-card">
                  <h3>هشدار موجودی کم</h3>
                  <p className="pro-summary">{dashboardLowStock ? dashboardLowStock.length.toLocaleString("fa-IR") : "—"} قلم</p>
                  <p className="pro-muted">آستانهٔ هشدار: موجودی قابل دسترس ≤ ۵؛ از گزارش رسمی موجودی کم.</p>
                  <Link to="/accounting" className="pro-btn-secondary">بررسی موجودی</Link>
                </article>
              </div>
            </section>

            <section aria-labelledby="dashboard-alerts-title">
              <h2 id="dashboard-alerts-title">موارد نیازمند توجه</h2>
              <div className="pro-product-card">
                {dashboardLowStock === null ? (
                  <p className="pro-muted">هشدار موجودی کم قابل تأیید نیست؛ گزارش موجودی در دسترس نیست.</p>
                ) : dashboardLowStock.length === 0 ? (
                  <p className="pro-muted">طبق آستانهٔ ۵، موردی در گزارش موجودی کم ثبت نشده است.</p>
                ) : (
                  <>
                    <p role="status">{dashboardLowStock.length.toLocaleString("fa-IR")} قلم با موجودی ≤ ۵ نیازمند بررسی است.</p>
                    <Link to="/accounting" className="pro-btn-primary">بازکردن گزارش موجودی</Link>
                  </>
                )}
                <p className="pro-muted">وضعیت پذیرش و QA محصول در این داشبورد عددگذاری نشده؛ API مدیریتیِ تأییدشده برای خلاصهٔ چرخهٔ محصول هنوز احراز نشده است.</p>
              </div>
            </section>

            <section aria-labelledby="dashboard-activity-title">
              <h2 id="dashboard-activity-title">آخرین گردش‌های انبار</h2>
              <div className="pro-product-card">
                {dashboardMovements === null ? (
                  <p className="pro-muted">گردش اخیر در دسترس نیست؛ گزارش حسابداری را بررسی کنید.</p>
                ) : dashboardMovements.length === 0 ? (
                  <p className="pro-muted">گردشی برای نمایش ثبت نشده است.</p>
                ) : (
                  <ul className="pro-ol">
                    {dashboardMovements.map((movement) => (
                      <li key={movement.movement_id}>
                        {movement.movement_type} · {movement.product_id} · تغییر {movement.quantity_delta.toLocaleString("fa-IR")} · موجودی پس از عملیات {movement.quantity_after.toLocaleString("fa-IR")}
                        {movement.created_at ? ` · ${new Date(movement.created_at).toLocaleString("fa-IR")}` : ""}
                      </li>
                    ))}
                  </ul>
                )}
                <Link to="/accounting" className="pro-btn-secondary">همهٔ گردش‌ها</Link>
              </div>
            </section>
          </section>
        )}

        {pageView === "content" && active === "previous" && (
          <section className="pro-panel">
            <h1>مشتری قبلی / جست‌وجو</h1>
            <p className="pro-lead">مشتری را پیدا کنید، سابقه او را بارگذاری کنید و سپس مشکل امروز را در یک پرونده جدید ثبت کنید.</p>
            <form className="pro-actions" onSubmit={(e) => { e.preventDefault(); void searchPreviousCustomers(); }}>
              <input
                className="pro-input"
                value={customerSearch}
                onChange={(e) => setCustomerSearch(e.target.value)}
                placeholder="نام یا شماره موبایل مشتری…"
                aria-label="جست‌وجوی مشتری قبلی با نام یا موبایل"
              />
              <button type="submit" className="pro-btn-primary" disabled={customerSearchBusy}>
                {customerSearchBusy ? "در حال جست‌وجو…" : "جست‌وجو"}
              </button>
            </form>
            {purchaseHistory.length > 0 ? (
              <div className="pro-panel" style={{ marginTop: "1rem" }}>
                <h2>سابقه خرید</h2>
                <div className="pro-product-grid">
                  {purchaseHistory.map((sale) => (
                    <article key={sale.sale_id} className="pro-product-card">
                      <h3>{sale.sale_id}</h3>
                      {(sale.items ?? []).map((item) => (
                        <p key={item.sale_item_id} className="pro-muted">
                          محصول: {item.product_id} · تعداد: {item.quantity} · Recommendation: {item.recommendation_id ?? "—"}
                        </p>
                      ))}
                    </article>
                  ))}
                </div>
              </div>
            ) : null}
            {customerSearchResults.length > 0 ? (
              <div className="pro-product-grid" style={{ marginTop: "1rem" }}>
                {customerSearchResults.map((customer) => (
                  <article key={customer.customer_id} className="pro-product-card">
                    <h3>{customer.name}</h3>
                    <p className="pro-muted">{customer.mobile ?? "موبایل ثبت نشده"}</p>
                    <p className="pro-muted">{customer.concerns ?? "سابقه دغدغه ثبت نشده"}</p>
                    <button type="button" className="pro-btn-primary" onClick={() => void selectPreviousCustomer(customer)} disabled={busy}>
                      انتخاب مشتری
                    </button>
                  </article>
                ))}
              </div>
            ) : customerSearch.trim() && !customerSearchBusy ? (
              <div className="pro-empty"><strong>مشتری‌ای با این نام پیدا نشد.</strong></div>
            ) : null}
          </section>
        )}

        {pageView === "content" && active === "consult" && (
          <section className="pro-panel">
            {purchaseHistory.length > 0 ? (
              <div className="pro-panel" style={{ marginBottom: "1rem" }}>
                <h2>سابقه خرید مشتری</h2>
                <div className="pro-product-grid">
                  {purchaseHistory.map((sale) => (
                    <article key={sale.sale_id} className="pro-product-card">
                      <h3>{sale.sale_id}</h3>
                      {(sale.items ?? []).map((item) => (
                        <p key={item.sale_item_id} className="pro-muted">
                          محصول: {item.product_id} · تعداد: {item.quantity} · Recommendation: {item.recommendation_id ?? "—"}
                        </p>
                      ))}
                    </article>
                  ))}
                </div>
              </div>
            ) : null}
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
                <legend>۲) لاین مشاوره</legend>
                <div className="pro-checks pro-checks-inline">
                  {CONSULTATION_LINES.map((line) => (
                    <label key={line.id} className="pro-check-card sm">
                      <input
                        type="checkbox"
                        checked={consultationLine === line.id}
                        onChange={() => setConsultationLine(consultationLine === line.id ? "" : line.id)}
                      />
                      <span>{line.label}</span>
                    </label>
                  ))}
                </div>
                <p className="pro-muted">این انتخاب محدوده همین مشاوره را مشخص می‌کند.</p>
              </fieldset>
              <fieldset className="pro-fieldset">
                <legend>۳) موضوع مشاوره</legend>
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
                <legend>۴) نوع پوست</legend>
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
                <legend>۵) توضیح</legend>
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

        {pageView === "content" && active === "profile" && (
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

        {pageView === "content" && active === "catalog" && (
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
                    <button
                      type="button"
                      className="pro-btn-primary"
                      onClick={() => {
                        sessionStorage.setItem("hbi_review_product_id", p.product_id);
                        go("review");
                      }}
                    >
                      بررسی پرونده
                    </button>
                  </div>
                </article>
              ))}
            </div>
          </section>
        )}

        {pageView === "content" && active === "review" && (
          <ProductReviewPanel
            token={sessionStorage.getItem("hbi_po_access_token")}
            productId={sessionStorage.getItem("hbi_review_product_id")}
            onEnsureSession={ensureReviewSession}
            onProductChanged={() => void loadProducts()}
          />
        )}

        {pageView === "content" && active === "intake" && (
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

        {pageView === "content" && active === "results" && (
          <section className="pro-panel">
            <h1>پیشنهادهای نهایی برای اپراتور</h1>
            {(() => {
              const eligibleRecs = recs.filter((r) => (r.eligibility_status ?? r.eligibility ?? "").trim().toUpperCase() === "ELIGIBLE");
              const rejectedRecs = recs.filter((r) => (r.eligibility_status ?? r.eligibility ?? "").trim().toUpperCase() !== "ELIGIBLE");
              return (
                <>
            {!recDone && <p className="pro-muted">هنوز پیشنهادی گرفته نشده — از مشاوره شروع کنید.</p>}
            {recDone && eligibleRecs.length === 0 && (
              <div className="pro-empty">
                <strong>پیشنهاد واجد شرایطی یافت نشد.</strong>
                <p>موارد ردشده، در صورت وجود، در بخش داخلی زیر برای بررسی ثبت شده‌اند.</p>
              </div>
            )}
            <div className="pro-rec-list">
              {eligibleRecs.slice(0, showAllRecommendations ? eligibleRecs.length : INITIAL_RECOMMENDATION_LIMIT).map((r, i) => {
                const product = sellableProducts.find((p) => p.product_id === r.product_id);
                return (
                  <article key={r.recommendation_id || `${r.product_id}-${i}`} className="pro-rec-card">
                    <div className="pro-rec-rank">#{i + 1}</div>
                    <div>
                      <h3>{product?.product_name ?? r.product_id}</h3>
                      {product?.brand ? <p className="pro-muted">{product.brand}</p> : null}
                      <p className="pro-lead">این محصول با نیاز ثبت‌شده شما برای ادامه بررسی مطابقت دارد.</p>
                      <div className="pro-tags">
                        <span className="pro-tag">تطابق با نیاز: {formatMatchLevel(r.need_match_score)}</span>
                        <span className="pro-tag">وضعیت پیشنهاد: {formatRecommendationStatus(r.eligibility_status ?? r.eligibility)}</span>
                        <span className="pro-tag">موجودی: {formatRecommendationAvailability(r.availability)}</span>
                      </div>
                      <p className="pro-muted">اطمینان سیستم: {formatConfidenceLevel(r.confidence)}</p>
                      <details className="pro-technical-details">
                        <summary>جزئیات فنی</summary>
                        <dl className="pro-dl">
                          <div><dt>شناسه محصول</dt><dd>{r.product_id}</dd></div>
                          <div><dt>شناسه پیشنهاد</dt><dd>{r.recommendation_id}</dd></div>
                          {r.need_match_score != null ? <div><dt>Need Match</dt><dd>{r.need_match_score.toFixed(2)}</dd></div> : null}
                          {r.evidence_score != null ? <div><dt>Evidence</dt><dd>{r.evidence_score.toFixed(2)}</dd></div> : null}
                          {r.ranking_score != null ? <div><dt>Ranking</dt><dd>{r.ranking_score.toFixed(2)}</dd></div> : null}
                          {r.final_score != null ? <div><dt>Final</dt><dd>{r.final_score.toFixed(2)}</dd></div> : null}
                          {r.reasoning ? <div><dt>ReasoningEngine</dt><dd>{r.reasoning}</dd></div> : null}
                        </dl>
                      </details>
                    </div>
                  </article>
                );
              })}
            </div>
            {eligibleRecs.length > INITIAL_RECOMMENDATION_LIMIT && !showAllRecommendations ? (
              <div className="pro-actions">
                <button type="button" className="pro-btn-secondary" onClick={() => setShowAllRecommendations(true)}>
                  نمایش همه پیشنهادها ({eligibleRecs.length})
                </button>
              </div>
            ) : null}
            {rejectedRecs.length > 0 ? (
              <section className="pro-panel" style={{ marginTop: "1rem" }} aria-label="موارد ارزیابی‌شده و ردشده">
                <h2>سوابق داخلی محصولات ردشده</h2>
                <p className="pro-muted">این موارد برای بررسی تیم نگهداری می‌شوند و پیشنهاد نهایی نیستند؛ از این بخش امکان انتخاب برای فروش وجود ندارد.</p>
                <div className="pro-rec-list">
                  {rejectedRecs.map((r) => (
                    <article key={r.recommendation_id} className="pro-rec-card">
                      <div><h3>{sellableProducts.find((p) => p.product_id === r.product_id)?.product_name ?? r.product_id}</h3>
                        <p className="pro-muted">شناسه محصول: {r.product_id}</p>
                        <p><strong>دلیل اصلی:</strong> {formatExclusionReason(r.exclusion_reasons?.[0])}</p>
                        <p className="pro-muted">وضعیت: {formatRecommendationStatus(r.eligibility_status ?? r.eligibility)}</p>
                        {r.warnings?.length ? <p className="pro-muted">تذکرها: {r.warnings.map((w) => String(w)).join("؛ ")}</p> : null}
                        <p className="pro-muted">تعداد ارجاعات شواهد: {r.evidence_refs?.length ?? 0}</p>
                      </div>
                    </article>
                  ))}
                </div>
              </section>
            ) : null}
                </>
              );
            })()}
          </section>
        )}

        {pageView === "content" && active === "sales" && (
          <section className="pro-panel" id="sales">
            <h1>ثبت فروش</h1>
            <p className="pro-lead">ثبت فروش مستقیم بدون مشاوره و بدون ثبت مشتری اجباری است. در صورت انتخاب مشتری، سابقهٔ خرید نیز به او متصل می‌شود.</p>
            <form className="pro-form" onSubmit={onSaleSubmit}>
                <fieldset className="pro-fieldset">
                  <legend>مشتری (اختیاری)</legend>
                  {saleCustomerId ? (
                    <div className="pro-actions">
                      <p className="pro-muted">مشتری انتخاب‌شده برای این فروش: <strong>{saleCustomerLabel}</strong> · <code>{saleCustomerId}</code></p>
                      <button type="button" className="pro-btn-secondary" onClick={() => { setSaleCustomerId(null); setSaleCustomerLabel(null); }}>حذف مشتری از این فروش</button>
                    </div>
                  ) : (
                    <>
                      <label className="pro-label" htmlFor="sale-customer-search">جست‌وجوی مشتری با شماره موبایل یا نام خانوادگی</label>
                      <input id="sale-customer-search" className="pro-input" value={saleCustomerSearch} onChange={(e) => setSaleCustomerSearch(e.target.value)} placeholder="شماره موبایل یا نام خانوادگی" />
                      <button type="button" className="pro-btn-secondary" onClick={() => void searchSaleCustomers()} disabled={customerSearchBusy}>{customerSearchBusy ? "در حال جست‌وجو…" : "جست‌وجوی مشتری"}</button>
                      {customerSearchResults.map((customer) => (
                        <button key={customer.customer_id} type="button" className="pro-btn-secondary" onClick={() => chooseSaleCustomer(customer)}>
                          {customer.name ?? "بدون نام"} · {customer.mobile ?? "بدون موبایل"} · {customer.customer_id}
                        </button>
                      ))}
                      <p className="pro-muted">می‌توانید بدون انتخاب مشتری فروش را ثبت کنید. برای مشتری جدید هم ثبت مشاوره پیش‌نیاز نیست.</p>
                    </>
                  )}
                  <p className="pro-muted">جمع فروش: {totalSales === null ? "—" : totalSales.toLocaleString("fa-IR")}</p>
                </fieldset>
                <fieldset className="pro-fieldset">
                  <legend>اقلام</legend>
                  <label className="pro-label" htmlFor="sale-product">
                    محصول
                  </label>
                  {saleProductsError ? <p className="pro-error" role="status">{saleProductsError}</p> : null}
                  <select id="sale-product" className="pro-input" value={saleProductId} onChange={(e) => {
                      setSaleProductId(e.target.value);
                    }}>
                    <option value="">— انتخاب از کاتالوگ —</option>
                    {sellableProducts.map((p) => (
                      <option key={p.product_id} value={p.product_id}>
                        {p.product_name} ({p.brand})
                      </option>
                    ))}
                  </select>
                  {sellableProducts.length === 0 && !saleProductsError ? <p className="pro-muted">هنوز محصول قابل انتخابی در کاتالوگ فروش موجود نیست.</p> : null}
                  <div className="pro-grid-2">
                    <div>
                      <label className="pro-label" htmlFor="sale-qty">
                        تعداد
                      </label>
                      <input id="sale-qty" className="pro-input" type="number" min={1} value={saleQty} onChange={(e) => setSaleQty(Number(e.target.value) || 1)} />
                    </div>
                    <div>
                      <span className="pro-label">قیمت واحد (تومان)</span>
                      <p className="pro-input" aria-live="polite">
                        {salePrice == null ? "در حال دریافت…" : salePrice.toLocaleString("fa-IR")}
                      </p>
                    </div>
                  </div>
                  <p className="pro-muted">
                    موجودی قابل فروش: {saleStock == null ? "در حال دریافت…" : saleStock.toLocaleString("fa-IR")}
                  </p>
                  <p className="pro-summary">
                    مبلغ: <strong>{salePrice == null ? "—" : (saleQty * salePrice).toLocaleString("fa-IR")}</strong> تومان
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

        {pageView === "content" && active === "about" && (
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
      <footer className="pro-footer">HBI · گالری مقصودی · فضای کاری مدیر</footer>
    </div>
  );
}
