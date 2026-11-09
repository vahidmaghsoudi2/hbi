# راهنمای اجرایی PowerShell — خروجی امن اسنپ‌شات هفت محصول

**هدف:** اجرای امن اسکریپت موجود `scripts/export_seven_product_acceptance_snapshot.py` روی ویندوز، بدون تغییر پایگاه‌داده منبع.

**مرجع PR:** #523  
**ارتباط با #504:** این ابزار فقط snapshot محدود و read-only می‌سازد؛ اجرای آن به‌تنهایی پذیرش هفت محصول یا E2E را ثابت نمی‌کند.

---

## ۱. پیش‌نیازها و توقف‌های اجباری

1. Python 3.10 یا جدیدتر روی PATH باشد:
   ```powershell
   python --version
   ```
2. شاخهٔ PR #523 یا نسخه‌ای که همین اسکریپت را دارد، در مخزن محلی در دسترس باشد.
3. مسیر دقیق فایل SQLite محلی را بدانید. مسیر نمونه در این راهنما فرضی است؛ مسیر واقعی را خود اپراتور وارد می‌کند.
4. پیش از اجرا، برنامه‌ها/فرایندهایی را که روی DB می‌نویسند متوقف کنید. فایل rollback journal را دستی حذف نکنید.
5. اگر DB وجود ندارد، منبع symlink/reparse point است، rollback journal وجود دارد، یا احتمال تغییر هم‌زمان DB/WAL/SHM هست، اجرا را متوقف کنید.

## ۲. فرمان واحد اجرا و کنترل نتیجه

PowerShell را از ریشهٔ مخزن HBI باز کنید و کل بلوک زیر را اجرا کنید. در زمان درخواست، مسیر واقعی DB را وارد کنید:

```powershell
$ErrorActionPreference = "Stop"

# اثبات اینکه PowerShell در ریشه مخزن قرار دارد
$RepoRoot = (Resolve-Path -LiteralPath ".").Path
$Exporter = Join-Path $RepoRoot "scripts\export_seven_product_acceptance_snapshot.py"
if (-not (Test-Path -LiteralPath $Exporter -PathType Leaf)) {
  throw "Exporter not found. Open PowerShell at the HBI repository root."
}

# مسیر واقعی را وارد کنید؛ مسیر پیش‌فرضی فرض نمی‌شود
$DatabaseInput = Read-Host "مسیر کامل فایل SQLite محلی HBI"
if (-not (Test-Path -LiteralPath $DatabaseInput -PathType Leaf)) {
  throw "Database not found. Stop; no snapshot was created."
}
$Database = (Resolve-Path -LiteralPath $DatabaseInput).Path
$dbItem = Get-Item -LiteralPath $Database
if (($dbItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
  throw "Database is a symlink/reparse point. Use the real file path."
}
if (Test-Path -LiteralPath ($Database + "-journal")) {
  throw "SQLite rollback journal exists. Stop writers and investigate; do not delete the journal."
}

# خروجی تازه و non-overwriting
$OutputDir = Join-Path $RepoRoot "artifacts"
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$Output = Join-Path $OutputDir "hbi-seven-product-acceptance-snapshot-$Stamp.json"
if (Test-Path -LiteralPath $Output) {
  throw "Output already exists. Choose a new timestamped output path."
}

# Hash وضعیت منبع، پیش از اجرای exporter
function Get-OptionalSha256([string]$Path) {
  if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return "<missing>" }
  return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
}
$before = @{
  db      = Get-OptionalSha256 $Database
  wal     = Get-OptionalSha256 ($Database + "-wal")
  shm     = Get-OptionalSha256 ($Database + "-shm")
  journal = Get-OptionalSha256 ($Database + "-journal")
}

# اجرا؛ کد خروج باید بلافاصله ذخیره شود
& python $Exporter --database $Database --output $Output
$ExporterExitCode = $LASTEXITCODE

# Hash وضعیت منبع، بلافاصله پس از اجرا
$after = @{
  db      = Get-OptionalSha256 $Database
  wal     = Get-OptionalSha256 ($Database + "-wal")
  shm     = Get-OptionalSha256 ($Database + "-shm")
  journal = Get-OptionalSha256 ($Database + "-journal")
}
if (($before.db -ne $after.db) -or
    ($before.wal -ne $after.wal) -or
    ($before.shm -ne $after.shm) -or
    ($before.journal -ne $after.journal)) {
  throw "Source DB/WAL/SHM/journal changed during export. Quarantine the snapshot; investigate before reuse."
}
Write-Host "PASS: source DB/WAL/SHM/journal hashes unchanged."

if (-not (Test-Path -LiteralPath $Output -PathType Leaf)) {
  throw "Exporter produced no snapshot file. Exit code: $ExporterExitCode"
}
$Snapshot = Get-Content -LiteralPath $Output -Raw -Encoding UTF8 | ConvertFrom-Json

# خروجی کامل فقط وقتی آماده بررسی هفت‌محصولی است که تمام این شروط برقرار باشند
if ($ExporterExitCode -ne 0) {
  throw "Snapshot is NOT complete. Exporter exit code: $ExporterExitCode. Keep for diagnosis only; do not use for seven-product acceptance."
}
if ($Snapshot.integrity_check -ne "ok") {
  throw "Snapshot integrity_check is not ok."
}
if ([int]$Snapshot.foreign_key_violation_count -ne 0) {
  throw "Snapshot contains foreign-key violations."
}
if (@($Snapshot.missing_product_ids).Count -ne 0) {
  throw "One or more canonical Product IDs are missing."
}
if (@($Snapshot.missing_tables).Count -ne 0) {
  throw "One or more required tables are missing."
}
if ($Snapshot.missing_columns.Count -ne 0) {
  throw "One or more required columns are missing."
}

Write-Host "PASS: exporter exit code 0; integrity, foreign keys, seven IDs, tables and columns are structurally complete."
Write-Host "Snapshot: $Output"
Write-Host "This is an export-readiness result only, not ProductKnowledge/QA/product acceptance or Home Page E2E."
```

## ۳. تفسیر دقیق کد خروج

| کد | معنای واقعی | اقدام |
|---|---|---|
| `0` | هفت Product ID حاضرند؛ جدول‌ها و ستون‌های allowlist موجودند؛ integrity برابر `ok` و FK violation برابر صفر است | snapshot از نظر ساختاری آمادهٔ بررسی است؛ هنوز پذیرش محصول نیست |
| `2` | حداقل یکی از هفت Product ID در جدول Product پیدا نشده است | snapshot برای گیت کامل هفت‌محصولی مردود است؛ علت داده/محیط بررسی شود |
| `3` | جدول یا ستون لازم مفقود است، یا foreign-key violation وجود دارد | snapshot برای گیت کامل مردود است؛ schema/یکپارچگی بررسی شود |
| هر کد دیگر یا خطای اجرا | اجرای exporter کامل نشده یا خطای پیش‌بینی‌نشده رخ داده است | توقف؛ علت بررسی شود و نتیجه موفق اعلام نشود |

حتی کد خروج `0` فقط کامل‌بودن ساختاری export را نشان می‌دهد؛ نه تأیید هویت فیزیکی، QA، lifecycle، Evidence، ProductKnowledge، موجودی یا Recommendation.

## ۴. فیلدهای لازم برای بازبینی ساختاری

- `database_sha256`، `wal_sha256`، `shm_sha256`: Hash مؤلفه‌های منبع در snapshot.
- `integrity_check`: باید `ok` باشد.
- `foreign_key_violation_count`: باید `0` باشد.
- `missing_product_ids`: باید خالی باشد.
- `missing_tables` و `missing_columns`: باید خالی باشند.
- `table_row_counts`: تعداد ردیف‌های exportشده برای هر جدول.

وجود ردیف در جدول، به‌تنهایی اعتبار یا تأیید آن را ثابت نمی‌کند. وضعیت‌های DRAFT، PENDING، UNKNOWN، CONFLICT و OUT_OF_STOCK باید عیناً حفظ و تفسیر شوند؛ آن‌ها را برای سبزشدن خروجی تغییر ندهید.

## ۵. حریم خصوصی و اشتراک‌گذاری

- exporter فقط هفت Product ID ثابت و ردیف‌های متناظر آن‌ها را export می‌کند؛ جدول‌های Case و Customer و شناسه‌های مشتری در خروجی نیستند.
- خروجی ممکن است حاوی ادعاها، منابع و جزئیات داخلی محصول باشد. پیش از اشتراک‌گذاری، فایل را بازبینی و اطلاعات غیرضروری را حذف کنید؛ فایل خام را در فضای عمومی یا issue عمومی قرار ندهید.
- فایل snapshot را فقط از مسیر امن و با حداقل دسترسی منتقل کنید.
- هیچ اطلاعات واقعی مشتری را به این فرایند اضافه نکنید.

## ۶. رفتار ابزار و خطاهای متداول

| پیام / وضعیت | اقدام |
|---|---|
| `Source database must be an existing regular file, not a symlink` | مسیر واقعی فایل را بدهید، نه symlink |
| `A SQLite rollback journal exists` | writerها را متوقف و علت journal را بررسی کنید؛ آن را دستی حذف نکنید |
| `Output already exists; choose a new path` | نام خروجی timestamp جدید انتخاب کنید |
| `Source DB/SQLite sidecars changed while copying` | تغییر هم‌زمان منبع رخ داده؛ snapshot را مصرف نکنید |
| Exit code 2 | Product ID مفقود است؛ گیت هفت‌محصولی عبور نکرده |
| Exit code 3 | schema یا foreign key مشکل دارد؛ گیت عبور نکرده |

## ۷. مرز ابزار

این ابزار:
- فقط snapshot محدود read-only می‌سازد؛
- Product Master، Evidence، ProductKnowledge، QA، lifecycle، Inventory یا Recommendation را تغییر نمی‌دهد؛
- هیچ Case/Customer را export نمی‌کند؛
- به‌تنهایی گیت E2E مربوط به PR #504 را تکمیل نمی‌کند؛
- مجوز پذیرش محصول یا فعال‌سازی Recommendation ایجاد نمی‌کند.

**وضعیت سند:** راهنمای اجرای ابزار موجود؛ جایگزین قرارداد پذیرش محصول یا تصمیم Product Owner نیست.
