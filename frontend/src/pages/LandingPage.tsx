import { Link } from "react-router-dom";
import "../styles/landing.css";

export default function LandingPage() {
  return (
    <div className="landing-page" dir="rtl">
      <header className="landing-header">
        <Link className="landing-brand" to="/">گالری مقصودی</Link>
        <nav aria-label="منوی اصلی">
          <a href="#products">محصولات</a>
          <a href="#need">نیاز شما</a>
          <a href="#consultation">مشاوره</a>
        </nav>
        <Link className="landing-login" to="/login">ورود به HBI</Link>
      </header>

      <main>
        <section className="landing-hero">
          <div className="landing-hero-copy">
            <span className="landing-eyebrow">HBI · هوش زیبایی و مراقبت</span>
            <h1>انتخاب درست،<br />از شناخت درست<br />شروع می‌شود.</h1>
            <p>ما فقط محصول نشان نمی‌دهیم؛ کمک می‌کنیم آگاهانه‌تر انتخاب کنید.</p>
            <div className="landing-actions">
              <Link className="landing-primary" to="/login">ورود به محیط HBI</Link>
              <a className="landing-secondary" href="#approach">آشنایی با روش کار</a>
            </div>
          </div>
          <div className="landing-hero-art" aria-hidden="true">
            <div className="landing-orbit orbit-one" />
            <div className="landing-orbit orbit-two" />
            <div className="landing-monogram">HBI</div>
            <span className="landing-art-caption">آگاهی · شواهد · انتخاب</span>
          </div>
        </section>

        <section className="landing-trust" aria-label="اصول HBI">
          <div><b>✓</b><span>اطلاعات قابل بررسی</span></div>
          <div><b>✓</b><span>شفافیت در انتخاب</span></div>
          <div><b>✓</b><span>پرهیز از حدس و دادهٔ ساختگی</span></div>
        </section>

        <section className="landing-section" id="need">
          <span className="landing-eyebrow">از نیاز شروع می‌کنیم</span>
          <h2>امروز بیشتر دنبال چه چیزی هستید؟</h2>
          <p>مراقبت پوست، مراقبت مو یا راهنمای انتخاب؛ نیاز واقعی نقطهٔ شروع بررسی است.</p>
          <div className="landing-pills">
            <span>مراقبت پوست</span><span>مراقبت مو</span><span>مراقبت پوست سر</span><span>راهنمای انتخاب</span>
          </div>
        </section>

        <section className="landing-section landing-approach" id="approach">
          <span className="landing-eyebrow">روش کار</span>
          <h2>چگونه HBI کمک می‌کند؟</h2>
          <div className="landing-steps">
            <article><strong>۰۱</strong><h3>شناخت نیاز</h3><p>اطلاعات مرتبط با نیاز شما مشخص می‌شود.</p></article>
            <article><strong>۰۲</strong><h3>بررسی شواهد</h3><p>اطلاعات موجود بررسی می‌شود و موارد نامعلوم پنهان نمی‌ماند.</p></article>
            <article><strong>۰۳</strong><h3>انتخاب مستند</h3><p>گزینه‌ها با توجه به شواهد و محدودیت‌های موجود ارزیابی می‌شوند.</p></article>
          </div>
        </section>

        <section className="landing-transparency" id="products">
          <div><span className="landing-eyebrow">اصل بنیادین HBI</span><h2>اطلاعات موجود را از فرضیات جدا می‌کنیم.</h2>
          <p>وقتی شواهد کافی نباشد، سیستم نباید با حدس‌زدن جای خالی اطلاعات را پر کند.</p></div>
          <Link className="landing-primary" to="/login">ورود به محیط HBI</Link>
        </section>

        <section className="landing-section landing-consultation" id="consultation">
          <h2>فناوری در خدمت انتخاب آگاهانه</h2>
          <p>HBI ابزار پشتیبان تصمیم‌گیری است؛ اطلاعات، شواهد و بررسی انسانی همچنان اهمیت دارند.</p>
        </section>
      </main>
      <footer className="landing-footer">گالری مقصودی · HBI · ۲۰۲۶</footer>
    </div>
  );
}
