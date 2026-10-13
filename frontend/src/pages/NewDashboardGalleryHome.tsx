import { Link } from "react-router-dom";
import "../styles/dashboard-gallery.css";

const quickActions = [
  {
    title: "ثبت فروش",
    description: "فروش ساده؛ بدون مشاوره",
    icon: "↗",
    to: "/sales",
    tag: "عملیات روزانه",
  },
  {
    title: "مشتری و مشاوره",
    description: "جست‌وجو یا شروع مشاوره",
    icon: "◎",
    to: "/workspace?panel=previous",
    tag: "ارتباط با مشتری",
  },
  {
    title: "کاتالوگ کالا",
    description: "فهرست کالاهای ثبت‌شده",
    icon: "▦",
    to: "/catalog",
    tag: "کالا و انبار",
  },
];

export default function NewDashboardGalleryHome() {
  return (
    <>
      <section className="hbi-welcome" id="dashboard">
        <div className="hbi-welcome-copy">
          <span className="hbi-eyebrow">مرکز مدیریت HBI</span>
          <h1>کار امروز را از اینجا شروع کنید.</h1>
          <p>
            منوی کناری حوزه‌های کاری را جدا نگه می‌دارد. فروش مستقیم از مسیر «فروش» انجام می‌شود و به مشاوره وابسته
            نیست.
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
            <strong>ثبت فروش</strong>
            <small>صفحهٔ سادهٔ فروش مستقیم</small>
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
    </>
  );
}
