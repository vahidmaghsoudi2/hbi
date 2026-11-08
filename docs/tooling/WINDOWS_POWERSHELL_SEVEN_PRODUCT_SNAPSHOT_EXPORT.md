# راهنمای اجرایی PowerShell — خروجی امن اسنپ‌شات هفت محصول

**هدف:** اجرای امن اسکریپت موجود `scripts/export_seven_product_acceptance_snapshot.py` روی ویندوز، بدون تغییر پایگاه‌داده منبع.

**مرجع PR:** #523  
**محدوده:** فقط آماده‌سازی ورودی read-only برای گیت پذیرش هفت‌محصولی؛ این راهنما خودِ پذیرش #504 نیست.

---

## ۱. پیش‌نیازها

1. Python 3.10+ روی PATH باشد:
   ```powershell
   python --version
   ```
2. مخزن HBI را clone کرده و روی شاخهٔ مربوط به exporter باشید (یا فایل اسکریپت را از همان شاخه داشته باشید).
3. مسیر پایگاه‌داده محلی SQLite مشخص باشد (معمولاً `data\hbi.db`).
4. **هیچ writer فعالی** نباید روی همان DB در حال نوشتن باشد. اگر فایل `-journal` وجود دارد، ابتدا writerها را متوقف کنید.

---

## ۲. قواعد ایمنی اجباری

- خروجی را **هرگز** روی خود DB یا sidecarهای `-wal` / `-shm` / `-journal` ننویسید.
- اگر فایل خروجی از قبل وجود دارد، exporter **بازنویسی نمی‌کند**؛ نام جدید انتخاب کنید.
- منبع نباید symlink باشد.
- exporter فقط کپی پایدار DB+WAL می‌گیرد و SQLite را فقط روی کپی موقت باز می‌کند؛ منبع را با SQLite باز نمی‌کند.
- خروجی ممکن است ادعاها و ارجاعات محصول را شامل شود؛ قبل از اشتراک‌گذاری بازبینی کنید.

---

## ۳. اجرای امن (کپی‌پیست PowerShell)

از ریشهٔ مخزن:

```powershell
# مسیرها را مطابق محیط خود تنظیم کنید
$RepoRoot = (Get-Location).Path
$Database = Join-Path $RepoRoot "data\hbi.db"
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$Output = Join-Path $RepoRoot "artifacts\hbi-seven-product-acceptance-snapshot-$Stamp.json"

# اطمینان از وجود پوشه خروجی
New-Item -ItemType Directory -Force -Path (Split-Path $Output) | Out-Null

# پیش‌بررسی وجود DB و نبود journal
if (-not (Test-Path -LiteralPath $Database -PathType Leaf)) {
  throw "Database not found: $Database"
}
if (Test-Path -LiteralPath ($Database + "-journal")) {
  throw "Rollback journal exists. Stop writers and retry."
}

# اجرای exporter
python "$RepoRoot\scripts\export_seven_product_acceptance_snapshot.py" `
  --database $Database `
  --output $Output

# کد خروج:
# 0 = کامل و سالم
# 2 = حداقل یکی از هفت product_id مفقود است
# 3 = جدول/ستون مفقود یا foreign-key violation
Write-Host "Exit code: $LASTEXITCODE"
Write-Host "Output: $Output"
```

---

## ۴. تفسیر سریع خروجی کنسول

خروجی JSON خلاصه شامل این فیلدهاست:

| فیلد | معنی |
|------|------|
| `database_sha256` / `wal_sha256` / `shm_sha256` | اثرانگشت منبع در لحظهٔ کپی پایدار |
| `integrity_check` | باید `ok` باشد |
| `foreign_key_violation_count` | باید `0` باشد |
| `missing_product_ids` | شناسه‌های canonical که در Product پیدا نشدند |
| `missing_tables` / `missing_columns` | شکاف schema |
| `table_row_counts` | تعداد ردیف‌های محدودهٔ هفت محصول |

اگر `missing_product_ids` خالی نیست، snapshot برای گیت کامل هفت‌محصولی هنوز کافی نیست؛ اما فایل همچنان برای بررسی جزئی قابل استفاده است.

---

## ۵. تأیید عدم تغییر منبع (اختیاری ولی توصیه‌شده)

قبل و بعد از اجرا می‌توانید hash فایل‌ها را مقایسه کنید:

```powershell
function Get-FileSha256([string]$Path) {
  if (-not (Test-Path -LiteralPath $Path)) { return $null }
  return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLower()
}

$beforeDb  = Get-FileSha256 $Database
$beforeWal = Get-FileSha256 ($Database + "-wal")
$beforeShm = Get-FileSha256 ($Database + "-shm")

# ... اجرای exporter ...

$afterDb  = Get-FileSha256 $Database
$afterWal = Get-FileSha256 ($Database + "-wal")
$afterShm = Get-FileSha256 ($Database + "-shm")

if ($beforeDb -ne $afterDb -or $beforeWal -ne $afterWal -or $beforeShm -ne $afterShm) {
  throw "Source DB/WAL/SHM changed during export. Investigate before reuse."
}
Write-Host "Source DB/WAL/SHM hashes unchanged."
```

---

## ۶. آنچه این ابزار انجام نمی‌دهد

- هیچ QA approval
- هیچ پذیرش ProductKnowledge
- هیچ mutation روی Product Master / Evidence / Inventory / Recommendation
- هیچ Case/Customer export
- هیچ تکمیل خودکار گیت E2E مربوط به PR #504

---

## ۷. عیب‌یابی رایج در ویندوز

| پیام / وضعیت | اقدام |
|--------------|--------|
| `Source database must be an existing regular file, not a symlink` | مسیر واقعی فایل را بدهید، نه junction/symlink |
| `A SQLite rollback journal exists` | برنامهٔ استفاده‌کننده از DB را ببندید و journal را بررسی کنید |
| `Output already exists; choose a new path` | نام خروجی را با timestamp جدید بسازید |
| `Source DB/SQLite sidecars changed while copying` | در حین export، writer دیگری DB را تغییر داده؛ دوباره تلاش کنید |
| Exit code 2 | یک یا چند product_id از هفت شناسهٔ canonical در جدول Product نیست |
| Exit code 3 | schema ناقص یا FK violation؛ snapshot را برای debug نگه دارید |

---

**وضعیت سند:** راهنمای اجرایی read-only برای ابزار موجود؛ جایگزین قرارداد پذیرش محصول یا تصمیم Product Owner نیست.
