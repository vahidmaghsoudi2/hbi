import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getInventoryReport, getLowStockReport, getSalesPeriod } from "../api/client";
import type { SalesReportDTO } from "../types/api";

function formatNumber(value: number | null | undefined): string {
  return value == null ? "—" : value.toLocaleString("fa-IR");
}

function formatMoneyToman(value: number | null | undefined): string {
  return value == null ? "—" : `${value.toLocaleString("fa-IR")} تومان`;
}

/**
 * A small, evidence-backed snapshot for the homepage.
 * Values come from existing Admin-authorized report APIs; no demo data or
 * inferred profitability is shown here.
 */
export default function HomeOperationalSummary() {
  const [sales, setSales] = useState<SalesReportDTO | null>(null);
  const [inventoryCount, setInventoryCount] = useState<number | null>(null);
  const [lowStockCount, setLowStockCount] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    const token = sessionStorage.getItem("hbi_admin_access_token");
    if (!token) {
      setSales(null);
      setInventoryCount(null);
      setLowStockCount(null);
      setError("برای دریافت وضعیت عملیاتی، نشست مدیر لازم است.");
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const [todaySales, inventoryRows, lowStockRows] = await Promise.all([
        getSalesPeriod("today", token),
        getInventoryReport(token),
        getLowStockReport(5, token),
      ]);
      setSales(todaySales);
      setInventoryCount(Array.isArray(inventoryRows) ? inventoryRows.length : 0);
      setLowStockCount(Array.isArray(lowStockRows) ? lowStockRows.length : 0);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return (
    <section className="hbi-ops-panel" aria-labelledby="hbi-ops-title">
      <div className="hbi-ops-heading">
        <div>
          <span className="hbi-kicker">LIVE OPERATIONAL SNAPSHOT</span>
          <h2 id="hbi-ops-title">وضعیت امروز</h2>
          <p>خلاصه از گزارش‌های واقعی سامانه؛ بدون دادهٔ نمایشی یا محاسبهٔ سود تأییدنشده.</p>
        </div>
        <div className="hbi-ops-actions">
          <button type="button" className="hbi-ops-refresh" onClick={() => void refresh()} disabled={loading}>
            {loading ? "در حال دریافت…" : "نوسازی اطلاعات"}
          </button>
          <Link className="hbi-ops-link" to="/accounting">گزارش‌های کامل ←</Link>
        </div>
      </div>

      {error && <p className="hbi-ops-error" role="alert">دریافت وضعیت کامل نشد: {error}</p>}

      <div className="hbi-ops-grid" aria-live="polite" aria-busy={loading}>
        <article className="hbi-ops-card">
          <span className="hbi-ops-label">فروش امروز</span>
          <strong>{loading && !sales ? "…" : formatMoneyToman(sales?.revenue_toman)}</strong>
          <small>{sales ? `${formatNumber(sales.sale_count)} فاکتور ثبت‌شده` : "بر اساس گزارش فروش روز"}</small>
        </article>
        <article className="hbi-ops-card">
          <span className="hbi-ops-label">اقلام گزارش موجودی</span>
          <strong>{loading && inventoryCount == null ? "…" : formatNumber(inventoryCount)}</strong>
          <small>تعداد ردیف‌های بازگشتی از گزارش موجودی</small>
        </article>
        <article className="hbi-ops-card">
          <span className="hbi-ops-label">اقلام کم‌موجودی</span>
          <strong>{loading && lowStockCount == null ? "…" : formatNumber(lowStockCount)}</strong>
          <small>طبق آستانهٔ گزارش فعلی: ۵ واحد</small>
        </article>
      </div>
      <p className="hbi-ops-footnote">سود ناخالص در این خلاصه نمایش داده نمی‌شود؛ سیاست بهای تمام‌شده باید مصوب باشد.</p>
    </section>
  );
}
