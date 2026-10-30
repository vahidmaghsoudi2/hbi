import { useMemo, useState } from "react";
import mapMarkdown from "../../../docs/product-intake-knowledge-registry/SKIN_PROBLEM_SPACE_MAP_V0.1.md?raw";
import workingRecordsMarkdown from "../../../docs/product-intake-knowledge-registry/SKIN_PROBLEM_BANK_WORKING_RECORDS.md?raw";
import { parseProblemRecords, type ProblemRecord } from "./skinProblemParser";

const PILOT_IDS = ["P08", "P17", "P18", "P19", "P22", "P24"] as const;
const SOURCE_COMMIT = "ca27443959091da5b02562458856da0e70b02235";
const MAP_BLOB = "c57ce7edbcee513dcb60b735ce91b98de22d8aa2";
const WORKING_RECORDS_BLOB = "be4e7432631db71c2a16de293838dc6a1f64636c";
const REPOSITORY = "https://github.com/vahidmaghsoudi2/hbi";

export default function SkinProblemBank({ onBack }: { onBack: () => void }) {
  const parsed = useMemo(() => {
    try {
      const allRecords = parseProblemRecords(mapMarkdown, workingRecordsMarkdown);
      return {
        records: allRecords.filter((record) => (PILOT_IDS as readonly string[]).includes(record.id)),
        error: null as string | null,
      };
    } catch (error) {
      return { records: [] as ProblemRecord[], error: error instanceof Error ? error.message : String(error) };
    }
  }, []);
  const [selectedId, setSelectedId] = useState<string>("P17");
  const [search, setSearch] = useState("");
  const [shelfFilter, setShelfFilter] = useState("ALL");

  const filtered = useMemo(() => {
    const query = search.trim().toLocaleLowerCase();
    return parsed.records.filter((record) => {
      const primary = record.mapEntries[record.canonicalMapEntryIndex ?? 0];
      if (shelfFilter !== "ALL" && primary?.shelfId !== shelfFilter) return false;
      if (!query) return true;
      const searchable = [
        record.id, record.headingName, ...record.mapEntries.flatMap((entry) =>
          [entry.shelfId, entry.shelfName, entry.name, entry.type, entry.relationshipRaw, entry.disposition]),
        ...record.fields.flatMap((field) => [field.label, field.value]),
      ].join(" ").toLocaleLowerCase();
      return searchable.includes(query);
    });
  }, [parsed.records, search, shelfFilter]);

  const selected = filtered.find((record) => record.id === selectedId) ?? filtered[0] ?? null;
  const selectedMap = selected?.mapEntries[selected.canonicalMapEntryIndex ?? 0] ?? null;

  return (
    <section className="pro-panel" aria-labelledby="skin-problem-bank-title">
      <div className="pro-section-head">
        <h1 id="skin-problem-bank-title">بانک مشکلات پوستی</h1>
        <button type="button" className="pro-btn-secondary" onClick={onBack}>بازگشت به دانش پوست</button>
      </div>
      <p className="pro-lead">نمای داخلی و فقط‌خواندنی از شش مدخل منتخب پایلوت. Parser داده‌های مرجع P01–P61 را پردازش می‌کند؛ نمایش این صفحه همچنان به شش مدخل محدود است.</p>
      <div className="pro-problem-scope" role="note">
        <strong>محدوده و محدودیت</strong>
        <p>این صفحه ابزار تشخیص، پذیرش Need، ارزیابی آمادگی مشاوره یا توصیهٔ محصول نیست. وضعیت‌ها و عبارت‌های UNKNOWN، GAP، Conflict و Accepted عیناً از منبع خوانده می‌شوند و به نتیجهٔ مثبت یا منفی تبدیل نمی‌شوند.</p>
        <p>نقش‌های پایلوت فقط برای بررسی محدود ارتباط‌ها هستند و نوع canonical رکورد را جایگزین نمی‌کنند.</p>
      </div>

      {parsed.error ? (
        <div className="pro-alert" role="alert">
          <strong>نمایش متوقف شد؛ منبع با قرارداد استخراج سازگار نیست.</strong>
          <p>{parsed.error}</p>
          <p>برای جلوگیری از نمایش ناقص یا نادرست، هیچ رکوردی بارگذاری نشده است.</p>
        </div>
      ) : (
        <>
          <div className="pro-problem-controls">
            <div>
              <label htmlFor="skin-problem-search">جست‌وجو در شش مدخل پایلوت</label>
              <input id="skin-problem-search" className="pro-input" type="search" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="شناسه، نام، نوع، وضعیت یا متن فیلد…" />
            </div>
            <div>
              <label htmlFor="skin-problem-shelf">فیلتر قفسه</label>
              <select id="skin-problem-shelf" className="pro-input" value={shelfFilter} onChange={(event) => setShelfFilter(event.target.value)}>
                <option value="ALL">همهٔ قفسه‌های پایلوت</option>
                {Array.from(new Map(parsed.records.map((record) => {
                  const primary = record.mapEntries[record.canonicalMapEntryIndex ?? 0];
                  return [primary.shelfId, primary.shelfName] as [string, string];
                })).entries()).map(([id, name]) => <option key={id} value={id}>{id} · {name}</option>)}
              </select>
            </div>
          </div>

          <div className="pro-problem-layout">
            <nav className="pro-problem-list" aria-label="شش مدخل منتخب مشکلات پوستی">
              <p className="pro-problem-count">{filtered.length} از {parsed.records.length} مدخل پایلوت</p>
              {filtered.map((record) => {
                const primary = record.mapEntries[record.canonicalMapEntryIndex ?? 0];
                return (
                  <button key={record.id} type="button" className={`pro-problem-item${selected?.id === record.id ? " is-active" : ""}`} aria-pressed={selected?.id === record.id} onClick={() => setSelectedId(record.id)}>
                    <span className="pro-problem-item-id">{record.id}</span>
                    <strong>{primary.name}</strong>
                    <span>{primary.shelfId} · {primary.type}</span>
                  </button>
                );
              })}
              {filtered.length === 0 ? <p className="pro-muted">در محدودهٔ همین شش مدخل نتیجه‌ای پیدا نشد.</p> : null}
            </nav>

            {selected && selectedMap ? (
              <article className="pro-problem-detail" aria-labelledby="skin-problem-detail-title">
                <div className="pro-problem-detail-head">
                  <div>
                    <span className="pro-problem-item-id">{selected.id}</span>
                    <h2 id="skin-problem-detail-title">{selectedMap.name}</h2>
                    <p>{selectedMap.shelfId} · {selectedMap.shelfName}</p>
                  </div>
                  <span className="pro-problem-type">{selectedMap.type}</span>
                </div>
                <dl className="pro-dl">
                  <div><dt>نوع در Map</dt><dd>{selectedMap.type}</dd></div>
                  <div><dt>جایگاه در Map</dt><dd>{selectedMap.shelfId} · {selectedMap.shelfName}</dd></div>
                  <div><dt>Disposition در Map</dt><dd>{selectedMap.disposition}</dd></div>
                  {selected.mapEntries.map((entry, index) => (
                    <div key={`${entry.shelfId}-${index}`}>
                      <dt>رابطهٔ Map · {entry.role === "canonical" ? "canonical" : entry.role === "cross_reference" ? "cross-reference" : "unspecified"}</dt>
                      <dd>{entry.shelfId} · {entry.relationshipRaw}{entry.pathRaw ? ` · مسیر: ${entry.pathRaw}` : ""}</dd>
                    </div>
                  ))}
                  {selected.fields.map((field, index) => <div key={`${field.label}-${index}`}><dt>{field.label}</dt><dd>{field.value || "مقدار خالی در منبع"}</dd></div>)}
                </dl>
                <p className="pro-problem-source-note">مقادیر بالا متن منبع‌اند؛ این صفحه آن‌ها را تفسیر یا تأیید پزشکی نمی‌کند.</p>
              </article>
            ) : null}
          </div>
        </>
      )}

      <footer className="pro-problem-provenance">
        <strong>منشأ داده و نسخه</strong>
        <p>Commit مبنا: <code>{SOURCE_COMMIT}</code></p>
        <p>Map blob: <code>{MAP_BLOB}</code></p>
        <p>Working Records blob: <code>{WORKING_RECORDS_BLOB}</code></p>
        <p><a href={`${REPOSITORY}/blob/${SOURCE_COMMIT}/docs/product-intake-knowledge-registry/SKIN_PROBLEM_SPACE_MAP_V0.1.md`} target="_blank" rel="noreferrer">مشاهده Map در همان commit</a> · <a href={`${REPOSITORY}/blob/${SOURCE_COMMIT}/docs/product-intake-knowledge-registry/SKIN_PROBLEM_BANK_WORKING_RECORDS.md`} target="_blank" rel="noreferrer">مشاهده Working Records در همان commit</a></p>
        <p className="pro-muted">منابع هنگام build از فایل‌های مرجع داخل همین repository خوانده می‌شوند؛ صفحه در زمان اجرا به GitHub یا API درخواست نمی‌فرستد.</p>
      </footer>
    </section>
  );
}
