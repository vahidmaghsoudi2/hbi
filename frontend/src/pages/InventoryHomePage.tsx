import { useCallback, useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { getInventoryReport, getLowStockReport, getStockMovements } from "../api/client";
import type { InventoryReportRow, StockMovementDTO } from "../types/api";

type Section = "inventory" | "stock-flow";

function formatNumber(value: number | null | undefined): string {
  return value == null ? "—" : value.toLocaleString("fa-IR");
}
function formatMoneyToman(value: number | null | undefined): string {
  return value == null ? "—" : `${value.toLocaleString("fa-IR")} تومان`;
}

export default function InventoryHomePage() {
  const [searchParams] = useSearchParams();
  const requested = searchParams.get("section");
  const [section, setSection] = useState<Section>(requested === "stock-flow" ? "stock-flow" : "inventory");
  const [adminToken] = useState(() => sessionStorage.getItem("hbi_admin_access_token"));
  const [inventory, setInventory] = useState<InventoryReportRow[] | null>(null);
  const [lowStock, setLowStock] = useState<InventoryReportRow[] | null>(null);
  const [movements, setMovements] = useState<StockMovementDTO[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    const token = sessionStorage.getItem("hbi_admin_access_token");
    if (!token) {
      setInventory(null); setLowStock(null); setMovements(null);
      setError("نشست مدیر موجود نیست؛ دوباره وارد شوید.");
      return;
    }
    setLoading(true); setError(null);
    const results = await Promise.allSettled([
      getInventoryReport(token), getLowStockReport(5, token), getStockMovements(token, { limit: 100 }),
    ]);
    if (results[0].status === "fulfilled") setInventory(Array.isArray(results[0].value) ? results[0].value : []);
    else setInventory(null);
    if (results[1].status === "fulfilled") setLowStock(Array.isArray(results[1].value) ? results[1].value : []);
    else setLowStock(null);
    if (results[2].status === "fulfilled") setMovements(Array.isArray(results[2].value) ? results[2].value : []);
    else setMovements(null);
    const failed = results.filter((r) => r.status === "rejected").length;
    if (failed) setError(`دریافت ${failed} گزارش از ۳ گزارش موجودی/گردش ناموفق بود.`);
    setLoading(false);
  }, []);

  useEffect(() => { if (requested === "stock-flow") setSection("stock-flow"); else if (requested === "inventory") setSection("inventory"); }, [requested]);
  useEffect(() => { void refresh(); }, [refresh]);

  return (
    <div className="acc-root" dir="rtl">
      <header className="acc-header"><div className="acc-header-inner">
        <div className="acc-brand"><span className="acc-brand-mark">HBI</span><div>
          <div className="acc-brand-title">کالا و موجودی</div><div className="acc-brand-sub">موجودی فیزیکی و گردش انبار · مبتنی بر APIهای واقعی</div>
        </div></div>
        <div className="acc-header-actions"><span className={`acc-auth-badge ${adminToken ? "ok" : "warn"}`}>{adminToken ? "نشست Admin فعال" : "نشست Admin لازم است"}</span><Link to="/" className="acc-back-btn">بازگشت به خانه HBI</Link></div>
      </div></header>
      <main className="acc-main">
        <section className="acc-panel"><h1>کالا و موجودی</h1><p className="acc-lead">این بخش مالک گزارش موجودی، هشدار کمبود و گردش ورود/خروج کالاست. مدیریت مشخصات و تأیید محصول در بخش جداگانهٔ مدیریت محصولات انجام می‌شود.</p></section>
        {error && <section className="acc-panel acc-error" role="alert"><strong>خطا:</strong> {error}</section>}
        <section className="acc-panel"><div className="acc-section-head"><h2>عملیات انبار</h2><button type="button" className="acc-refresh-btn" onClick={() => void refresh()} disabled={loading}>{loading ? "در حال دریافت…" : "نوسازی"}</button></div>
          <nav className="acc-menu" aria-label="منوی کالا و موجودی">
            <button type="button" className={`acc-menu-item ${section === "inventory" ? "selected" : ""}`} onClick={() => setSection("inventory")}><span className="acc-menu-label">موجودی و ارزش کالا</span></button>
            <button type="button" className={`acc-menu-item ${section === "stock-flow" ? "selected" : ""}`} onClick={() => setSection("stock-flow")}><span className="acc-menu-label">گردش کالا</span></button>
          </nav>
        </section>
        {section === "inventory" && <section className="acc-panel"><div className="acc-section-head"><h2>موجودی کالا</h2><span className="acc-summary-note">ارزش‌گذاری بر پایهٔ آخرین قیمت خرید ثبت‌شده</span></div>
          <div className="acc-table-wrap"><table className="acc-table"><thead><tr><th>محصول</th><th>موجودی</th><th>آخرین خرید</th><th>ارزش موجودی</th></tr></thead><tbody>
            {(inventory ?? []).map((row) => <tr key={row.inventory_id}><td><code>{row.product_id}</code></td><td>{formatNumber(row.quantity_available)}</td><td>{formatMoneyToman(row.purchase_price_toman)}</td><td>{formatMoneyToman(row.inventory_value_toman)}</td></tr>)}
          </tbody></table>{lowStock === null ? <p className="acc-summary-note">گزارش موجودی پایین در دسترس نیست.</p> : <p className="acc-summary-note">موجودی پایین (≤۵): {formatNumber(lowStock.length)} قلم</p>}{inventory?.length === 0 && <p className="acc-empty">دادهٔ موجودی برای نمایش وجود ندارد.</p>}{inventory === null && !error && <p className="acc-empty">دادهٔ موجودی در دسترس نیست.</p>}</div>
        </section>}
        {section === "stock-flow" && <section className="acc-panel"><div className="acc-section-head"><h2>گردش کالا</h2><span className="acc-summary-note">GET /inventory/movements · حداکثر ۱۰۰ رکورد</span></div>
          <div className="acc-table-wrap"><table className="acc-table"><thead><tr><th>نوع</th><th>محصول</th><th>تغییر</th><th>موجودی بعد</th><th>مبلغ</th></tr></thead><tbody>
            {(movements ?? []).map((row) => <tr key={row.movement_id}><td>{row.movement_type}</td><td><code>{row.product_id}</code></td><td>{formatNumber(row.quantity_delta)}</td><td>{formatNumber(row.quantity_after)}</td><td>{formatMoneyToman(row.amount_toman)}</td></tr>)}
          </tbody></table>{movements?.length === 0 && <p className="acc-empty">گردش کالایی برای نمایش ثبت نشده است.</p>}{movements === null && !error && <p className="acc-empty">گزارش گردش در دسترس نیست.</p>}</div>
        </section>}
      </main><footer className="acc-footer">HBI Inventory · مدیریت مشخصات محصول از موجودی فیزیکی جداست.</footer>
    </div>
  );
}
