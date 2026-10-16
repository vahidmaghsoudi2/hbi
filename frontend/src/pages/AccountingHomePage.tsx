import { useCallback, useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { getFinancialSummary, getSalesPeriod } from "../api/client";
import type { FinancialSummaryDTO, SalesReportDTO } from "../types/api";

type Section = "sales" | "finance-report";
const MENU_ITEMS: { id: Section; label: string }[] = [
  { id: "sales", label: "فروش امروز" },
  { id: "finance-report", label: "گزارش مالی" },
];
function isSection(value: string | null): value is Section {
  return MENU_ITEMS.some((item) => item.id === value);
}
function formatNumber(value: number | null | undefined): string {
  return value == null ? "—" : value.toLocaleString("fa-IR");
}
function formatMoneyToman(value: number | null | undefined): string {
  return value == null ? "—" : `${value.toLocaleString("fa-IR")} تومان`;
}

export default function AccountingHomePage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const requestedSection = searchParams.get("section");
  const [adminToken, setAdminToken] = useState<string | null>(() => sessionStorage.getItem("hbi_admin_access_token"));
  const [activeSection, setActiveSection] = useState<Section>(() => isSection(requestedSection) ? requestedSection : "sales");
  const [sales, setSales] = useState<SalesReportDTO | null>(null);
  const [financial, setFinancial] = useState<FinancialSummaryDTO | null>(null);
  const [loading, setLoading] = useState(false);
  const [reportErrors, setReportErrors] = useState<Record<Section, string | null>>({ sales: null, "finance-report": null });

  const loadReports = useCallback(async () => {
    const token = sessionStorage.getItem("hbi_admin_access_token");
    setAdminToken(token);
    if (!token) {
      setSales(null); setFinancial(null);
      setReportErrors({ sales: "نشست مدیر موجود نیست؛ ابتدا وارد حساب مدیر شوید.", "finance-report": "نشست مدیر موجود نیست؛ ابتدا وارد حساب مدیر شوید." });
      return;
    }
    setLoading(true); setReportErrors({ sales: null, "finance-report": null });
    const now = new Date();
    const start = new Date(now); start.setHours(0, 0, 0, 0);
    const end = new Date(start); end.setDate(end.getDate() + 1);
    const results = await Promise.allSettled([
      getSalesPeriod("today", token),
      getFinancialSummary(start.toISOString(), end.toISOString(), token),
    ]);
    if (results[0].status === "fulfilled") setSales(results[0].value); else setSales(null);
    if (results[1].status === "fulfilled") setFinancial(results[1].value); else setFinancial(null);
    setReportErrors({
      sales: results[0].status === "rejected" ? "دریافت گزارش فروش ناموفق بود." : null,
      "finance-report": results[1].status === "rejected" ? "دریافت گزارش مالی ناموفق بود." : null,
    });
    setLoading(false);
  }, []);

  useEffect(() => { if (isSection(requestedSection)) setActiveSection(requestedSection); }, [requestedSection]);
  useEffect(() => { void loadReports(); }, [loadReports]);

  function openSection(next: Section) {
    setActiveSection(next);
    setSearchParams({ section: next });
  }

  const activeTitle = activeSection === "sales" ? "فروش امروز" : "گزارش مالی";
  return (
    <div className="acc-root" dir="rtl">
      <header className="acc-header"><div className="acc-header-inner">
        <div className="acc-brand"><span className="acc-brand-mark">HBI</span><div><div className="acc-brand-title">حسابداری و گزارش‌ها</div><div className="acc-brand-sub">گزارش فروش و مالی · مبتنی بر APIهای واقعی</div></div></div>
        <div className="acc-header-actions"><span className={`acc-auth-badge ${adminToken ? "ok" : "warn"}`}>{adminToken ? "نشست Admin فعال" : "نشست Admin لازم است"}</span><Link to="/" className="acc-back-btn">بازگشت به خانه HBI</Link></div>
      </div></header>
      <main className="acc-main">
        <section className="acc-panel"><h1>حسابداری و گزارش‌ها</h1><p className="acc-lead">این بخش فقط گزارش‌های مالی و فروش را نگه می‌دارد. موجودی و گردش فیزیکی کالا در فضای کاری مستقل «کالا و موجودی» قرار دارد.</p></section>
        {!adminToken && <section className="acc-panel acc-auth-panel"><h2>احراز هویت مدیریتی موردنیاز</h2><p>گزارش‌های فروش و مالی با نقش <strong>Admin</strong> محافظت می‌شوند.</p><code>sessionStorage: hbi_admin_access_token</code></section>}
        {adminToken && reportErrors[activeSection] && <section className="acc-panel acc-error" role="alert"><strong>خطا در دریافت داده:</strong> {reportErrors[activeSection]}</section>}
        <section className="acc-panel"><div className="acc-section-head"><h2>خلاصه</h2><button type="button" className="acc-refresh-btn" onClick={() => void loadReports()} disabled={loading}>{loading ? "در حال دریافت…" : "نوسازی"}</button></div>
          <div className="acc-summary-grid">
            <article className="acc-summary-card"><h3>فروش امروز</h3><p className="acc-summary-value">{formatMoneyToman(sales?.revenue_toman)}</p><p className="acc-summary-note">{reportErrors.sales ?? `${formatNumber(sales?.sale_count)} فاکتور`}</p></article>
            <article className="acc-summary-card"><h3>خالص درآمد امروز</h3><p className="acc-summary-value">{formatMoneyToman(financial?.net_revenue_toman)}</p><p className="acc-summary-note">{reportErrors["finance-report"] ?? "درآمد منهای مرجوعی، طبق API مالی موجود"}</p></article>
            <article className="acc-summary-card"><h3>سود ناخالص</h3><p className="acc-summary-value acc-deferred">DEFERRED</p><p className="acc-summary-note">COGS و سود ناخالص تا تأیید PO محاسبه نمی‌شوند</p></article>
          </div>
        </section>
        <section className="acc-layout">
          <nav className="acc-menu" aria-label="منوی حسابداری">{MENU_ITEMS.map((item) => <button key={item.id} type="button" className={`acc-menu-item ${activeSection === item.id ? "selected" : ""}`} onClick={() => openSection(item.id)}><span className="acc-menu-label">{item.label}</span></button>)}</nav>
        </section>
        {activeSection === "sales" && <section className="acc-panel"><div className="acc-section-head"><h2>فروش امروز</h2><span className="acc-summary-note">GET /reports/sales/period/today</span></div><div className="acc-kpi-row"><span>تعداد فروش: <strong>{formatNumber(sales?.sale_count)}</strong></span><span>درآمد: <strong>{formatMoneyToman(sales?.revenue_toman)}</strong></span><span>USD: <strong>{formatNumber(sales?.revenue_usd)}</strong></span></div></section>}
        {activeSection === "finance-report" && <section className="acc-panel"><div className="acc-section-head"><h2>گزارش مالی عملیاتی</h2><span className="acc-summary-note">GET /reports/financial · امروز</span></div><div className="acc-kpi-row"><span>درآمد: <strong>{formatMoneyToman(financial?.revenue_toman)}</strong></span><span>مرجوعی: <strong>{formatMoneyToman(financial?.returns_toman)}</strong></span><span>خالص: <strong>{formatMoneyToman(financial?.net_revenue_toman)}</strong></span></div><div className="acc-deferred-grid"><div><strong>COGS</strong><span>DEFERRED BY PO</span></div><div><strong>سود ناخالص</strong><span>DEFERRED BY PO</span></div><div><strong>تخفیف</strong><span>DEFERRED / UNSUPPORTED</span></div></div></section>}
      </main><footer className="acc-footer">HBI Accounting · گزارش فروش و مالی</footer>
    </div>
  );
}
