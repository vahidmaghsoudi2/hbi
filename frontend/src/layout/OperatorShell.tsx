import { useState } from "react";
import { Link, Outlet, useLocation, useNavigate } from "react-router-dom";
import "../styles/dashboard-gallery.css";
import "../styles/homepage-navigation.css";

type NavChild = { label: string; to: string };
type NavItem = {
  label: string;
  detail: string;
  icon: string;
  to: string;
  children: NavChild[];
};

const navigation: NavItem[] = [
  {
    label: "خانه",
    detail: "داشبورد و میان‌برها",
    icon: "⌂",
    to: "/",
    children: [],
  },
  {
    label: "مشتری و مشاوره",
    detail: "مشتریان و روند مشاوره",
    icon: "◎",
    to: "/workspace?panel=previous",
    children: [
      { label: "مشتریان", to: "/workspace?panel=previous" },
      { label: "پرونده مشاوره / مشتری", to: "/workspace?panel=profile" },
      { label: "مشاوره جدید", to: "/workspace?panel=consult" },
      { label: "پیشنهاد محصول", to: "/recommendation" },
      { label: "سوابق مشاوره", to: "/workspace?panel=previous" },
    ],
  },
  {
    label: "خرید و فروش",
    detail: "فروش مستقیم و خرید کالا",
    icon: "↗",
    to: "/sales",
    children: [
      { label: "ثبت فروش", to: "/sales" },
      { label: "سفارش خرید / ورود کالا", to: "/purchase" },
    ],
  },
  {
    label: "کالا و انبار",
    detail: "کاتالوگ و موجودی",
    icon: "▦",
    to: "/catalog",
    children: [
      { label: "محصولات (گالری / کاتالوگ)", to: "/catalog" },
      { label: "ورود کالا", to: "/purchase" },
    ],
  },
  {
    label: "حسابداری و گزارش",
    detail: "گزارش‌های موجود در سیستم",
    icon: "▤",
    to: "/accounting",
    children: [
      { label: "گزارش فروش / خانه حسابداری", to: "/accounting" },
    ],
  },
];

function pathMatches(to: string, pathname: string, search: string): boolean {
  if (to.startsWith("/workspace")) {
    const q = to.split("?")[1] ?? "";
    return pathname === "/workspace" && (q === "" || search.includes(q));
  }
  if (to === "/") return pathname === "/";
  return pathname === to || pathname.startsWith(to + "/");
}

export default function OperatorShell() {
  const navigate = useNavigate();
  const location = useLocation();
  const [openGroup, setOpenGroup] = useState<string | null>(() => {
    for (const item of navigation) {
      if (pathMatches(item.to, location.pathname, location.search)) return item.label;
      if (item.children.some((c) => pathMatches(c.to, location.pathname, location.search))) return item.label;
    }
    return "خرید و فروش";
  });

  function logout() {
    [
      "hbi_admin_access_token",
      "hbi_admin_refresh_token",
      "hbi_access_token",
      "hbi_refresh_token",
      "hbi_customer_id",
      "hbi_case_id",
      "hbi_operator_access_token",
      "hbi_po_access_token",
    ].forEach((key) => sessionStorage.removeItem(key));
    navigate("/login", { replace: true });
  }

  return (
    <main className="hbi-home" dir="rtl">
      <aside className="hbi-sidebar">
        <Link className="hbi-brand" to="/" aria-label="صفحه اصلی HBI">
          <span className="hbi-brand-mark">H</span>
          <span className="hbi-brand-copy">
            <strong>HBI</strong>
            <small>مدیریت سلامت و زیبایی</small>
          </span>
        </Link>
        <div className="hbi-nav-label">منوی اصلی</div>
        <nav className="hbi-side-nav" aria-label="منوی اصلی">
          {navigation.map((item) => {
            const hasChildren = item.children.length > 0;
            const isOpen = openGroup === item.label;
            const isCurrent = pathMatches(item.to, location.pathname, location.search);
            return (
              <div key={item.label} className="hbi-nav-group">
                <div className="hbi-nav-row">
                  <Link className={isCurrent ? "hbi-nav-item is-current" : "hbi-nav-item"} to={item.to}>
                    <span className="hbi-nav-icon" aria-hidden="true">{item.icon}</span>
                    <span className="hbi-nav-copy">
                      <strong>{item.label}</strong>
                      <small>{item.detail}</small>
                    </span>
                    {isCurrent ? <span className="hbi-nav-indicator" aria-hidden="true" /> : null}
                  </Link>
                  {hasChildren ? (
                    <button
                      type="button"
                      className="hbi-nav-toggle"
                      aria-expanded={isOpen}
                      aria-controls={`subnav-${item.label}`}
                      onClick={() => setOpenGroup((prev) => (prev === item.label ? null : item.label))}
                    >
                      <span aria-hidden="true">{isOpen ? "▾" : "◂"}</span>
                    </button>
                  ) : null}
                </div>
                {hasChildren && isOpen ? (
                  <div className="hbi-subnav" id={`subnav-${item.label}`}>
                    {item.children.map((child) => (
                      <Link key={child.label} className="hbi-subnav-link" to={child.to}>
                        {child.label}
                      </Link>
                    ))}
                  </div>
                ) : null}
              </div>
            );
          })}
        </nav>
        <div className="hbi-sidebar-bottom">
          <div className="hbi-operator-card">
            <span className="hbi-avatar" aria-hidden="true">م</span>
            <span>
              <strong>مدیر سیستم</strong>
              <small>دسترسی عملیاتی</small>
            </span>
          </div>
          <button type="button" className="hbi-logout" onClick={logout}>
            <span aria-hidden="true">↪</span> خروج از حساب
          </button>
        </div>
      </aside>
      <div className="hbi-main">
        <header className="hbi-topbar">
          <div className="hbi-breadcrumb">
            <span>منوی اصلی</span>
            <span aria-hidden="true">/</span>
            <strong>{location.pathname === "/" ? "خانه" : location.pathname}</strong>
          </div>
          <div className="hbi-topbar-note">
            <span className="hbi-status-dot" /> پنل مدیریت HBI
          </div>
        </header>
        <div className="hbi-page-wrap">
          <Outlet />
        </div>
      </div>
    </main>
  );
}
