import { Link } from "react-router-dom";

/** Temporary stub. DO NOT MERGE. Full homepage restored via patch. */
export default function NewHomePage() {
  return (
    <div className="home-root pro-home">
      <header className="pro-header">
        <div className="pro-header-inner">
          <div className="pro-brand">
            <span className="pro-brand-mark">HBI</span>
            <div>
              <div className="pro-brand-title">گالری مقصودی</div>
              <div className="pro-brand-sub">هوش زیبایی و مراقبت · فضای کاری مدیر</div>
            </div>
          </div>
        </div>
      </header>
      <main className="pro-main">
        <section className="pro-panel">
          <h1>صفحه اول (داشبورد)</h1>
          <p className="pro-lead">در حال اعمال نهایی حذف دکمه خروج و چیدمان داشبورد طبق دیاگرام.</p>
          <Link className="pro-btn-primary" to="/">تازه‌سازی</Link>
        </section>
      </main>
    </div>
  );
}
