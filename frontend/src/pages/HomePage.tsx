import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listProducts } from "../api/client";
import type { ProductDTO } from "../types/api";

export default function HomePage() {
  const [products, setProducts] = useState<ProductDTO[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await listProducts();
        if (!cancelled) setProducts(data);
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : String(e));
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <section>
      <h1>کاتالوگ محصولات</h1>
      <p className="lead">
        فهرست عمومی محصولات تأییدشده (بدون نیاز به احراز هویت). برای مسیر کامل Pilot از منوی بالا استفاده کنید.
      </p>
      <div className="row" style={{ marginBottom: "1rem" }}>
        <Link className="btn" to="/pilot">
          شروع مسیر Pilot
        </Link>
      </div>

      {loading && <div className="alert">در حال بارگذاری…</div>}
      {error && (
        <div className="alert error">
          خطا در دریافت محصولات. Backend را روی پورت ۸۰۰۰ بالا بیاورید.
          <div className="muted" style={{ marginTop: 6 }}>
            {error}
          </div>
        </div>
      )}

      {!loading && !error && products.length === 0 && (
        <div className="alert">محصول تأییدشدهای یافت نشد.</div>
      )}

      <div className="grid">
        {products.map((p) => (
          <article key={p.product_id} className="card product-card">
            <h3>{p.product_name}</h3>
            <div className="meta">{p.brand}</div>
            <div className="meta">شناسه: {p.product_id}</div>
            <span className="badge">{p.identity_status}</span>
          </article>
        ))}
      </div>
    </section>
  );
}
