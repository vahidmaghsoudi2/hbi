import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listProducts } from "../api/client";
import type { ProductDTO } from "../types/api";
import "../styles/landing.css";

export default function LandingPage() {
  const [products, setProducts] = useState<ProductDTO[]>([]);
  const [productsLoading, setProductsLoading] = useState(true);
  const [productsError, setProductsError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    void listProducts()
      .then((items) => {
        if (!cancelled) setProducts(Array.isArray(items) ? items : []);
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          setProductsError(error instanceof Error ? error.message : "دریافت فهرست محصولات ناموفق بود.");
        }
      })
      .finally(() => {
        if (!cancelled) setProductsLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="landing-page" dir="rtl">
      <header className="landing-header">
        <Link className="landing-brand" to="/">گالری مقصودی</Link>
        <nav aria-label="منوی اصلی">
          <a href="#products">محصولات</a>
          <a href="#need">حوزه‌های مراقبت</a>
          <a href="#consultation">درباره مشاوره</a>
        </nav>
        <Link className="landing-login" to="/login">ورود مدیر HBI</Link>
      </header>

      <main>
        <section className="landing-hero">
          <div className="landing-hero-copy">
            <span className="landing-eyebrow">HBI · هوش زیبایی و مراقبت</span>
            <h1>انتخاب درست،<br />از شناخت درست<br />شروع می‌شود.</h1>
            <p>ما فقط محصول نشان نمی‌دهیم؛ کمک می‌کنیم آگاهانه‌تر انتخاب کنید.</p>
            <div className="landing-actions">
              <Link className="landing-primary" to="/login">ورود مدیر به HBI</Link>
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
          <h2>حوزه‌هایی که HBI بررسی می‌کند</h2>
          <p>این دسته‌ها برای معرفی حوزه‌های کاری HBI هستند و در این صفحه انتخاب تعاملی یا ثبت نیاز انجام نمی‌دهند.</p>
          <div className="landing-pills" aria-label="دسته‌های مراقبت">
            <span>مراقبت پوست</span><span>مراقبت مو</span><span>مراقبت پوست سر</span><span>راهنمای انتخاب</span>
          </div>
          <p className="landing-note">ثبت مشتری، نیاز و مشاوره از این بخش انجام نمی‌شود؛ این عملیات فقط از مسیر عملیاتی مجاز HBI در دسترس است.</p>
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

        <section className="landing-section landing-products" id="products">
          <span className="landing-eyebrow">کاتالوگ عمومی</span>
          <h2>محصولات قابل نمایش</h2>
          <p>فهرست از API عمومی HBI دریافت می‌شود؛ این بخش اطلاعات ساختگی یا نمونه‌ای تولید نمی‌کند.</p>
          {productsLoading && <p role="status" className="landing-product-state">در حال بارگذاری محصولات…</p>}
          {!productsLoading && productsError && (
            <p role="alert" className="landing-product-state">دریافت محصولات ممکن نشد. اتصال سرویس در این محیط باید بررسی شود.</p>
          )}
          {!productsLoading && !productsError && products.length === 0 && (
            <p className="landing-product-state">در حال حاضر محصولی برای نمایش از API دریافت نشد.</p>
          )}
          {!productsLoading && !productsError && products.length > 0 && (
            <div className="landing-product-grid">
              {products.map((product) => (
                <article className="landing-product-card" key={product.product_id}>
                  <h3>{product.product_name || "نام ثبت نشده"}</h3>
                  <p>{product.brand || "برند ثبت نشده"}</p>
                  {product.variant && <p>گونه: {product.variant}</p>}
                  {product.size_value != null && product.size_unit && <p>اندازه: {product.size_value} {product.size_unit}</p>}
                </article>
              ))}
            </div>
          )}
        </section>

        <section className="landing-transparency">
          <div><span className="landing-eyebrow">اصل بنیادین HBI</span><h2>اطلاعات موجود را از فرضیات جدا می‌کنیم.</h2>
          <p>وقتی شواهد کافی نباشد، سیستم نباید با حدس‌زدن جای خالی اطلاعات را پر کند.</p></div>
        </section>

        <section className="landing-section landing-consultation" id="consultation">
          <h2>مشاوره در HBI</h2>
          <p>این بخش معرفی است و پروندهٔ مشاوره ایجاد نمی‌کند. ثبت و پیگیری مشاوره در محیط عملیاتی مجاز HBI انجام می‌شود.</p>
        </section>
      </main>
      <footer className="landing-footer">گالری مقصودی · HBI · ۲۰۲۶</footer>
    </div>
  );
}
