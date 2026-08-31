# ساخت میانبر روی دسکتاپ ویندوز برای start-hbi.bat
# یک‌بار اجرا کنید: راست‌کلیک → Run with PowerShell

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$Bat = Join-Path $Root "scripts\start-hbi.bat"

if (-not (Test-Path $Bat)) {
    Write-Host "start-hbi.bat پیدا نشد: $Bat" -ForegroundColor Red
    exit 1
}

$Desktop = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $Desktop "گالری مقصودی - HBI.lnk"

$Wsh = New-Object -ComObject WScript.Shell
$Sc = $Wsh.CreateShortcut($ShortcutPath)
$Sc.TargetPath = $Bat
$Sc.WorkingDirectory = $Root
$Sc.WindowStyle = 1
$Sc.Description = "راه‌اندازی Home پروژه HBI — گالری مقصودی"
# آیکون پیش‌فرض مرورگر/سیستم؛ در صورت داشتن .ico می‌توانید مسیر بدهید
$Sc.IconLocation = "%SystemRoot%\System32\shell32.dll,13"
$Sc.Save()

Write-Host ""
Write-Host "میانبر ساخته شد:" -ForegroundColor Green
Write-Host "  $ShortcutPath"
Write-Host ""
Write-Host "از این به بعد فقط روی آیکون دسکتاپ دابل‌کلیک کنید."
Write-Host ""
Read-Host "Enter برای خروج"
