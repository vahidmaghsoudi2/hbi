{pageView === "content" && active === "sales" && (
          <section className="pro-panel" id="sales">
            <p className="pro-section-kicker">صندوق فروش</p>
            <h1>ثبت فروش</h1>
            <p className="pro-lead">کالا و مبلغ در مرکز توجه است. طرف‌حساب اختیاری است — فروش حضوری بدون مشتری مجاز است.</p>
            <form className="pro-form pro-desk" onSubmit={onSaleSubmit}>
                <div className="pro-desk-hero" aria-live="polite">
                  <div>
                    <p className="pro-desk-hero-label">مبلغ این فاکتور</p>
                    <p className="pro-desk-total">
                      {salePrice == null ? "—" : (saleQty * salePrice).toLocaleString("fa-IR")}
                      <span style={{ fontSize: "0.45em", fontWeight: 650, marginRight: "0.35rem", color: "var(--muted)" }}> تومان</span>
                    </p>
                    <p className="pro-desk-meta">
                      موجودی قابل فروش: {!saleProductId ? "پس از انتخاب محصول" : saleStock == null ? "…" : saleStock.toLocaleString("fa-IR")}
                      {totalSales != null ? ` · جمع نشست: ${totalSales.toLocaleString("fa-IR")}` : ""}
                    </p>
                  </div>
                  <button type="submit" className="pro-btn-primary pro-desk-submit" disabled={saleBusy}>
                    {saleBusy ? "در حال ثبت…" : "ثبت فروش"}
                  </button>
                </div>

                <fieldset className="pro-fieldset">
                  <legend>اقلام فاکتور</legend>
                  <label className="pro-label" htmlFor="sale-product">محصول</label>
                  {saleProductsError ? <p className="pro-error" role="status">{saleProductsError}</p> : null}
                  <select id="sale-product" className="pro-input" value={saleProductId} onChange={(e) => {
                      setSaleProductId(e.target.value);
                    }}>
                    <option value="">— انتخاب از کاتالوگ —</option>
                    {sellableProducts.map((p) => (
                      <option key={p.product_id} value={p.product_id}>
                        {p.product_name} ({p.brand})
                      </option>
                    ))}
                  </select>
                  <div className="pro-actions">
                    <button type="button" className="pro-btn-secondary" onClick={() => void loadSellableProducts()} disabled={saleProductsLoading}>
                      {saleProductsLoading ? "در حال بارگذاری کاتالوگ…" : "نوسازی کاتالوگ"}
                    </button>
                  </div>
                  {saleProductsLoading ? <p className="pro-muted" role="status">در حال دریافت کاتالوگ فروش…</p> : null}
                  {!saleProductsLoading && sellableProducts.length === 0 && !saleProductsError ? (
                    <p className="pro-muted" role="status">هنوز محصول قابل انتخابی در کاتالوگ فروش موجود نیست.</p>
                  ) : null}
                  <div className="pro-grid-2">
                    <div>
                      <label className="pro-label" htmlFor="sale-qty">تعداد</label>
                      <input id="sale-qty" className="pro-input" type="number" min={1} value={saleQty} onChange={(e) => setSaleQty(Number(e.target.value) || 1)} />
                    </div>
                    <div>
                      <span className="pro-label">قیمت واحد</span>
                      <p className="pro-input" aria-live="polite">
                        {!saleProductId ? "پس از انتخاب محصول" : salePrice == null ? "در حال دریافت…" : `${salePrice.toLocaleString("fa-IR")} تومان`}
                      </p>
                    </div>
                  </div>
                </fieldset>

                <div className="pro-party-strip">
                  <p className="pro-label" style={{ marginBottom: "0.5rem" }}>طرف‌حساب <span className="pro-muted">(اختیاری)</span></p>
                  {saleCustomerId ? (
                    <div className="pro-party-connected">
                      <span>متصل به <strong>{saleCustomerLabel}</strong></span>
                      <span className="pro-muted">{saleCustomerId}</span>
                      <button
                        type="button"
                        className="pro-btn-secondary"
                        onClick={() => { setSaleCustomerId(null); setSaleCustomerLabel(null); }}
                      >
                        بدون طرف‌حساب
                      </button>
                    </div>
                  ) : (
                    <>
                      <p className="pro-muted" style={{ marginTop: 0 }}>پیش‌فرض: فروش حضوری. موبایل اینجا نیست — هویت در بخش مشتریان است.</p>
                      <label className="pro-label" htmlFor="sale-customer-search">جست‌وجوی طرف‌حساب با نام خانوادگی</label>
                      <input
                        id="sale-customer-search"
                        className="pro-input"
                        value={saleCustomerSearch}
                        onChange={(e) => setSaleCustomerSearch(e.target.value)}
                        placeholder="نام خانوادگی…"
                        autoComplete="off"
                      />
                      <div className="pro-actions">
                        <button type="button" className="pro-btn-secondary" onClick={() => void searchSaleCustomers()} disabled={customerSearchBusy}>
                          {customerSearchBusy ? "در حال جست‌وجو…" : "یافتن طرف‌حساب"}
                        </button>
                      </div>
                      {customerSearchResults.map((customer) => (
                        <button key={customer.customer_id} type="button" className="pro-btn-secondary" onClick={() => chooseSaleCustomer(customer)}>
                          {customer.family_name ?? "بدون نام خانوادگی"} · {customer.customer_id}
                        </button>
                      ))}
                    </>
                  )}
                </div>
            </form>
            {lastSale && (
              <div className="pro-last-sale" style={{ marginTop: "1rem" }} role="status">
                <div className="pro-last-sale-mark" aria-hidden="true">✓</div>
                <div>
                  <strong>آخرین فروش ثبت شد</strong>
                  <p className="pro-muted" style={{ margin: "0.2rem 0 0" }}>
                    {String(lastSale.sale_id ?? "—")} · {Number(lastSale.total_amount_toman ?? 0).toLocaleString("fa-IR")} تومان
                  </p>
                </div>
              </div>
            )}
          </section>
        )}

        