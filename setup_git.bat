@echo off
chcp 65001
cd /d E:\HBI

REM ====================================================
REM  این دو خط را با اطلاعات خودتان ویرایش کنید:
REM ====================================================
set GIT_USER_NAME=Vahid Maghsoudi
set GIT_USER_EMAIL=p09052100734@gmail.com
REM ====================================================

echo [1/5] Checking git...
git --version
if errorlevel 1 (
    echo.
    echo ERROR: git is not installed or not in PATH.
    echo Please install git first.
    pause
    exit /b 1
)

echo.
echo [2/5] Setting local git identity...
git config user.name "%GIT_USER_NAME%"
git config user.email "%GIT_USER_EMAIL%"
echo Identity set to: %GIT_USER_NAME% ^<%GIT_USER_EMAIL%^>

echo.
echo [3/5] Initializing repository...
if not exist .git (
    git init
    echo Repository initialized.
) else (
    echo .git already exists, skipping init.
)

echo.
echo [4/5] Staging all files...
git add -A
echo All files staged.

echo.
echo [5/5] Creating initial commit...
git commit -m "chore: initialize HBI memory structure and Source of Truth (Phase 7)"

echo.
echo ====================================================
echo DONE. Local repository is ready.
echo Next step: Box 3 (connect to GitHub and push).
echo ====================================================
pause