/**
 * PHASE 03 — HBI Accounting Home (UI shell only).
 * No business logic, no fake summary numbers, no Phase 04+ features.
 */
import { Link } from "react-router-dom";

const MENU_ITEMS: { id: string; label: string; status: "active" | "later" }[] = [
  { id: "sales", label: "فروش", status: "later" },
  { id: "inventory", label: "موجودی", status: "later" },
  { id: "stock-in", label: "ورود کالا", status: "later" },
  { id: "stock-flow", label: "گردش کالا", status: "later" },
  { id: "sales-report", label: "گزارش فروش", status: "later" },
  { id: "finance-report", label: "گزارش مالی", status: "later" },
  { id: "customers", label: "مشتریان", status: "later" },
  { id: "settings", label: "تنظیمات", status: "later" },
];

const SUMMARY_CARDS: { id: string; label: string }[] = [
  { id: "sales-today", label: "فروش امروز" },
  { id: "sales-count", label: "تعداد فروش" },
  { id: "inventory-value", label: "ارزش موجودی" },
  { id: "gross-profit", label: "سود ناخالص" },
];

export default function AccountingHomePage() {
  return (
    <div className="acc-root" dir="rtl">
      <header className="acc-header">
        <div className="acc-header-inner">
          <div className="acc-brand">
            <span className="acc-brand-mark">HBI</span>
            <div>
              <div className="acc-brand-title">حسابداری</div>
              <div className="acc-brand-sub">HBI Accounting Home · زیرسیستم حسابداری</div>
            </div>
          </div>
          <Link to="/" className="acc-back-btn">
            بازگشت به خانه HBI
          </Link>
        </div>
      </header>

      <main className="acc-main">
        <section className="acc-panel">
          <h1>خانه حسابداری</h1>
          <p className="acc-lead">
            کنسول عملیاتی حسابداری HBI. در این نسخه فقط پوستهٔ ناوبری و خلاصه آماده است؛
            منطق کسب‌وکار و گزارش‌ها در فازهای بعدی متصل می‌شوند.
          </p>
        </section>

        <section className="acc-panel" aria-labelledby="acc-summary-title">
          <h2 id="acc-summary-title">خلاصه</h2>
          <div className="acc-summary-grid">
            {SUMMARY_CARDS.map((card) => (
              <article key={card.id} className="acc-summary-card">
                <h3>{card.label}</h3>
                <p className="acc-summary-value acc-unavailable" title="endpoint حسابداری Phase 03 متصل نشده">
                  در دسترس نیست
                </p>
                <p className="acc-summary-note">هنوز متصل نشده · TODO: Phase 05+ summary API</p>
              </article>
            ))}
          </div>
        </section>

        <section className="acc-panel" aria-labelledby="acc-menu-title">
          <h2 id="acc-menu-title">منوی حسابداری</h2>
          <nav className="acc-menu" aria-label="منوی حسابداری">
            {MENU_ITEMS.map((item) => (
              <button
                key={item.id}
                type="button"
                className="acc-menu-item"
                disabled={item.status === "later"}
                title={item.status === "later" ? "در فازهای بعدی فعال می‌شود" : undefined}
              >
                <span className="acc-menu-label">{item.label}</span>
                {item.status === "later" ? (
                  <span className="acc-menu-badge">مرحله بعد</span>
                ) : null}
              </button>
            ))}
            <Link to="/" className="acc-menu-item acc-menu-back">
              <span className="acc-menu-label">بازگشت</span>
            </Link>
          </nav>
        </section>
      </main>

      <footer className="acc-footer">HBI Accounting · فاز ۰۳ · فقط UI/Navigation</footer>
    </div>
  );
}
