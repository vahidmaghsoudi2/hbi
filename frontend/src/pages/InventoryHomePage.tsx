import { useCallback, useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { getInventoryReport, getLowStockReport, getStockMovements } from "../api/client";
import type { InventoryReportRow, StockMovementDTO } from "../types/api";

type Section = "inventory" | "low-stock" | "stock-flow";

function formatNumber(value: number | null | undefined): string {
  return value == null ? "—" : value.toLocaleString("fa-IR");
}
function formatMoneyToman(value: number | null | undefined): string {
  return value == null ? "—" : `${value.toLocaleString("fa-IR")} تومان`;
}

function sectionFromQuery(requested: string | null): Section {
  if (requested === "stock-flow") return "stock-flow";
  if (requested === "low-stock") return "low-stock";
  return "inventory";
}

export default function InventoryHomePage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const requested = searchParams.get("section");
  const [section, setSection] = useState<Section>(() => sectionFromQuery(requested));
  const [adminToken] = useState(() => sessionStorage.getItem("hbi_admin_access_token"));
  const [inventory, setInventory] = useState<InventoryReportRow[] | null>(null);
  const [lowStock, setLowStock] = useState<InventoryReportRow[] | null>(null);
  const [movements, setMovements] = useState<StockMovementDTO[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [reportErrors, setReportErrors] = useState<Record<Section, string | null>>({ inventory: null, "low-stock": null, "stock-flow": null });

  const refresh = useCallback(async () => {
    const token = sessionStorage.getItem("hbi_admin_access_token");
    if (!token) {
      setInventory(null);
      setLowStock(null);
      setMovements(null);
      setReportErrors({ inventory: "نشست مدیر موجود نیست؛ دوباره وارد شوید.", "low-stock": "نشست مدیر موجود نیست؛ دوباره وارد شوید.", "stock-flow": "نشست مدیر موجود نیست؛ دوباره وارد شوید." });
      return;
    }
    setLoading(true);
    setReportErrors({ inventory: null, "low-stock": null, "stock-flow": null });
    const results = await Promise.allSettled([
      getInventoryReport(token),
      getLowStockReport(5, token),
      getStockMovements(token, { limit: 100 }),
    ]);
    if (results[0].status === "fulfilled") setInventory(Array.isArray(results[0].value) ? results[0].value : []);
    else setInventory(null);
    if (results[1].status === "fulfilled") setLowStock(Array.isArray(results[1].value) ? results[1].value : []);
    else setLowStock(null);
    if (results[2].status === "fulfilled") setMovements(Array.isArray(results[2].value) ? results[2].value : []);
    else setMovements(null);
    setReportErrors({
      inventory: results[0].status === "rejected" ? "دریافت گزارش موجودی ناموفق بود." : null,
      "low-stock": results[1].status === "rejected" ? "دریافت گزارش کمبود موجودی ناموفق بود." : null,
      "stock-flow": results[2].status === "rejected" ? "دریافت گزارش گردش کالا ناموفق بود." : null,
    });
    setLoading(false);
  }, []);

  useEffect(() => {
    setSection(sectionFromQuery(requested));
  }, [requested]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  function openSection(next: Section) {
    setSection(next);
    setSearchParams({ section: next });
  }

  return (
    <div className="acc-root">
      <header className="acc-header">
        <div className="acc-header-inner">
          <div>
            <p className="acc-kicker">HBI · کالا و موجودی</p>
            <h1>کالا و موجودی</h1>
            <p className="acc-lead">گزارش موجودی، کمبود و گردش کالا؛ جدا از مدیریت مشخصات محصول.</p>
          </div>
          <div className="acc-header-actions">
            <Link to="/" className="acc-link-btn">بازگشت به خانه HBI</Link>
            <Link to="/purchase" className="acc-link-btn">خرید / ورود کالا</Link>
            <button type="button" className="acc-link-btn" onClick={() => void refresh()} disabled={loading}>
              {loading ? "در حال بارگذاری…" : "بروزرسانی"}
            </button>
          </div>
        </div>
      </header>
      <main className="acc-main">
        {!adminToken && <p className="acc-error" role="alert">نشست مدیر لازم است.</p>}
        {adminToken && reportErrors[section] && <p className="acc-error" role="alert">{reportErrors[section]}</p>}
        <section className="acc-menu-panel">
          <nav className="acc-menu" aria-label="بخش‌های موجودی">
            <button type="button" className={`acc-menu-item ${section === "inventory" ? "selected" : ""}`} onClick={() => openSection("inventory")}>
              <span className="acc-menu-label">موجودی و ارزش کالا</span>
            </button>
            <button type="button" className={`acc-menu-item ${section === "low-stock" ? "selected" : ""}`} onClick={() => openSection("low-stock")}>
              <span className="acc-menu-label">کمبود موجودی</span>
            </button>
            <button type="button" className={`acc-menu-item ${section === "stock-flow" ? "selected" : ""}`} onClick={() => openSection("stock-flow")}>
              <span className="acc-menu-label">گردش کالا</span>
            </button>
          </nav>
        </section>

        {section === "inventory" && (
          <section className="acc-panel">
            <div className="acc-section-head">
              <h2>موجودی کالا</h2>
              <span className="acc-summary-note">ارزش‌گذاری بر پایهٔ آخرین قیمت خرید ثبت‌شده</span>
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
                  {(inventory ?? []).map((row) => (
                    <tr key={row.inventory_id}>
                      <td><code>{row.product_id}</code></td>
                      <td>{formatNumber(row.quantity_available)}</td>
                      <td>{formatMoneyToman(row.purchase_price_toman)}</td>
                      <td>{formatMoneyToman(row.inventory_value_toman)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {inventory?.length === 0 && <p className="acc-empty">دادهٔ موجودی برای نمایش وجود ندارد.</p>}
              {inventory === null && !reportErrors.inventory && <p className="acc-empty">دادهٔ موجودی در دسترس نیست.</p>}
            </div>
          </section>
        )}

        {section === "low-stock" && (
          <section className="acc-panel">
            <div className="acc-section-head">
              <h2>کمبود موجودی</h2>
              <span className="acc-summary-note">آستانهٔ کمبود: موجودی ≤ ۵</span>
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
                  {(lowStock ?? []).map((row) => (
                    <tr key={row.inventory_id}>
                      <td><code>{row.product_id}</code></td>
                      <td>{formatNumber(row.quantity_available)}</td>
                      <td>{formatMoneyToman(row.purchase_price_toman)}</td>
                      <td>{formatMoneyToman(row.inventory_value_toman)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {lowStock?.length === 0 && <p className="acc-empty">قلم کمبود موجودی در آستانهٔ ≤۵ ثبت نشده است.</p>}
              {lowStock === null && !reportErrors["low-stock"] && <p className="acc-empty">گزارش کمبود موجودی در دسترس نیست.</p>}
            </div>
          </section>
        )}

        {section === "stock-flow" && (
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
                  {(movements ?? []).map((row) => (
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
              {movements?.length === 0 && <p className="acc-empty">گردش کالایی برای نمایش ثبت نشده است.</p>}
              {movements === null && !reportErrors["stock-flow"] && <p className="acc-empty">گزارش گردش در دسترس نیست.</p>}
            </div>
          </section>
        )}
      </main>
      <footer className="acc-footer">HBI Inventory · مدیریت مشخصات محصول از موجودی فیزیکی جداست.</footer>
    </div>
  );
}
