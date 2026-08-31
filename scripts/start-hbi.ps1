# HBI — راه‌انداز یک‌کلیکی (PowerShell)
# اجرا: راست‌کلیک → Run with PowerShell  یا از start-hbi.bat

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " گالری مقصودی / HBI — شروع سیستم" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "مسیر: $Root"
Write-Host ""

if (-not (Test-Path (Join-Path $Root "app\main.py"))) {
    Write-Host "[خطا] app\main.py پیدا نشد." -ForegroundColor Red
    Read-Host "Enter برای خروج"
    exit 1
}
if (-not (Test-Path (Join-Path $Root "frontend\package.json"))) {
    Write-Host "[خطا] frontend پیدا نشد." -ForegroundColor Red
    Read-Host "Enter برای خروج"
    exit 1
}

function Test-Cmd($name) {
    return [bool](Get-Command $name -ErrorAction SilentlyContinue)
}

if (-not (Test-Cmd "python")) {
    Write-Host "[خطا] Python در PATH نیست." -ForegroundColor Red
    Read-Host "Enter برای خروج"
    exit 1
}
if (-not (Test-Cmd "npm")) {
    Write-Host "[خطا] npm پیدا نشد. Node.js LTS نصب کنید." -ForegroundColor Red
    Read-Host "Enter برای خروج"
    exit 1
}

$nodeModules = Join-Path $Root "frontend\node_modules"
if (-not (Test-Path $nodeModules)) {
    Write-Host "[1/4] npm install (بار اول)..." -ForegroundColor Yellow
    Push-Location (Join-Path $Root "frontend")
    npm install
    if ($LASTEXITCODE -ne 0) { Pop-Location; Read-Host "خطا"; exit 1 }
    Pop-Location
} else {
    Write-Host "[1/4] Frontend آماده است." -ForegroundColor Cyan
}

Write-Host "[2/4] Backend :8000 ..." -ForegroundColor Cyan
Start-Process -FilePath "cmd.exe" -ArgumentList "/k", "python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload" -WorkingDirectory $Root -WindowStyle Normal

Start-Sleep -Seconds 3

Write-Host "[3/4] Frontend :5173 ..." -ForegroundColor Cyan
Start-Process -FilePath "cmd.exe" -ArgumentList "/k", "npm run dev -- --host 127.0.0.1 --port 5173" -WorkingDirectory (Join-Path $Root "frontend") -WindowStyle Normal

Start-Sleep -Seconds 5

Write-Host "[4/4] باز کردن مرورگر..." -ForegroundColor Cyan
Start-Process "http://127.0.0.1:5173/"

Write-Host ""
Write-Host "Home: http://127.0.0.1:5173/" -ForegroundColor Green
Write-Host "API Docs: http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host "دو پنجره Backend/Frontend را باز نگه دارید." -ForegroundColor Yellow
Write-Host ""
Read-Host "Enter برای بستن این پنجره (سرویس‌ها می‌مانند)"
