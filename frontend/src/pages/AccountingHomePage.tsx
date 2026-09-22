import { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  getFinancialSummary,
  getInventoryReport,
  getLowStockReport,
  getSalesPeriod,
  getStockMovements,
} from "../api/client";
import type {
  FinancialSummaryDTO,
  InventoryReportRow,
  SalesReportDTO,
  StockMovementDTO,
} from "../types/api";

type Section = "sales" | "inventory" | "stock-flow" | "finance-report";

const MENU_ITEMS: { id: Section | "stock-in" | "customers" | "settings"; label: string; active: boolean }[] = [
  { id: "sales", label: "فروش", active: true },
  { id: "inventory", label: "موجودی", active: true },
  { id: "stock-in", label: "ورود کالا", active: false },
  { id: "stock-flow", label: "گردش کالا", active: true },
  { id: "sales-report", label: "گزارش فروش", active: true },
  { id: "finance-report", label: "گزارش مالی", active: true },
  { id: "customers", label: "مشتریان", active: false },
  { id: "settings", label: "تنظیمات", active: false },
];

function formatNumber(value: number | null | undefined): string {
  return value == null ? "—" : value.toLocaleString("fa-IR");
}

function formatMoneyToman(value: number | null | undefined): string {
  return value == null ? "—" : `${value.toLocaleString("fa-IR")} تومان`;
}

export default function AccountingHomePage() {
  const [adminToken, setAdminToken] = useState<string | null>(() =>
    sessionStorage.getItem("hbi_admin_access_token")
  );
  const [activeSection, setActiveSection] = useState<Section>("sales");
  const [sales, setSales] = useState<SalesReportDTO | null>(null);
  const [financial, setFinancial] = useState<FinancialSummaryDTO | null>(null);
  const [inventory, setInventory] = useState<InventoryReportRow[]>([]);
  const [lowStock, setLowStock] = useState<InventoryReportRow[]>([]);
  const [movements, setMovements] = useState<StockMovementDTO[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadDashboard = useCallback(async () => {
    const token = sessionStorage.getItem("hbi_admin_access_token");
    setAdminToken(token);
    if (!token) {
      setSales(null);
      setFinancial(null);
      setInventory([]);
      setLowStock([]);
      setMovements([]);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const [salesToday, financeToday, inventoryRows, lowRows, movementRows] = await Promise.all([
        getSalesPeriod("today", token),
        (() => {
          const now = new Date();
          const start = new Date(now);
          start.setHours(0, 0, 0, 0);
          const end = new Date(start);
          end.setDate(end.getDate() + 1);
          return getFinancialSummary(start.toISOString(), end.toISOString(), token);
        })(),
        getInventoryReport(token),
        getLowStockReport(5, token),
        getStockMovements(token, { limit: 100 }),
      ]);
      setSales(salesToday);
      setFinancial(financeToday);
      setInventory(Array.isArray(inventoryRows) ? inventoryRows : []);
      setLowStock(Array.isArray(lowRows) ? lowRows : []);
      setMovements(Array.isArray(movementRows) ? movementRows : []);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadDashboard();
  }, [loadDashboard]);

  const inventoryValue = useMemo(() => {
    if (!inventory.length) {
      return { usd: null as number | null, toman: null as number | null, missing: 0 };
    }
    let usd = 0;
    let toman = 0;
    let missing = 0;
    for (const row of inventory) {
      if (row.quantity_available <= 0) continue;
      if (row.inventory_value_usd == null || row.inventory_value_toman == null) {
        missing += 1;
        continue;
      }
      usd += row.inventory_value_usd;
      toman += row.inventory_value_toman;
    }
    return { usd: missing ? null : usd, toman: missing ? null : toman, missing };
  }, [inventory]);

  const activeTitle = {
    sales: "فروش امروز",
    inventory: "موجودی",
    "stock-flow": "گردش کالا",
    "finance-report": "گزارش مالی",
  }[activeSection];

  return (
    <div className="acc-root" dir="rtl">
      <header className="acc-header">
        <div className="acc-header-inner">
          <div className="acc-brand">
            <span className="acc-brand-mark">HBI</span>
            <div>
              <div className="acc-brand-title">حسابداری</div>
              <div className="acc-brand-sub">کنسول عملیاتی · مبتنی بر APIهای واقعی</div>
            </div>
          </div>
          <div className="acc-header-actions">
            <span className={`acc-auth-badge ${adminToken ? "ok" : "warn"}`}>
              {adminToken ? "نشست Admin فعال" : "نشست Admin لازم است"}
            </span>
            <Link to="/" className="acc-back-btn">بازگشت به خانه HBI</Link>
          </div>
        </div>
      </header>

      <main className="acc-main">
        <section className="acc-panel">
          <h1>خانه حسابداری</h1>
          <p className="acc-lead">
            خلاصه‌های زیر فقط از گزارش‌های موجود HBI خوانده می‌شوند. ارزش موجودی طبق تصمیم PO
            بر مبنای آخرین قیمت خرید ثبت‌شده محاسبه می‌شود.
          </p>
        </section>

        {!adminToken && (
          <section className="acc-panel acc-auth-panel">
            <h2>احراز هویت مدیریتی موردنیاز</h2>
            <p>
              APIهای گزارش فروش، موجودی و گزارش مالی با نقش <strong>Admin</strong> محافظت می‌شوند.
              این صفحه از توکن مشتری یا Editor برای دور زدن مجوز استفاده نمی‌کند.
            </p>
            <code>sessionStorage: hbi_admin_access_token</code>
            <p className="acc-summary-note">
              پس از ایجاد نشست Admin توسط مسیر احراز هویت مدیریتی محیط، صفحه را نوسازی کنید.
            </p>
          </section>
        )}

        {error && (
          <section className="acc-panel acc-error" role="alert">
            <strong>خطا در دریافت داده:</strong> {error}
          </section>
        )}

        <section className="acc-panel" aria-labelledby="acc-summary-title">
          <div className="acc-section-head">
            <h2 id="acc-summary-title">خلاصه</h2>
            <button type="button" className="acc-refresh-btn" onClick={() => void loadDashboard()} disabled={loading}>
              {loading ? "در حال دریافت…" : "نوسازی"}
            </button>
          </div>
          <div className="acc-summary-grid">
            <article className="acc-summary-card">
              <h3>فروش امروز</h3>
              <p className="acc-summary-value">{formatMoneyToman(sales?.revenue_toman)}</p>
              <p className="acc-summary-note">{formatNumber(sales?.sale_count)} فاکتور</p>
            </article>
            <article className="acc-summary-card">
              <h3>خالص درآمد امروز</h3>
              <p className="acc-summary-value">{formatMoneyToman(financial?.net_revenue_toman)}</p>
              <p className="acc-summary-note">درآمد − مرجوعی، طبق API مالی موجود</p>
            </article>
            <article className="acc-summary-card">
              <h3>ارزش موجودی</h3>
              <p className="acc-summary-value">
                {inventoryValue.toman == null ? "—" : formatMoneyToman(inventoryValue.toman)}
              </p>
              <p className="acc-summary-note">
                مبنا: تعداد موجود × آخرین قیمت خرید ثبت‌شده
                {inventoryValue.missing ? ` · ${inventoryValue.missing} قلم بدون قیمت خرید` : ""}
              </p>
            </article>
            <article className="acc-summary-card">
              <h3>سود ناخالص</h3>
              <p className="acc-summary-value acc-deferred">DEFERRED BY PO</p>
              <p className="acc-summary-note">COGS هنوز سیاست مصوب محاسبه ندارد.</p>
            </article>
          </div>
        </section>

        <section className="acc-panel" aria-labelledby="acc-menu-title">
          <div className="acc-section-head">
            <h2 id="acc-menu-title">منوی حسابداری</h2>
            <span className="acc-summary-note">بخش فعال: {activeTitle}</span>
          </div>
          <nav className="acc-menu" aria-label="منوی حسابداری">
            {MENU_ITEMS.map((item) => (
              item.active ? (
                <button
                  key={item.id}
                  type="button"
                  className={`acc-menu-item ${activeSection === item.id ? "selected" : ""}`}
                  onClick={() => setActiveSection(item.id as Section)}
                >
                  <span className="acc-menu-label">{item.label}</span>
                </button>
              ) : (
                <button key={item.id} type="button" className="acc-menu-item" disabled>
                  <span className="acc-menu-label">{item.label}</span>
                  <span className="acc-menu-badge">مرحله بعد</span>
                </button>
              )
            ))}
          </nav>
        </section>

        {activeSection === "sales" && (
          <section className="acc-panel">
            <div className="acc-section-head">
              <h2>فروش امروز</h2>
              <span className="acc-summary-note">GET /reports/sales/period/today</span>
            </div>
            <div className="acc-kpi-row">
              <span>تعداد فروش: <strong>{formatNumber(sales?.sale_count)}</strong></span>
              <span>درآمد: <strong>{formatMoneyToman(sales?.revenue_toman)}</strong></span>
              <span>USD: <strong>{formatNumber(sales?.revenue_usd)}</strong></span>
            </div>
          </section>
        )}

        {activeSection === "inventory" && (
          <section className="acc-panel">
            <div className="acc-section-head">
              <h2>موجودی کالا</h2>
              <span className="acc-summary-note">آخرین قیمت خرید</span>
            </div>
            <div className="acc-table-wrap">
              <table className="acc-table">
                <thead>
                  <tr>
                    <th>محصول</th>
                    <th>موجودی</th>
                    <th>آخرین خرید</th>
                    <th>ارزش موجودی</th>
                  </tr>
                </thead>
                <tbody>
                  {inventory.map((row) => (
                    <tr key={row.inventory_id}>
                      <td><code>{row.product_id}</code></td>
                      <td>{formatNumber(row.quantity_available)}</td>
                      <td>{formatMoneyToman(row.purchase_price_toman)}</td>
                      <td>{formatMoneyToman(row.inventory_value_toman)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {lowStock.length > 0 && (
                <p className="acc-summary-note">موجودی پایین (≤۵): {formatNumber(lowStock.length)} قلم</p>
              )}
              {!inventory.length && <p className="acc-empty">داده موجودی برای نمایش وجود ندارد.</p>}
            </div>
          </section>
        )}

        {activeSection === "stock-flow" && (
          <section className="acc-panel">
            <div className="acc-section-head">
              <h2>گردش کالا</h2>
              <span className="acc-summary-note">GET /inventory/movements · حداکثر ۱۰۰ رکورد</span>
            </div>
            <div className="acc-table-wrap">
              <table className="acc-table">
                <thead>
                  <tr>
                    <th>نوع</th>
                    <th>محصول</th>
                    <th>تغییر</th>
                    <th>موجودی بعد</th>
                    <th>مبلغ</th>
                  </tr>
                </thead>
                <tbody>
                  {movements.map((row) => (
                    <tr key={row.movement_id}>
                      <td>{row.movement_type}</td>
                      <td><code>{row.product_id}</code></td>
                      <td>{formatNumber(row.quantity_delta)}</td>
                      <td>{formatNumber(row.quantity_after)}</td>
                      <td>{formatMoneyToman(row.amount_toman)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {!movements.length && <p className="acc-empty">گردش کالایی برای نمایش وجود ندارد.</p>}
            </div>
          </section>
        )}

        {activeSection === "finance-report" && (
          <section className="acc-panel">
            <div className="acc-section-head">
              <h2>گزارش مالی عملیاتی</h2>
              <span className="acc-summary-note">GET /reports/financial · امروز</span>
            </div>
            <div className="acc-kpi-row">
              <span>درآمد: <strong>{formatMoneyToman(financial?.revenue_toman)}</strong></span>
              <span>مرجوعی: <strong>{formatMoneyToman(financial?.returns_toman)}</strong></span>
              <span>خالص: <strong>{formatMoneyToman(financial?.net_revenue_toman)}</strong></span>
            </div>
            <div className="acc-deferred-grid">
              <div><strong>COGS</strong><span>DEFERRED BY PO</span></div>
              <div><strong>سود ناخالص</strong><span>DEFERRED BY PO</span></div>
              <div><strong>تخفیف</strong><span>DEFERRED / UNSUPPORTED</span></div>
            </div>
          </section>
        )}
      </main>

      <footer className="acc-footer">
        HBI Accounting · ارزش موجودی = تعداد موجود × آخرین قیمت خرید ثبت‌شده
      </footer>
    </div>
  );
}
