import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import './styles/home.css';

// ============================================================
// COMPONENTS
// ============================================================

function Header() {
  return (
    <header className="header">
      <div className="container header-inner">
        <div className="brand">گالری مقصودی</div>
        <nav className="nav">
          <a href="#products">محصولات</a>
          <a href="#need">نیاز شما</a>
          <a href="#consultation">مشاوره</a>
        </nav>
        <button className="cta-primary">شروع از نیاز من</button>
      </div>
    </header>
  );
}

function Hero() {
  return (
    <section className="hero">
      <div className="container hero-inner">
        <h1>
          انتخاب درست،<br />
          از شناخت درست<br />
          شروع می‌شود.
        </h1>
        <p className="hero-subtitle">
          ما فقط محصول نشان نمی‌دهیم.<br />
          کمک می‌کنیم آگاهانه‌تر انتخاب کنید.
        </p>
        <div className="hero-actions">
          <button className="cta-hero">شروع از نیاز من</button>
          <button className="cta-hero-secondary">محصولات</button>
        </div>
      </div>
    </section>
  );
}

function TrustStrip() {
  return (
    <section className="trust">
      <div className="container trust-inner">
        <div className="trust-item">
          <span className="trust-icon">✓</span>
          <span>اطلاعات قابل بررسی</span>
        </div>
        <div className="trust-item">
          <span className="trust-icon">✓</span>
          <span>شفافیت در انتخاب</span>
        </div>
        <div className="trust-item">
          <span className="trust-icon">✓</span>
          <span>پیشنهاد مبتنی بر اطلاعات</span>
        </div>
      </div>
    </section>
  );
}

function NeedSelection() {
  return (
    <section className="need" id="need">
      <div className="container need-inner">
        <h2>امروز بیشتر دنبال چه چیزی هستید؟</h2>
        <div className="need-options">
          <button className="need-btn">مراقبت پوست</button>
          <button className="need-btn">مراقبت مو</button>
          <button className="need-btn">مراقبت پوست سر</button>
          <button className="need-btn">راهنمای انتخاب</button>
        </div>
      </div>
    </section>
  );
}

function HBIApproach() {
  return (
    <section className="approach">
      <div className="container approach-inner">
        <h2>چگونه HBI به شما کمک می‌کند؟</h2>
        <div className="approach-steps">
          <div className="step">
            <span className="step-num">۰۱</span>
            <h3>نیاز شما</h3>
            <p>با چند سؤال ساده، نیاز واقعی شما را شناسایی می‌کنیم.</p>
          </div>
          <div className="step">
            <span className="step-num">۰۲</span>
            <h3>بررسی اطلاعات</h3>
            <p>محصولات را بر اساس شواهد علمی بررسی می‌کنیم.</p>
          </div>
          <div className="step">
            <span className="step-num">۰۳</span>
            <h3>پیشنهاد</h3>
            <p>بهترین گزینه‌ها را با دلیل به شما نشان می‌دهیم.</p>
          </div>
        </div>
      </div>
    </section>
  );
}

function ProductGrid({ products, loading, error }) {
  if (loading) return <div className="product-state">در حال بارگذاری محصولات...</div>;
  if (error) return <div className="product-state">خطا در دریافت محصولات. لطفاً بعداً تلاش کنید.</div>;
  if (!products || products.length === 0) return <div className="product-state">هنوز محصول قابل نمایش وجود ندارد.</div>;

  return (
    <div className="product-grid">
      {products.map((p, i) => (
        <div key={i} className="product-card">
          <h4>{p.product_name || 'نامشخص'}</h4>
          <p className="product-brand">{p.brand || 'برند نامشخص'}</p>
          <p className="product-status">وضعیت: {p.identity_status || 'نامشخص'}</p>
          <a href="http://127.0.0.1:8000/docs" target="_blank" className="product-link">
            مشاهده در API
          </a>
        </div>
      ))}
    </div>
  );
}

function ProductsSection({ products, loading, error }) {
  return (
    <section className="products" id="products">
      <div className="container products-inner">
        <h2>محصولات شاخص</h2>
        <ProductGrid products={products} loading={loading} error={error} />
      </div>
    </section>
  );
}

function Transparency() {
  return (
    <section className="transparency">
      <div className="container transparency-inner">
        <h2>قبل از اینکه انتخاب کنید</h2>
        <p>
          ما در HBI اطلاعات موجود را از فرضیات جدا می‌کنیم.
          هر پیشنهاد بر اساس شواهد قابل بررسی است.
          هیچ داده جعلی، هیچ تشخیص بی‌اساس.
        </p>
      </div>
    </section>
  );
}

function HumanConsultation() {
  return (
    <section className="consultation" id="consultation">
      <div className="container consultation-inner">
        <h2>مشاوره انسانی</h2>
        <p>
          فناوری قرار نیست جای مشاوره انسانی را بگیرد.
          ما در کنار شما هستیم تا بهترین انتخاب را داشته باشید.
        </p>
        <button className="cta-consult">درخواست مشاوره</button>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="footer">
      <div className="container footer-inner">
        <p>© ۲۰۲۶ گالری مقصودی و همکاران</p>
      </div>
    </footer>
  );
}

// ============================================================
// MAIN APP
// ============================================================

function App() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';
    fetch(`${apiBase}/products/`)
      .then(async (res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        setProducts(Array.isArray(data) ? data : []);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <div className="app">
      <Header />
      <Hero />
      <TrustStrip />
      <NeedSelection />
      <HBIApproach />
      <ProductsSection products={products} loading={loading} error={error} />
      <Transparency />
      <HumanConsultation />
      <Footer />
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
