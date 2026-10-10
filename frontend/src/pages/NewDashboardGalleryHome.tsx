import { Link } from "react-router-dom";
import "../styles/dashboard-gallery.css";

const galleryLines = [
  { number: "01", title: "پوست", subtitle: "مراقبت و سلامت پوست", icon: "✳", tone: "rose" },
  { number: "02", title: "مو", subtitle: "مراقبت مو و پوست سر", icon: "〰", tone: "violet" },
  { number: "03", title: "آرایشی", subtitle: "زیبایی و آرایش", icon: "✦", tone: "peach" },
  { number: "04", title: "ادکلن و عطر", subtitle: "رایحه‌ها و عطرها", icon: "❋", tone: "gold" },
  { number: "05", title: "ابزار", subtitle: "ابزار و تجهیزات مراقبت", icon: "⌁", tone: "blue" },
  { number: "06", title: "متفرقه", subtitle: "سایر محصولات", icon: "＋", tone: "green" },
];

const workAreas = [
  { title: "مشتری و مشاوره", detail: "پرونده، نیاز و پیشنهاد محصول", icon: "◎", to: "/workspace", tone: "violet" },
  { title: "معرفی و بررسی محصول", detail: "ورود محصول و کنترل اطلاعات", icon: "✳", to: "/workspace", tone: "rose" },
  { title: "فروش و برگشت", detail: "ثبت فروش و پیگیری برگشت کالا", icon: "↗", to: "/workspace", tone: "green" },
  { title: "خرید و موجودی", detail: "ثبت خرید و گردش موجودی", icon: "▤", to: "/purchase", tone: "gold" },
  { title: "مالی و حسابداری", detail: "ورود به بخش مالی موجود", icon: "◫", to: "/accounting", tone: "blue" },
  { title: "کاتالوگ محصولات", detail: "مشاهده فهرست محصولات ثبت‌شده", icon: "▦", to: "/catalog", tone: "peach" },
];

export default function NewDashboardGalleryHome() {
  return (
    <main className="hbi-home" dir="rtl">
      <header className="hbi-topbar">
        <Link className="hbi-brand" to="/" aria-label="صفحه اصلی HBI">
          <span className="hbi-brand-mark">H</span>
          <span><strong>HBI</strong><small>هوشمندی سلامت و زیبایی</small></span>
        </Link>
        <nav className="hbi-topnav" aria-label="ناوبری اصلی">
          <a className="is-current" href="#dashboard">داشبورد</a>
          <a href="#gallery">گالری محصولات</a>
          <a href="#workspaces">حوزه‌های کاری</a>
        </nav>
        <div className="hbi-operator"><span className="hbi-online-dot" /> فضای کاری مدیر <span className="hbi-avatar">و</span></div>
      </header>

      <div className="hbi-page-wrap">
        <section className="hbi-welcome" id="dashboard">
          <div className="hbi-welcome-copy">
            <span className="hbi-eyebrow"><span /> مرکز مدیریت HBI</span>
            <h1>کسب‌وکار شما، <em>یک‌جا و روشن.</em></h1>
            <p>از گالری محصولات تا مشاوره، فروش و حسابداری؛ مسیرهای اصلی کار روزانه در یک صفحه.</p>
            <div className="hbi-welcome-actions">
              <a className="hbi-primary-btn" href="#gallery">ورود به گالری <span>←</span></a>
              <Link className="hbi-secondary-btn" to="/workspace">شروع کار روزانه</Link>
            </div>
          </div>
          <div className="hbi-orbit-art" aria-hidden="true">
            <div className="hbi-orbit orbit-one" /><div className="hbi-orbit orbit-two" />
            <div className="hbi-orbit-core"><span>HBI</span><small>CARE · BEAUTY · INTELLIGENCE</small></div>
            <span className="hbi-orbit-chip chip-one">محصول</span>
            <span className="hbi-orbit-chip chip-two">دانش</span>
            <span className="hbi-orbit-chip chip-three">تصمیم</span>
          </div>
        </section>

        <section className="hbi-section" id="gallery">
          <div className="hbi-section-heading">
            <div><span className="hbi-kicker">PRODUCT GALLERY</span><h2>گالری محصولات</h2><p>شش حوزهٔ مستقل برای مرتب‌کردن سبد محصولات HBI</p></div>
            <Link className="hbi-text-link" to="/catalog">فهرست محصولات ثبت‌شده <span>←</span></Link>
          </div>
          <div className="hbi-gallery-grid">
            {galleryLines.map((line) => (
              <Link className={`hbi-gallery-card tone-${line.tone}`} to="/catalog" key={line.number}>
                <span className="hbi-card-number">{line.number}</span>
                <span className="hbi-gallery-icon">{line.icon}</span>
                <span className="hbi-gallery-title">{line.title}</span>
                <span className="hbi-gallery-subtitle">{line.subtitle}</span>
                <span className="hbi-card-arrow" aria-hidden="true">↙</span>
              </Link>
            ))}
          </div>
          <p className="hbi-honesty-note"><span>i</span> ورود هر حوزه به کاتالوگ فعلی انجام می‌شود؛ فیلتر اختصاصی هر حوزه تا زمان پیاده‌سازی، فعال فرض نشده است.</p>
        </section>

        <section className="hbi-section hbi-work-section" id="workspaces">
          <div className="hbi-section-heading">
            <div><span className="hbi-kicker">DAILY WORKSPACE</span><h2>مسیرهای اصلی کار</h2><p>قابلیت‌های موجود از اینجا در دسترس‌اند؛ چیزی صرفاً برای پرکردن صفحه جعل نشده است.</p></div>
            <span className="hbi-live-label"><span /> فضای کاری عملیاتی</span>
          </div>
          <div className="hbi-work-grid">
            {workAreas.map((area) => (
              <Link className="hbi-work-card" to={area.to} key={area.title}>
                <span className={`hbi-work-icon tone-${area.tone}`}>{area.icon}</span>
                <span className="hbi-work-copy"><strong>{area.title}</strong><small>{area.detail}</small></span>
                <span className="hbi-work-arrow">←</span>
              </Link>
            ))}
          </div>
        </section>

        <footer className="hbi-home-footer">
          <span><strong>HBI</strong> · مرکز تصمیم‌یار سلامت و زیبایی</span>
          <span>واقعیت موجود، مبنای تصمیم است.</span>
        </footer>
      </div>
    </main>
  );
}
