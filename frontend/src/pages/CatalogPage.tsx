import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listProducts } from "../api/client";
import type { ProductDTO } from "../types/api";

export default function CatalogPage() {
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
    return () => { cancelled = true; };
  }, []);

  return (
    <section>
      <h1>کاتالوگ محصولات با هویت تأییدشده</h1>
      <p className="lead">فهرست فقط محصولاتی را نشان می‌دهد که هویت آن‌ها VERIFIED است؛ این به‌تنهایی به معنی فعال بودن یا قابل فروش بودن نیست. دسترسی از مسیر احراز هویت مدیر کنترل می‌شود.</p>
      <div className="row" style={{ marginBottom: "1rem" }}>
        <Link className="btn" to="/">بازگشت به منوی اصلی</Link>
      </div>
      {loading && <div className="alert">در حال بارگذاری…</div>}
      {error && <div className="alert error" role="alert">{error}</div>}
      {!loading && !error && (
        <div className="product-list">
          {products.length === 0 && <p role="status">محصولی با هویت تأییدشده برای نمایش وجود ندارد.</p>}
          {products.map((p) => (
            <div key={p.product_id} className="card">
              <strong>{p.product_name}</strong>
              <span>{p.brand}</span>
              <small>{p.product_id}</small>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
