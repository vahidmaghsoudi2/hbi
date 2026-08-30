import { Link } from "react-router-dom";

export default function NewHomePage() {
  return (
    <section>
      <h1>HBI — داشبورد عملیاتی</h1>
      <p className="lead">مدیریت محصولات، مشتریان، و تولید توصیه‌های هوشمند.</p>
      <div className="card-grid">
        <div className="card">
          <h2>کاتالوگ محصولات</h2>
          <p>مشاهده محصولات تأییدشده (Legacy)</p>
          <Link className="btn" to="/catalog">مشاهده کاتالوگ</Link>
        </div>
        <div className="card">
          <h2>مسیر Pilot</h2>
          <p>دریافت توکن آزمایشی و ایجاد Case</p>
          <Link className="btn" to="/pilot">شروع Pilot</Link>
        </div>
        <div className="card">
          <h2>تولید Recommendation</h2>
          <p>تولید توصیه با Case ID و پروفایل مشتری</p>
          <Link className="btn" to="/recommendation">تولید توصیه</Link>
        </div>
      </div>
    </section>
  );
}
