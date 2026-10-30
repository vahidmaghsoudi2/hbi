import { useMemo, useState } from "react";
import mapMarkdown from "../../../docs/product-intake-knowledge-registry/SKIN_PROBLEM_SPACE_MAP_V0.1.md?raw";
import workingRecordsMarkdown from "../../../docs/product-intake-knowledge-registry/SKIN_PROBLEM_BANK_WORKING_RECORDS.md?raw";

type ProblemField = { label: string; value: string };
type PilotProblem = {
  id: string;
  mapName: string;
  shelfId: string;
  shelfName: string;
  canonicalType: string;
  mapDisposition: string;
  fields: ProblemField[];
};

const PILOT_IDS = ["P08", "P17", "P18", "P19", "P22", "P24"] as const;
const SOURCE_COMMIT = "ca27443959091da5b02562458856da0e70b02235";
const MAP_BLOB = "c57ce7edbcee513dcb60b735ce91b98de22d8aa2";
const WORKING_RECORDS_BLOB = "be4e7432631db71c2a16de293838dc6a1f64636c";
const REPOSITORY = "https://github.com/vahidmaghsoudi2/hbi";

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(message);
}

function normalizeType(value: string): string {
  return value.toLowerCase().replace(/\s*\/\s*/g, "/").replace(/\s+/g, " ").trim();
}

function parsePilotRecords(): PilotProblem[] {
  const shelfSection = mapMarkdown.split(/^## 2\. Lightweight Skin Problem Space\s*$/m)[1]?.split(/^## 3\./m)[0];
  const mapSection = mapMarkdown.split(/^## 4\. P01–P61 Mapping\s*$/m)[1]?.split(/^## 5\./m)[0];
  assert(shelfSection && mapSection, "ساختار بخش‌های ۲ و ۴ در Map مطابق قرارداد مورد انتظار نیست.");

  const shelfNames = new Map<string, string>();
  for (const line of shelfSection.split("\n")) {
    const match = line.trim().match(/^(S\d{2})\s*[—-]\s*(.+)$/);
    if (match) shelfNames.set(match[1], match[2].trim());
  }

  const mapRows = new Map<string, { name: string; type: string; shelf: string; disposition: string }[]>();
  let currentShelf = "";
  for (const line of mapSection.split("\n")) {
    const shelfHeading = line.trim().match(/^###\s+(S\d{2})\s*$/);
    if (shelfHeading) {
      currentShelf = shelfHeading[1];
      continue;
    }
    const row = line.trim().match(/^(P\d{2})\s+(.+?)\s+—\s+(.+?)\s+—\s+(.+?)\s+—\s+(.+)$/);
    if (!row || !(PILOT_IDS as readonly string[]).includes(row[1])) continue;
    const id = row[1];
    const name = row[2];
    const type = row[3];
    const disposition = row[5];
    const entries = mapRows.get(id) ?? [];
    entries.push({ name: name.trim(), type: type.trim(), shelf: currentShelf, disposition: disposition.trim() });
    mapRows.set(id, entries);
  }

  const headings = [...workingRecordsMarkdown.matchAll(/^###\s+(?:رکورد|Record)\s+(P\d{2})\s*[—-]\s*(.+)$/gm)];
  const parsed = new Map<string, { heading: string; fields: ProblemField[] }[]>();
  for (let index = 0; index < headings.length; index += 1) {
    const heading = headings[index];
    const id = heading[1];
    if (!(PILOT_IDS as readonly string[]).includes(id)) continue;
    const start = (heading.index ?? 0) + heading[0].length;
    const end = index + 1 < headings.length ? (headings[index + 1].index ?? workingRecordsMarkdown.length) : workingRecordsMarkdown.length;
    const section = workingRecordsMarkdown.slice(start, end);
    const fields: ProblemField[] = [];
    for (const line of section.split("\n")) {
      if (!/^\s*\|/.test(line)) continue;
      const cells = line.split("|");
      if (cells.length < 4) continue;
      const label = cells[1].trim();
      const value = cells.slice(2, -1).join("|").trim();
      if (!label || /^[-:]+$/.test(label) || label === "فیلد" || label === "Field") continue;
      fields.push({ label, value });
    }
    const entries = parsed.get(id) ?? [];
    entries.push({ heading: heading[2].trim(), fields });
    parsed.set(id, entries);
  }

  return PILOT_IDS.map((id) => {
    const mapped = mapRows.get(id) ?? [];
    const recorded = parsed.get(id) ?? [];
    if (id === "P22") {
      // P22 is intentionally cross-listed under S09; its canonical Map row remains under S04.
      assert(mapped.length === 2 && mapped[0].shelf === "S04" && mapped[1].shelf === "S09", "P22: ارجاع متقاطع S04/S09 در Map مطابق ساختار مورد انتظار نیست.");
    } else {
      assert(mapped.length === 1, `${id}: در جدول نگاشت Map باید دقیقاً یک ردیف وجود داشته باشد؛ تعداد فعلی ${mapped.length} است.`);
    }
    assert(recorded.length === 1, `${id}: در Working Records باید دقیقاً یک heading وجود داشته باشد؛ تعداد فعلی ${recorded.length} است.`);
    const mapRow = mapped[0];
    const record = recorded[0];
    assert(shelfNames.has(mapRow.shelf), `${id}: نام قفسهٔ ${mapRow.shelf} در Map پیدا نشد.`);
    assert(record.fields.length === 14, `${id}: انتظار ۱۴ فیلد داده می‌رفت؛ ${record.fields.length} فیلد پیدا شد.`);
    const fieldKeys = record.fields.map((field) => field.label);
    assert(new Set(fieldKeys).size === fieldKeys.length, `${id}: کلید فیلد تکراری در Working Records وجود دارد.`);
    assert(record.fields.some((field) => field.label === "ID نقشه" || field.label === "Map ID"), `${id}: فیلد شناسه در Working Records وجود ندارد.`);
    const typeField = record.fields.find((field) => field.label === "نوع واحد" || field.label === "Unit type");
    assert(typeField, `${id}: فیلد نوع واحد وجود ندارد.`);
    const recordedType = typeField.value.split(/\s+—\s+/)[0].trim();
    assert(normalizeType(recordedType) === normalizeType(mapRow.type), `${id}: نوع canonical در Map و Working Records ناسازگار است.`);
    const idField = record.fields.find((field) => field.label === "ID نقشه" || field.label === "Map ID");
    assert(idField?.value === id, `${id}: شناسهٔ Working Records با heading سازگار نیست.`);
    return {
      id,
      mapName: mapRow.name,
      shelfId: mapRow.shelf,
      shelfName: shelfNames.get(mapRow.shelf) as string,
      canonicalType: mapRow.type,
      mapDisposition: mapRow.disposition,
      fields: record.fields,
    };
  });
}

function fieldValue(fields: ProblemField[], labels: string[]): string {
  return fields.find((field) => labels.includes(field.label))?.value ?? "در منبع ثبت نشده";
}

export default function SkinProblemBank({ onBack }: { onBack: () => void }) {
  const parsed = useMemo(() => {
    try {
      return { records: parsePilotRecords(), error: null as string | null };
    } catch (error) {
      return { records: [] as PilotProblem[], error: error instanceof Error ? error.message : String(error) };
    }
  }, []);
  const [selectedId, setSelectedId] = useState<string>("P17");
  const [search, setSearch] = useState("");
  const [shelfFilter, setShelfFilter] = useState("ALL");

  const filtered = useMemo(() => {
    const query = search.trim().toLocaleLowerCase();
    return parsed.records.filter((record) => {
      if (shelfFilter !== "ALL" && record.shelfId !== shelfFilter) return false;
      if (!query) return true;
      const searchable = [
        record.id, record.mapName, record.shelfId, record.shelfName, record.canonicalType,
        record.mapDisposition, ...record.fields.flatMap((field) => [field.label, field.value]),
      ].join(" ").toLocaleLowerCase();
      return searchable.includes(query);
    });
  }, [parsed.records, search, shelfFilter]);

  const selected = filtered.find((record) => record.id === selectedId) ?? filtered[0] ?? null;

  return (
    <section className="pro-panel" aria-labelledby="skin-problem-bank-title">
      <div className="pro-section-head">
        <h1 id="skin-problem-bank-title">بانک مشکلات پوستی</h1>
        <button type="button" className="pro-btn-secondary" onClick={onBack}>بازگشت به دانش پوست</button>
      </div>
      <p className="pro-lead">نمای داخلی و فقط‌خواندنی از شش مدخل منتخب پایلوت. فهرست مرجع کامل P01–P61 همچنان در Map نگهداری می‌شود؛ این صفحه ادعای پوشش کل بانک را ندارد.</p>
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
                {[...new Map(parsed.records.map((record) => [record.shelfId, record.shelfName])).entries()].map(([id, name]) => <option key={id} value={id}>{id} · {name}</option>)}
              </select>
            </div>
          </div>

          <div className="pro-problem-layout">
            <nav className="pro-problem-list" aria-label="شش مدخل منتخب مشکلات پوستی">
              <p className="pro-problem-count">{filtered.length} از {parsed.records.length} مدخل پایلوت</p>
              {filtered.map((record) => (
                <button key={record.id} type="button" className={`pro-problem-item${selected?.id === record.id ? " is-active" : ""}`} aria-pressed={selected?.id === record.id} onClick={() => setSelectedId(record.id)}>
                  <span className="pro-problem-item-id">{record.id}</span>
                  <strong>{record.mapName}</strong>
                  <span>{record.shelfId} · {record.canonicalType}</span>
                </button>
              ))}
              {filtered.length === 0 ? <p className="pro-muted">در محدودهٔ همین شش مدخل نتیجه‌ای پیدا نشد.</p> : null}
            </nav>

            {selected ? (
              <article className="pro-problem-detail" aria-labelledby="skin-problem-detail-title">
                <div className="pro-problem-detail-head">
                  <div>
                    <span className="pro-problem-item-id">{selected.id}</span>
                    <h2 id="skin-problem-detail-title">{selected.mapName}</h2>
                    <p>{selected.shelfId} · {selected.shelfName}</p>
                  </div>
                  <span className="pro-problem-type">{selected.canonicalType}</span>
                </div>
                <dl className="pro-dl">
                  <div><dt>نوع canonical در Map</dt><dd>{selected.canonicalType}</dd></div>
                  <div><dt>جایگاه در Map</dt><dd>{selected.shelfId} · {selected.shelfName}</dd></div>
                  <div><dt>Disposition در Map</dt><dd>{selected.mapDisposition}</dd></div>
                  {selected.fields.map((field) => <div key={field.label}><dt>{field.label}</dt><dd>{field.value || "مقدار خالی در منبع"}</dd></div>)}
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
