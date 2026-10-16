{pageView === "content" && active === "home" && (
          <section className="pro-panel">
            <p className="pro-section-kicker">میز کار امروز</p>
            <h1>داشبورد HBI</h1>
            <p className="pro-lead">یک نگاه به فروش و موجودی — بعد یک اقدام سریع. عددی که از API نیاید ساخته نمی‌شود.</p>

            <div className="pro-dash-hero">
              <div className="pro-dash-hero-main">
                <h2>فروش امروز</h2>
                <p className="pro-metric">
                  {dashboardSales
                    ? `${dashboardSales.revenue_toman.toLocaleString("fa-IR")} تومان`
                    : dashboardLoading
                      ? "…"
                      : "داده نیست"}
                </p>
                <p className="pro-muted">
                  {dashboardSales
                    ? `${dashboardSales.sale_count.toLocaleString("fa-IR")} تراکنش ثبت‌شده`
                    : "پس از نوسازی یا اتصال API نمایش داده می‌شود."}
                </p>
                <Link to="/accounting?section=sales" className="pro-btn-secondary">گزارش فروش</Link>
              </div>
              <div className="pro-dash-hero-side">
                <h2>موجودی کم</h2>
                <p className="pro-metric">
                  {dashboardLowStock == null
                    ? (dashboardLoading ? "…" : "—")
                    : dashboardLowStock.length.toLocaleString("fa-IR")}
                </p>
                <p className="pro-muted">آستانه ≤ ۵ · از گزارش رسمی</p>
                <Link to="/inventory?section=low-stock" className="pro-btn-secondary">کمبود موجودی</Link>
              </div>
            </div>

            <section aria-labelledby="dashboard-actions-title">
              <h2 id="dashboard-actions-title">اقدام سریع</h2>
              <div className="pro-product-grid">
                <article className="pro-product-card pro-action-card--sale">
                  <h3>فروش مستقیم</h3>
                  <p className="pro-muted">ثبت سریع در صندوق — بدون الزام مشاوره.</p>
                  <button type="button" className="pro-btn-primary" onClick={() => { setReturnToDashboard(true); go("sales"); }}>ثبت فروش</button>
                </article>
                <article className="pro-product-card">
                  <h3>مشتریان</h3>
                  <p className="pro-muted">جست‌وجو، ایجاد پروفایل و سابقهٔ خرید.</p>
                  <div className="pro-actions">
                    <button type="button" className="pro-btn-primary" onClick={() => { setReturnToDashboard(true); go("previous"); }}>جست‌وجوی مشتری</button>
                    <button type="button" className="pro-btn-secondary" onClick={() => { setReturnToDashboard(true); go("profile"); }}>مشتری جدید</button>
                  </div>
                </article>
                <article className="pro-product-card">
                  <h3>مشاوره</h3>
                  <p className="pro-muted">ثبت مسئله، بررسی نیاز و مشاهده پیشنهادهای واجد شرایط.</p>
                  <button type="button" className="pro-btn-primary" onClick={() => { setReturnToDashboard(true); go("consult"); }}>شروع مشاوره</button>
                </article>
              </div>
            </section>

            <section aria-labelledby="dashboard-summary-title">
              <div className="pro-section-head">
                <h2 id="dashboard-summary-title">خلاصهٔ عملیات</h2>
                <button type="button" className="pro-btn-secondary" onClick={() => void refreshDashboard()} disabled={dashboardLoading}>
                  {dashboardLoading ? "در حال دریافت…" : "نوسازی داده‌ها"}
                </button>
              </div>
              {dashboardError && <p className="pro-error" role="status">{dashboardError}</p>}
              <div className="pro-product-grid">
