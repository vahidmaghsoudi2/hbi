# apply_encyclopedia_menu.py — run from HBI repo root on the laptop
# Usage: python tools/apply_encyclopedia_menu.py
from pathlib import Path

path = Path("frontend/src/pages/NewHomePage.tsx")
text = path.read_text(encoding="utf-8")
if "ENCYCLOPEDIA_SUBMENUS" in text:
    print("Already applied.")
    raise SystemExit(0)


def rep(old: str, new: str, label: str) -> None:
    global text
    c = text.count(old)
    if c != 1:
        raise SystemExit(f"FAIL {label}: count={c}")
    text = text.replace(old, new)
    print("OK", label)


rep(
    'type Panel = "home" | "consult" | "previous" | "profile" | "catalog" | "review" | "intake" | "results" | "sales" | "about";',
    'type Panel = "home" | "consult" | "previous" | "profile" | "catalog" | "review" | "intake" | "results" | "sales" | "about" | "encyclopedia";',
    "panel",
)
rep(
    'type MainSection = "home" | "customers" | "consultation" | "sales" | "products" | "inventory" | "purchases" | "reports";',
    'type MainSection = "home" | "customers" | "consultation" | "sales" | "products" | "inventory" | "purchases" | "reports" | "encyclopedia";',
    "mainsection",
)
rep(
    'const CONSULTATION_LINES = [{ id: "SKIN", label: "پوست" }] as const;\nconst INITIAL_RECOMMENDATION_LIMIT = 5;',
    '''const CONSULTATION_LINES = [{ id: "SKIN", label: "پوست" }] as const;
const INITIAL_RECOMMENDATION_LIMIT = 5;

/** PO-approved encyclopedia structure; mostly no dedicated page yet. Knowledge "سایر" is not product-line OTHER. */
const ENCYCLOPEDIA_SUBMENUS = [
  { id: "skin", label: "دانش پوست", status: "reference-available-no-dedicated-page", blurb: "ارجاع به بانک رسمی مشکلات پوست در مستندات پروژه؛ فهرست موازی ساخته نمی‌شود و اعتبار پزشکی ادعا نمی‌شود." },
  { id: "hair", label: "دانش مو", status: "no-page-yet", blurb: "دانش ساختار و مراقبت مو و پوست سر. رنگ‌آمیزی در زیرمنوی «رنگ مو» است." },
  { id: "perfume", label: "دانش ادکلن", status: "no-page-yet", blurb: "مرجع دانشی عطر و ادکلن؛ صفحهٔ اختصاصی هنوز آماده نیست." },
  { id: "hair-color", label: "رنگ مو", status: "no-page-yet", blurb: "رنگ‌آمیزی و نگهداری موی رنگ‌شده؛ متمایز از دانش عمومی مو." },
  { id: "makeup", label: "آرایش", status: "no-page-yet", blurb: "مرجع دانشی آرایش؛ صفحهٔ اختصاصی هنوز آماده نیست." },
  { id: "tools", label: "ابزار", status: "no-page-yet", blurb: "دانش ابزارهای مرتبط؛ صفحهٔ اختصاصی هنوز آماده نیست." },
  { id: "other", label: "سایر", status: "no-page-yet", blurb: "دستهٔ تکمیلی دانشنامه؛ با مقدار OTHER در خط محصول یکی نیست." },
] as const;''',
    "const",
)
rep(
    "  const [returnToCatalog, setReturnToCatalog] = useState(false);\n  const [token, setToken]",
    "  const [returnToCatalog, setReturnToCatalog] = useState(false);\n  const [encyclopediaTopic, setEncyclopediaTopic] = useState<(typeof ENCYCLOPEDIA_SUBMENUS)[number][\"id\"] | null>(null);\n  const [token, setToken]",
    "state",
)
rep(
    '''  function openMainSection(next: MainSection) {
    setReturnToDashboard(false);
    setReturnToCatalog(false);
    setMainSection(next);
    setError(null);
    setStatusMsg(null);
    if (next === "home") {
      setActive("home");
      setPageView("content");
    } else {
      setPageView("section");
    }
  }''',
    '''  function openMainSection(next: MainSection) {
    setReturnToDashboard(false);
    setReturnToCatalog(false);
    setMainSection(next);
    setEncyclopediaTopic(null);
    setError(null);
    setStatusMsg(null);
    if (next === "home") {
      setActive("home");
      setPageView("content");
    } else {
      setPageView("section");
    }
  }

  function openEncyclopediaTopic(id: (typeof ENCYCLOPEDIA_SUBMENUS)[number]["id"]) {
    setEncyclopediaTopic(id);
    setActive("encyclopedia");
    setPageView("content");
    setError(null);
    setStatusMsg(null);
  }''',
    "open",
)
card = (
    '<article className="pro-product-card"><h2>حسابداری و گزارش‌ها</h2>'
    '<p className="pro-muted">گزارش فروش و مالی؛ گزارش موجودی و گردش کالا در بخش «کالا و موجودی» قرار دارد.</p>'
    '<button type="button" className="pro-btn-primary" onClick={() => openMainSection("reports")}>'
    "ورود به حسابداری و گزارش‌ها</button></article>"
)
rep(
    card,
    card
    + """
              <article className=\"pro-product-card\"><h2>دانشنامه</h2><p className=\"pro-muted\">منابع دانشی پوست، مو، ادکلن، رنگ مو، آرایش، ابزار و سایر؛ ساختار مصوب مالک محصول — محتوای بیشتر زیرمنوها هنوز آماده نیست.</p><button type=\"button\" className=\"pro-btn-primary\" onClick={() => openMainSection(\"encyclopedia\")}>ورود به دانشنامه</button></article>""",
    "card",
)
rep(
    '''                products: "مدیریت محصولات", inventory: "کالا و موجودی", purchases: "خرید",
                reports: "حسابداری و گزارش‌ها", home: "خانه و داشبورد",
              } as Record<MainSection, string>)[mainSection]}</h1>''',
    '''                products: "مدیریت محصولات", inventory: "کالا و موجودی", purchases: "خرید",
                reports: "حسابداری و گزارش‌ها", encyclopedia: "دانشنامه", home: "خانه و داشبورد",
              } as Record<MainSection, string>)[mainSection]}</h1>''',
    "title",
)
rep(
    '''              {mainSection === "reports" ? <>
                <article className="pro-product-card"><h2>گزارش فروش</h2><p className="pro-muted">خلاصه فروش روز جاری.</p><Link to="/accounting?section=sales" className="pro-btn-primary">بازکردن گزارش فروش</Link></article>
                <article className="pro-product-card"><h2>گزارش مالی</h2><p className="pro-muted">خلاصه گزارش مالی موجود.</p><Link to="/accounting?section=finance-report" className="pro-btn-primary">بازکردن گزارش مالی</Link></article>
              </> : null}
            </div>
          </section>
        )}''',
    '''              {mainSection === "reports" ? <>
                <article className="pro-product-card"><h2>گزارش فروش</h2><p className="pro-muted">خلاصه فروش روز جاری.</p><Link to="/accounting?section=sales" className="pro-btn-primary">بازکردن گزارش فروش</Link></article>
                <article className="pro-product-card"><h2>گزارش مالی</h2><p className="pro-muted">خلاصه گزارش مالی موجود.</p><Link to="/accounting?section=finance-report" className="pro-btn-primary">بازکردن گزارش مالی</Link></article>
              </> : null}
              {mainSection === "encyclopedia" ? <>
                <p className="pro-muted">ساختار منو به تأیید مالک محصول رسیده است. فقط وقتی مرجع یا صفحه آماده باشد به عنوان آماده معرفی می شود.</p>
                {ENCYCLOPEDIA_SUBMENUS.map((item) => (
                  <article className="pro-product-card" key={item.id}>
                    <h2>{item.label}</h2>
                    <p className="pro-muted">{item.blurb}</p>
                    <p className="pro-muted">وضعیت: {item.status === "no-page-yet" ? "صفحه اختصاصی هنوز آماده نیست" : "مرجع مستنداتی موجود — صفحه داخل برنامه هنوز اختصاصی نیست"}</p>
                    <button type="button" className="pro-btn-primary" onClick={() => openEncyclopediaTopic(item.id)}>مشاهده</button>
                  </article>
                ))}
              </> : null}
            </div>
          </section>
        )}''',
    "section",
)
marker = '{pageView === "content" && active === "home" && ('
enc = '''        {pageView === "content" && active === "encyclopedia" && (
          <section className="pro-panel">
            <h1>دانشنامه{encyclopediaTopic ? ` · ${ENCYCLOPEDIA_SUBMENUS.find((x) => x.id === encyclopediaTopic)?.label ?? ""}` : ""}</h1>
            <p className="pro-lead">این بخش برای تجمیع منابع دانشی است و جایگزین منوهای عملیاتی نیست.</p>
            {(() => {
              const item = ENCYCLOPEDIA_SUBMENUS.find((x) => x.id === encyclopediaTopic);
              if (!item) return <p className="pro-muted">موضوعی انتخاب نشده است.</p>;
              return (
                <article className="pro-product-card">
                  <h2>{item.label}</h2>
                  <p>{item.blurb}</p>
                  <p className="pro-muted">وضعیت: <code>{item.status}</code></p>
                  {item.id === "skin" ? (
                    <p className="pro-muted">مرجع مستندات: <code>docs/product-intake-knowledge-registry/SKIN_PROBLEM_BANK_WORKSPACE_INDEX.md</code> — ادعای تأیید پزشکی ندارد.</p>
                  ) : (
                    <p className="pro-muted">صفحه یا بسته دانشی تأییدشده برای نمایش عملیاتی هنوز ثبت نشده است.</p>
                  )}
                  <button type="button" className="pro-btn-secondary" onClick={() => { setEncyclopediaTopic(null); openMainSection("encyclopedia"); }}>بازگشت به فهرست دانشنامه</button>
                </article>
              );
            })()}
          </section>
        )}

'''
if marker not in text:
    raise SystemExit("home marker missing")
text = text.replace(marker, enc + marker, 1)
path.write_text(text, encoding="utf-8")
print("Applied to", path.resolve())
