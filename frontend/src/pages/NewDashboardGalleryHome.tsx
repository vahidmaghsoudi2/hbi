import { Link, useNavigate } from "react-router-dom";
import "../styles/dashboard-gallery.css";
import "../styles/homepage-navigation.css";

const navigation = [
  { label: "خانه و داشبورد", detail: "نمای کلی عملیات", icon: "⌂", to: "/", current: true, children: [] },
  {
    label: "کالا و انبار", detail: "کاتالوگ، پرونده و موجودی", icon: "▦", to: "/catalog",
    children: [
      { label: "کاتالوگ کالاها", to: "/catalog" },
      { label: "بررسی پرونده کالا", to: "/workspace?panel=review" },
      { label: "ثبت و ویرایش کالا", to: "/workspace?panel=intake" },
      { label: "خرید و ورود موجودی", to: "/purchase" },
    ],
  },
  {
    label: "مشتری و مشاوره", detail: "پرونده، مراجعه و نتایج", icon: "◎", to: "/workspace?panel=consult",
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
  { title: "ثبت فروش", description: "ثبت فروش مستقیم، بدون نیاز به مشاوره قبلی", icon: "↗", to: "/workspace?panel=sales", tag: "عملیات روزانه" },
  { title: "مشتری و مشاوره", description: "جست‌وجوی مشتری یا ثبت مراجعه و نیاز", icon: "◎", to: "/workspace?panel=consult", tag: "ارتباط با مشتری" },
  { title: "گالری محصولات", description: "مشاهده کاتالوگ محصولات موجود", icon: "▦", to: "/catalog", tag: "کالا و انبار" },
  { title: "خرید و موجودی", description: "ثبت خرید و پیگیری گردش موجودی", icon: "▤", to: "/purchase", tag: "تأمین کالا" },
];

const moreActions = [
  { title: "بررسی پرونده کالا", description: "بازبینی پرونده‌های موجود", icon: "▧", to: "/workspace?panel=review" },
  { title: "نتایج مشاوره", description: "مشاهده نتایج ثبت‌شده", icon: "⌕", to: "/workspace?panel=results" },
  { title: "سوابق مراجعه", description: "دسترسی به سوابق قبلی", icon: "◷", to: "/workspace?panel=previous" },
  { title: "پرونده مشتری", description: "مشاهده اطلاعات پرونده مشتری", icon: "♙", to: "/workspace?panel=profile" },
];

export default function NewDashboardGalleryHome() {
  const navigate = useNavigate();

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

  return (
    <main className="hbi-home" dir="rtl">
      <aside className="hbi-sidebar">
        <Link className="hbi-brand" to="/" aria-label="صفحه اصلی HBI">
          <span className="hbi-brand-mark">H</span>
          <span className="hbi-brand-copy"><strong>HBI</strong><small>مدیریت سلامت و زیبایی</small></span>
        </Link>

        <div className="hbi-nav-label">فضای کاری</div>
        <nav className="hbi-side-nav" aria-label="منوی اصلی">
          {navigation.map((item) => (
            <div key={item.label} className="hbi-nav-group">
              <Link className={item.current ? "hbi-nav-item is-current" : "hbi-nav-item"} to={item.to}>
                <span className="hbi-nav-icon" aria-hidden="true">{item.icon}</span>
                <span className="hbi-nav-copy"><strong>{item.label}</strong><small>{item.detail}</small></span>
                {item.current ? <span className="hbi-nav-indicator" aria-hidden="true" /> : null}
              </Link>
              {item.children.length > 0 ? (
                <div className="hbi-subnav" aria-label={`زیرمنوهای ${item.label}`}>
                  {item.children.map((child) => (
                    <Link key={child.label} className="hbi-subnav-link" to={child.to}>
                      {child.label}
                    </Link>
                  ))}
                </div>
              ) : null}
            </div>
          ))}
        </nav>

        <div className="hbi-sidebar-bottom">
          <div className="hbi-operator-card">
            <span className="hbi-avatar" aria-hidden="true">م</span>
            <span><strong>مدیر سیستم</strong><small>دسترسی عملیاتی</small></span>
          </div>
          <button type="button" className="hbi-logout" onClick={logout}><span aria-hidden="true">↪</span> خروج از حساب</button>
        </div>
      </aside>

      <div className="hbi-main">
        <header className="hbi-topbar">
          <div className="hbi-breadcrumb"><span>فضای کاری</span><span className="hbi-breadcrumb-separator">/</span><strong>خانه</strong></div>
          <div className="hbi-topbar-note"><span className="hbi-status-dot" /> پنل مدیریت HBI</div>
        </header>

        <div className="hbi-page-wrap">
          <section className="hbi-welcome" id="dashboard">
            <div className="hbi-welcome-copy">
              <span className="hbi-eyebrow">مرکز مدیریت HBI</span>
              <h1>کار امروز را از اینجا شروع کنید.</h1>
              <p>دسترسی روشن به کارهای روزانه؛ هر بخش در جای خودش، بدون شلوغی اضافه.</p>
            </div>
            <div className="hbi-welcome-mark" aria-hidden="true">
              <span className="hbi-welcome-mark-core">H</span>
              <span className="hbi-welcome-mark-orbit orbit-one" />
              <span className="hbi-welcome-mark-orbit orbit-two" />
            </div>
          </section>

          <section className="hbi-section" aria-labelledby="quick-actions-title">
            <div className="hbi-section-heading">
              <div><span className="hbi-kicker">دسترسی سریع</span><h2 id="quick-actions-title">کارهای پرتکرار</h2><p>عملیات اصلی را مستقیم باز کنید.</p></div>
            </div>
            <div className="hbi-action-grid">
              {quickActions.map((action, index) => (
                <Link className="hbi-action-card" to={action.to} key={action.title}>
                  <div className="hbi-action-card-top">
                    <span className="hbi-action-icon" aria-hidden="true">{action.icon}</span>
                    <span className="hbi-action-number">0{index + 1}</span>
                  </div>
                  <span className="hbi-action-tag">{action.tag}</span>
                  <strong className="hbi-action-title">{action.title}</strong>
                  <span className="hbi-action-description">{action.description}</span>
                  <span className="hbi-action-link">ورود به بخش <span aria-hidden="true">←</span></span>
                </Link>
              ))}
            </div>
          </section>

          <section className="hbi-section hbi-more-section" aria-labelledby="more-actions-title">
            <div className="hbi-section-heading">
              <div><span className="hbi-kicker">دسترسی‌های مستقیم</span><h2 id="more-actions-title">سایر بخش‌های کاری</h2><p>برای رسیدن به ابزارهای موجود لازم نیست از چند منو عبور کنید.</p></div>
            </div>
            <div className="hbi-more-grid">
              {moreActions.map((action) => (
                <Link className="hbi-more-card" to={action.to} key={action.title}>
                  <span className="hbi-more-icon" aria-hidden="true">{action.icon}</span>
                  <span className="hbi-more-copy"><strong>{action.title}</strong><small>{action.description}</small></span>
                  <span className="hbi-more-arrow" aria-hidden="true">←</span>
                </Link>
              ))}
            </div>
          </section>

          <section className="hbi-section hbi-flow-section" aria-labelledby="flow-title">
            <div className="hbi-section-heading">
              <div><span className="hbi-kicker">نقشهٔ کار</span><h2 id="flow-title">جریان اصلی فعالیت در HBI</h2><p>مسیرها از هم جدا هستند و فقط در نقاط لازم به هم متصل می‌شوند.</p></div>
            </div>
            <div className="hbi-flow-strip">
              <div className="hbi-flow-step"><span>۱</span><strong>شناخت نیاز</strong><small>مشتری و مشاوره، در صورت نیاز</small></div>
              <span className="hbi-flow-arrow" aria-hidden="true">←</span>
              <div className="hbi-flow-step"><span>۲</span><strong>بررسی محصول</strong><small>بر پایهٔ شواهد و موجودی</small></div>
              <span className="hbi-flow-arrow" aria-hidden="true">←</span>
              <div className="hbi-flow-step"><span>۳</span><strong>تصمیم و اقدام</strong><small>پیشنهاد یا فروش مستقل</small></div>
            </div>
            <p className="hbi-flow-note">فروش مستقیم همیشه از منوی «فروش» در دسترس است؛ مشاوره پیش‌نیاز ثبت فروش نیست.</p>
          </section>

          <footer className="hbi-home-footer">
            <span><strong>HBI</strong> · فضای کاری مدیر</span>
            <span>هر کار در جای خودش.</span>
          </footer>
        </div>
      </div>
    </main>
  );
}
