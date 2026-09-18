@echo off
chcp 65001 >nul
setlocal EnableExtensions EnableDelayedExpansion

REM ============================================================
REM HBI — Single Entry Launcher
REM Desktop shortcut -> this file -> GitHub sync -> Home
REM ============================================================

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "ROOT=%%~fI"

echo.
echo  ========================================
echo   HBI — به‌روزرسانی و اجرای Home
echo  ========================================
echo   مسیر: %ROOT%
echo.

if not exist "%ROOT%\.git" (
  echo [خطا] مخزن Git در مسیر پروژه پیدا نشد.
  pause
  exit /b 1
)

where git >nul 2>&1
if errorlevel 1 (
  echo [خطا] Git در PATH پیدا نشد.
  pause
  exit /b 1
)

where python >nul 2>&1
if errorlevel 1 (
  echo [خطا] Python در PATH پیدا نشد.
  pause
  exit /b 1
)

where npm >nul 2>&1
if errorlevel 1 (
  echo [خطا] npm پیدا نشد.
  pause
  exit /b 1
)

REM ------------------------------------------------------------
REM 1) محافظت از تغییرات محلی
REM ------------------------------------------------------------
git -C "%ROOT%" diff --quiet
if errorlevel 1 (
  echo [توقف] تغییرات محلی ثبت‌نشده وجود دارد.
  echo ابتدا وضعیت Git را بررسی کنید.
  pause
  exit /b 1
)

git -C "%ROOT%" diff --cached --quiet
if errorlevel 1 (
  echo [توقف] تغییرات staged ثبت‌نشده وجود دارد.
  echo ابتدا وضعیت Git را بررسی کنید.
  pause
  exit /b 1
)

REM ------------------------------------------------------------
REM 2) دریافت آخرین وضعیت GitHub
REM ------------------------------------------------------------
echo [۱/۵] دریافت آخرین نسخه از GitHub...
git -C "%ROOT%" fetch origin --prune
if errorlevel 1 (
  echo [خطا] دریافت از GitHub ناموفق بود.
  pause
  exit /b 1
)

REM ------------------------------------------------------------
REM 3) انتخاب نسخه اجرا
REM    - اگر HEAD در master است: origin/master
REM    - در غیر این صورت branch جاری، در صورت وجود remote
REM    - برای detached HEAD، اولین remote branch حاوی HEAD
REM ------------------------------------------------------------
set "TARGET_REF="

git -C "%ROOT%" merge-base --is-ancestor HEAD origin/master
if not errorlevel 1 (
  set "TARGET_REF=origin/master"
  goto :sync
)

for /f "delims=" %%B in ('git -C "%ROOT%" symbolic-ref --short -q HEAD 2^>nul') do set "CURRENT_BRANCH=%%B"
if defined CURRENT_BRANCH (
  git -C "%ROOT%" show-ref --verify --quiet "refs/remotes/origin/!CURRENT_BRANCH!"
  if not errorlevel 1 set "TARGET_REF=origin/!CURRENT_BRANCH!"
)

if defined TARGET_REF goto :sync

for /f "delims=" %%B in ('git -C "%ROOT%" branch -r --contains HEAD 2^>nul ^| findstr /R /C:"origin/"') do (
  if not defined TARGET_REF set "TARGET_REF=%%B"
)

if not defined TARGET_REF (
  echo [خطا] نسخه قابل‌تشخیص برای همگام‌سازی پیدا نشد.
  pause
  exit /b 1
)

set "TARGET_REF=%TARGET_REF: =%"
 
:sync
echo [۲/۵] همگام‌سازی با %TARGET_REF%...
git -C "%ROOT%" checkout --detach "%TARGET_REF%"
if errorlevel 1 (
  echo [خطا] همگام‌سازی فایل‌های پروژه ناموفق بود.
  pause
  exit /b 1
)

REM ------------------------------------------------------------
REM 4) وابستگی Frontend
REM ------------------------------------------------------------
if not exist "%ROOT%\frontend\node_modules\" (
  echo [۳/۵] نصب وابستگی‌های Frontend...
  pushd "%ROOT%\frontend"
  call npm install --no-audit --no-fund
  if errorlevel 1 (
    popd
    echo [خطا] نصب وابستگی‌های Frontend ناموفق بود.
    pause
    exit /b 1
  )
  popd
) else (
  echo [۳/۵] وابستگی‌های Frontend آماده است.
)

REM ------------------------------------------------------------
REM 5) اجرای Backend + Frontend و انتظار برای آماده‌شدن واقعی
REM ------------------------------------------------------------
echo [۴/۵] اجرای Backend روی 8000...
start "HBI-Backend" /D "%ROOT%" cmd /k "python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo [۵/۵] اجرای Frontend روی 5173...
start "HBI-Frontend" /D "%ROOT%\frontend" cmd /k "npm run dev -- --host 127.0.0.1 --port 5173"

echo.
echo  در انتظار آماده‌شدن Home...

set "READY=0"
for /L %%N in (1,1,30) do (
  powershell -NoProfile -Command "try { Invoke-WebRequest -UseBasicParsing -TimeoutSec 1 http://127.0.0.1:5173/ ^| Out-Null; exit 0 } catch { exit 1 }" >nul 2>&1
  if not errorlevel 1 (
    set "READY=1"
    goto :open_home
  )
  timeout /t 1 /nobreak >nul
)

:open_home
if "%READY%"=="1" (
  echo Home آماده است.
  start "" "http://127.0.0.1:5173/"
) else (
  echo [خطا] Home در زمان مقرر آماده نشد.
  echo پنجره‌های Backend و Frontend را برای بررسی باز نگه دارید.
  pause
  exit /b 1
)

echo.
echo  ========================================
echo   HBI با موفقیت راه‌اندازی شد.
echo   نسخه اجرا: %TARGET_REF%
echo   Home: http://127.0.0.1:5173/
echo  ========================================
echo.
exit /b 0
