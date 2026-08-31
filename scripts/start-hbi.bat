@echo off
chcp 65001 >nul
setlocal EnableExtensions

REM ============================================================
REM  HBI — راه‌انداز یک‌کلیکی (ویندوز)
REM  این فایل را دابل‌کلیک کنید یا از میانبر دسکتاپ اجرا کنید.
REM ============================================================

REM پوشه ریشه پروژه = والد پوشه scripts
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "ROOT=%%~fI"

echo.
echo  ========================================
echo   گالری مقصودی / HBI — شروع سیستم
echo  ========================================
echo   مسیر پروژه: %ROOT%
echo.

if not exist "%ROOT%\app\main.py" (
  echo [خطا] فایل app\main.py پیدا نشد.
  echo مطمئن شوید این اسکریپت داخل پوشه hbi\scripts است.
  pause
  exit /b 1
)

if not exist "%ROOT%\frontend\package.json" (
  echo [خطا] پوشه frontend پیدا نشد.
  pause
  exit /b 1
)

where python >nul 2>&1
if errorlevel 1 (
  echo [خطا] Python در PATH نیست. Python 3 را نصب و به PATH اضافه کنید.
  pause
  exit /b 1
)

where npm >nul 2>&1
if errorlevel 1 (
  echo [خطا] npm پیدا نشد. Node.js LTS را نصب کنید: https://nodejs.org
  pause
  exit /b 1
)

REM نصب وابستگی فرانت در صورت نیاز
if not exist "%ROOT%\frontend\node_modules\" (
  echo [۱/۴] نصب وابستگی‌های Frontend ^(فقط بار اول^)...
  pushd "%ROOT%\frontend"
  call npm install
  if errorlevel 1 (
    echo [خطا] npm install ناموفق بود.
    popd
    pause
    exit /b 1
  )
  popd
) else (
  echo [۱/۴] Frontend آماده است ^(node_modules موجود^).
)

echo [۲/۴] روشن کردن Backend روی پورت 8000...
start "HBI-Backend" /D "%ROOT%" cmd /k "python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo [۳/۴] روشن کردن Frontend روی پورت 5173...
timeout /t 3 /nobreak >nul
start "HBI-Frontend" /D "%ROOT%\frontend" cmd /k "npm run dev -- --host 127.0.0.1 --port 5173"

echo [۴/۴] باز کردن Home در مرورگر...
timeout /t 5 /nobreak >nul
start "" "http://127.0.0.1:5173/"

echo.
echo  ========================================
echo   Home باید در مرورگر باز شده باشد.
echo   آدرس: http://127.0.0.1:5173/
echo   API:  http://127.0.0.1:8000/docs
echo.
echo   دو پنجره مشکی Backend و Frontend را نبندید
echo   تا وقتی با سیستم کار می‌کنید.
echo   برای توقف: آن دو پنجره را ببندید.
echo  ========================================
echo.
pause
