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
      <h1>کاتالوگ کالاها</h1>
      <p className="lead">فهرست کالاهای ثبت‌شده در سیستم. خرید و ورود موجودی از منوی «کالا و انبار → خرید» است، نه از این فهرست.</p>
      <div className="row" style={{ marginBottom: "1rem", gap: "0.5rem", display: "flex", flexWrap: "wrap" }}>
        <Link className="btn" to="/">← داشبورد</Link>
        <Link className="btn" to="/purchase">خرید و ورود موجودی</Link>
      </div>
      {loading && <div className="alert">در حال بارگذاری…</div>}
      {error && <div className="alert error">{error}</div>}
      {!loading && !error && (
        <div className="product-list">
          {products.length === 0 && <p>محصولی یافت نشد.</p>}
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
