{pageView === "content" && active === "sales" && (
          <section className="pro-panel" id="sales">
            <h1>ثبت فروش</h1>
            <p className="pro-lead">الگوی صندوق فروش: ابتدا کالا و مبلغ. مشتری اجباری نیست — فروش حضوری بدون طرف‌حساب مجاز است.</p>
            <form className="pro-form" onSubmit={onSaleSubmit}>
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
                      {saleProductsLoading ? "در حال بارگذاری کاتالوگ…" : "نوسازی کاتالوگ فروش"}
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
                      <span className="pro-label">قیمت واحد (تومان)</span>
                      <p className="pro-input" aria-live="polite">
                        {!saleProductId ? "پس از انتخاب محصول" : salePrice == null ? "در حال دریافت…" : salePrice.toLocaleString("fa-IR")}
                      </p>
                    </div>
                  </div>
                  <p className="pro-muted">
                    موجودی قابل فروش: {!saleProductId ? "پس از انتخاب محصول" : saleStock == null ? "در حال دریافت…" : saleStock.toLocaleString("fa-IR")}
                  </p>
                  <p className="pro-summary">
                    مبلغ: <strong>{salePrice == null ? "—" : (saleQty * salePrice).toLocaleString("fa-IR")}</strong> تومان
                  </p>
                </fieldset>

                <fieldset className="pro-fieldset">
                  <legend>طرف‌حساب (اختیاری)</legend>
                  <p className="pro-muted">
                    پیش‌فرض این فاکتور «فروش حضوری بدون مشتری» است. شماره موبایل فیلد فرم فروش نیست؛ هویت مشتری در بخش مشتریان مدیریت می‌شود.
                  </p>
                  {saleCustomerId ? (
                    <div className="pro-actions">
                      <p>متصل به: <strong>{saleCustomerLabel}</strong> <span className="pro-muted">({saleCustomerId})</span></p>
                      <button
                        type="button"
                        className="pro-btn-secondary"
                        onClick={() => { setSaleCustomerId(null); setSaleCustomerLabel(null); }}
                      >
                        فروش بدون طرف‌حساب
                      </button>
                    </div>
                  ) : (
                    <>
                      <label className="pro-label" htmlFor="sale-customer-search">جست‌وجوی طرف‌حساب با نام خانوادگی</label>
                      <input
                        id="sale-customer-search"
                        className="pro-input"
                        value={saleCustomerSearch}
                        onChange={(e) => setSaleCustomerSearch(e.target.value)}
                        placeholder="نام خانوادگی…"
                        autoComplete="off"
                      />
                      <button type="button" className="pro-btn-secondary" onClick={() => void searchSaleCustomers()} disabled={customerSearchBusy}>
                        {customerSearchBusy ? "در حال جست‌وجو…" : "یافتن طرف‌حساب"}
                      </button>
                      {customerSearchResults.map((customer) => (
                        <button key={customer.customer_id} type="button" className="pro-btn-secondary" onClick={() => chooseSaleCustomer(customer)}>
                          {customer.family_name ?? "بدون نام خانوادگی"} · {customer.customer_id}
                        </button>
                      ))}
                    </>
                  )}
                </fieldset>

                <div className="pro-actions">
                  <button type="submit" className="pro-btn-primary" disabled={saleBusy}>
                    {saleBusy ? "در حال ثبت…" : "ثبت فروش"}
                  </button>
                  <button type="button" className="pro-btn-secondary" onClick={() => void refreshSalesTotal()}>
                    بروزرسانی جمع
                  </button>
                </div>
                <p className="pro-muted">جمع فروش نشست: {totalSales === null ? "—" : totalSales.toLocaleString("fa-IR")}</p>
            </form>
            {lastSale && (
              <div className="pro-rec-card" style={{ marginTop: "1rem" }}>
                <div className="pro-rec-rank">✓</div>
                <div>
                  <h3>آخرین فروش</h3>
                  <p className="pro-muted">
                    {String(lastSale.sale_id ?? "—")} · {Number(lastSale.total_amount_toman ?? 0).toLocaleString("fa-IR")} تومان
                  </p>
                </div>
              </div>
            )}
          </section>
        )}

        