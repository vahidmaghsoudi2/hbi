                <article className="pro-product-card">
                  <h3>فروش امروز</h3>
                  <p className="pro-summary">{dashboardSales ? dashboardSales.sale_count.toLocaleString("fa-IR") : "—"} تراکنش</p>
                  <p className="pro-muted">{dashboardSales ? dashboardSales.revenue_toman.toLocaleString("fa-IR") + " تومان درآمد ثبت‌شده" : "دادهٔ فروش در دسترس نیست."}</p>
                  <Link to="/accounting?section=sales" className="pro-btn-secondary">گزارش فروش</Link>
                </article>
                <article className="pro-product-card">
                  <h3>موجودی انبار</h3>
                  <p className="pro-summary">{dashboardInventory ? dashboardInventory.length.toLocaleString("fa-IR") : "—"} ردیف موجودی</p>
                  <p className="pro-muted">{dashboardInventory ? "بر اساس گزارش موجودی فعلی." : "دادهٔ موجودی در دسترس نیست."}</p>
                  <Link to="/inventory?section=inventory" className="pro-btn-secondary">گزارش موجودی</Link>
                </article>
                <article className="pro-product-card">
                  <h3>هشدار موجودی کم</h3>
                  <p className="pro-summary">{dashboardLowStock ? dashboardLowStock.length.toLocaleString("fa-IR") : "—"} قلم</p>
                  <p className="pro-muted">آستانهٔ هشدار: موجودی ثبت‌شده ≤ ۵؛ بر پایهٔ گزارش رسمی موجودی کم.</p>
                  <Link to="/inventory?section=low-stock" className="pro-btn-secondary">کمبود موجودی</Link>
                </article>
              </div>
            </section>

            <section aria-labelledby="dashboard-alerts-title">
              <h2 id="dashboard-alerts-title">موارد نیازمند توجه</h2>
              <div className="pro-product-card">
                {dashboardLowStock === null ? (
                  <p className="pro-muted">هشدار موجودی کم قابل تأیید نیست؛ گزارش موجودی در دسترس نیست.</p>
                ) : dashboardLowStock.length === 0 ? (
                  <p className="pro-muted">طبق آستانهٔ ۵، موردی در گزارش موجودی کم ثبت نشده است.</p>
                ) : (
                  <>
                    <p role="status">{dashboardLowStock.length.toLocaleString("fa-IR")} قلم با موجودی ≤ ۵ نیازمند بررسی است.</p>
                    <Link to="/inventory?section=low-stock" className="pro-btn-primary">بازکردن کمبود موجودی</Link>
                  </>
                )}
                <p className="pro-muted">وضعیت پذیرش و QA محصول در این داشبورد عددگذاری نشده؛ API مدیریتیِ تأییدشده برای خلاصهٔ چرخهٔ محصول هنوز احراز نشده است.</p>
              </div>
            </section>

            <section aria-labelledby="dashboard-activity-title">
              <h2 id="dashboard-activity-title">آخرین گردش‌های انبار</h2>
              <div className="pro-product-card">
                {dashboardMovements === null ? (
                  <p className="pro-muted">گردش اخیر در دسترس نیست؛ گزارش گردش کالا را در بخش «کالا و موجودی» بررسی کنید.</p>
                ) : dashboardMovements.length === 0 ? (
                  <p className="pro-muted">گردشی برای نمایش ثبت نشده است.</p>
                ) : (
                  <ul className="pro-ol">
                    {dashboardMovements.map((movement) => (
                      <li key={movement.movement_id}>
                        {movement.movement_type} · {movement.product_id} · تغییر {movement.quantity_delta.toLocaleString("fa-IR")} · موجودی پس از عملیات {movement.quantity_after.toLocaleString("fa-IR")}
                        {movement.created_at ? ` · ${new Date(movement.created_at).toLocaleString("fa-IR")}` : ""}
                      </li>
                    ))}
                  </ul>
                )}
                <Link to="/inventory?section=stock-flow" className="pro-btn-secondary">گردش اخیر</Link>
              </div>
            </section>
          </section>
        )}

        