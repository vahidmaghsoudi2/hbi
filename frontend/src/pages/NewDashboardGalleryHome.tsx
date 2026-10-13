import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "../styles/dashboard-gallery.css";
import "../styles/homepage-navigation.css";

type NavChild = { label: string; to: string };
type NavItem = {
  label: string;
  detail: string;
  icon: string;
  to: string;
  current?: boolean;
  children: NavChild[];
};

const navigation: NavItem[] = [
  { label: "خانه و داشبورد", detail: "نمای کلی عملیات", icon: "⌂", to: "/", current: true, children: [] },
  {
    label: "کالا و انبار",
    detail: "کاتالوگ و موجودی",
    icon: "▦",
    to: "/catalog",
    children: [
      { label: "کاتالوگ کالاها", to: "/catalog" },
      { label: "خرید و ورود موجودی", to: "/purchase" },
      { label: "بررسی پرونده کالا", to: "/workspace?panel=review" },
    ],
  },
  {
    label: "مشتری و مشاوره",
    detail: "پرونده، مراجعه و نتایج",
    icon: "◎",
    to: "/workspace?panel=consult",
    children: [
      { label: "ثبت مراجعه و مشاوره", to: "/workspace?panel=consult" },
      { label: "پرونده مشتری", to: "/workspace?panel=profile" },
      { label: "سوابق مراجعه", to: "/workspace?panel=previous" },
      { label: "نتایج ارزیابی و پیشنهاد", to: "/workspace?panel=results" },
    ],
  },
  { label: "فروش", detail: "ثبت فروش مستقیم", icon: "↗", to: "/workspace?panel=sales", children: [] },
  { label: "مالی و حسابداری", detail: "گزارش‌ها و امور مالی", icon: "▤", to: "/accounting", children: [] },
];

const quickActions = [
  {
    title: "ثبت فروش",
    description: "فروش مستقیم؛ مشاوره پیش‌نیاز نیست",
    icon: "↗",
    to: "/workspace?panel=sales",
    tag: "عملیات روزانه",
  },
  {
    title: "مشتری و مشاوره",
    description: "ثبت مراجعه یا ادامهٔ مشاوره در صورت نیاز",
    icon: "◎",
    to: "/workspace?panel=consult",
    tag: "ارتباط با مشتری",
  },
  {
    title: "گالری محصولات",
    description: "مشاهدهٔ کاتالوگ کالاهای موجود",
    icon: "▦",
    to: "/catalog",
    tag: "کالا و انبار",
  },
];

export default function NewDashboardGalleryHome() {
  const navigate = useNavigate();
  const [openGroup, setOpenGroup] = useState<string | null>(null);

  function logout() {
    [
      "hbi_admin_access_token",
      "hbi_admin_refresh_token",
      "hbi_access_token",
      "hbi_refresh_token",
      "hbi_customer_id",
      "hbi_case_id",
      "hbi_operator_access_token",
      "hbi_po_access_token",
    ].forEach((key) => sessionStorage.removeItem(key));
    navigate("/login", { replace: true });
  }

  function toggleGroup(label: string) {
    setOpenGroup((prev) => (prev === label ? null : label));
  }

  return (
    <main className="hbi-home" dir="rtl">
      <aside className="hbi-sidebar">
        <Link className="hbi-brand" to="/" aria-label="صفحه اصلی HBI">
          <span className="hbi-brand-mark">H</span>
          <span className="hbi-brand-copy">
            <strong>HBI</strong>
            <small>مدیریت سلامت و زیبایی</small>
          </span>
        </Link>

        <div className="hbi-nav-label">منوی اصلی</div>
        <nav className="hbi-side-nav" aria-label="منوی اصلی">
          {navigation.map((item) => {
            const hasChildren = item.children.length > 0;
            const isOpen = openGroup === item.label;
            return (
              <div key={item.label} className="hbi-nav-group">
                <div className="hbi-nav-row">
                  <Link
                    className={item.current ? "hbi-nav-item is-current" : "hbi-nav-item"}
                    to={item.to}
                  >
                    <span className="hbi-nav-icon" aria-hidden="true">
                      {item.icon}
                    </span>
                    <span className="hbi-nav-copy">
                      <strong>{item.label}</strong>
                      <small>{item.detail}</small>
                    </span>
                    {item.current ? <span className="hbi-nav-indicator" aria-hidden="true" /> : null}
                  </Link>
                  {hasChildren ? (
                    <button
                      type="button"
                      className="hbi-nav-toggle"
                      aria-expanded={isOpen}
                      aria-controls={`subnav-${item.label}`}
                      aria-label={isOpen ? `بستن زیرمنوی ${item.label}` : `باز کردن زیرمنوی ${item.label}`}
                      onClick={() => toggleGroup(item.label)}
                    >
                      <span aria-hidden="true">{isOpen ? "▾" : "◂"}</span>
                    </button>
                  ) : null}
                </div>
                {hasChildren && isOpen ? (
                  <div
                    className="hbi-subnav"
                    id={`subnav-${item.label}`}
                    aria-label={`زیرمنوهای ${item.label}`}
                  >
                    {item.children.map((child) => (
                      <Link key={child.label} className="hbi-subnav-link" to={child.to}>
                        {child.label}
                      </Link>
                    ))}
                  </div>
                ) : null}
              </div>
            );
          })}
        </nav>

        <div className="hbi-sidebar-bottom">
          <div className="hbi-operator-card">
            <span className="hbi-avatar" aria-hidden="true">
              م
            </span>
            <span>
              <strong>مدیر سیستم</strong>
              <small>دسترسی عملیاتی</small>
            </span>
          </div>
          <button type="button" className="hbi-logout" onClick={logout}>
            <span aria-hidden="true">↪</span> خروج از حساب
          </button>
        </div>
      </aside>

      <div className="hbi-main">
        <header className="hbi-topbar">
          <div className="hbi-breadcrumb">
            <span>منوی اصلی</span>
            <span aria-hidden="true">/</span>
            <strong>خانه</strong>
          </div>
          <div className="hbi-topbar-status">
            <span className="hbi-status-dot" /> پنل مدیریت HBI
          </div>
        </header>

        <div className="hbi-page-wrap">
          <section className="hbi-welcome" id="dashboard">
            <div className="hbi-welcome-copy">
              <span className="hbi-eyebrow">مرکز مدیریت HBI</span>
              <h1>کار امروز را از اینجا شروع کنید.</h1>
              <p>
                منوی کناری حوزه‌های کاری را جدا نگه می‌دارد. کارهای پرتکرار روز در سه میان‌بر زیر هستند؛ بقیه از
                زیرمنوی همان حوزه باز می‌شوند.
              </p>
            </div>
            <div className="hbi-welcome-mark" aria-hidden="true">
              <span className="hbi-welcome-mark-core">H</span>
              <span className="hbi-welcome-mark-orbit orbit-one" />
              <span className="hbi-welcome-mark-orbit orbit-two" />
            </div>
          </section>

          <section className="hbi-section" aria-labelledby="quick-actions-title">
            <div className="hbi-section-heading">
              <div>
                <span className="hbi-kicker">دسترسی سریع</span>
                <h2 id="quick-actions-title">کارهای پرتکرار</h2>
                <p>سه میان‌بر روزانه — نه تکرار کامل منو.</p>
              </div>
            </div>
            <div className="hbi-action-grid">
              {quickActions.map((action, index) => (
                <Link className="hbi-action-card" to={action.to} key={action.title}>
                  <div className="hbi-action-card-top">
                    <span className="hbi-action-icon" aria-hidden="true">
                      {action.icon}
                    </span>
                    <span className="hbi-action-number">0{index + 1}</span>
                  </div>
                  <span className="hbi-action-tag">{action.tag}</span>
                  <strong className="hbi-action-title">{action.title}</strong>
                  <span className="hbi-action-description">{action.description}</span>
                  <span className="hbi-action-link">
                    ورود به بخش <span aria-hidden="true">←</span>
                  </span>
                </Link>
              ))}
            </div>
          </section>

          <section className="hbi-section hbi-flow-section" aria-labelledby="flow-title">
            <div className="hbi-section-heading">
              <div>
                <span className="hbi-kicker">نقشهٔ کار</span>
                <h2 id="flow-title">جریان اصلی فعالیت در HBI</h2>
                <p>حوزه‌ها جدا هستند؛ فقط در نقطهٔ نیاز به هم وصل می‌شوند.</p>
              </div>
            </div>
            <div className="hbi-flow-strip">
              <div className="hbi-flow-step">
                <span>۱</span>
                <strong>شناخت نیاز</strong>
                <small>مشتری و مشاوره، فقط در صورت نیاز</small>
              </div>
              <span className="hbi-flow-arrow" aria-hidden="true">
                ←
              </span>
              <div className="hbi-flow-step">
                <span>۲</span>
                <strong>بررسی محصول</strong>
                <small>کاتالوگ و موجودی</small>
              </div>
              <span className="hbi-flow-arrow" aria-hidden="true">
                ←
              </span>
              <div className="hbi-flow-step">
                <span>۳</span>
                <strong>تصمیم و اقدام</strong>
                <small>پیشنهاد یا فروش مستقیم</small>
              </div>
            </div>
            <p className="hbi-flow-note">
              فروش مستقیم همیشه از منوی «فروش» در دسترس است؛ مشاوره پیش‌نیاز ثبت فروش نیست.
            </p>
          </section>

          <footer className="hbi-home-footer">
            <span>
              <strong>HBI</strong> · پنل مدیر
            </span>
            <span>هر حوزه در منوی خودش.</span>
          </footer>
        </div>
      </div>
    </main>
  );
}
