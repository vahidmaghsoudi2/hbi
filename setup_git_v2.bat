@echo off
chcp 65001
cd /d E:\HBI

REM ====================================================
REM  این دو خط را با اطلاعات خودتان ویرایش کنید:
REM ====================================================
set GIT_USER_NAME=Vahid Maghsoudi
set GIT_USER_EMAIL=p09052100734@gmail.com
REM ====================================================

echo [1/6] Checking git...
git --version
if errorlevel 1 (
    echo ERROR: git not found.
    pause
    exit /b 1
)

echo.
echo [2/6] Removing incomplete .git from previous attempt...
if exist .git (
    rmdir /s /q .git
    echo Old .git removed.
) else (
    echo No old .git found.
)

echo.
echo [3/6] Initializing repository...
git init
if errorlevel 1 (
    echo ERROR: git init failed.
    pause
    exit /b 1
)

echo.
echo [4/6] Setting local git identity...
git config user.name "%GIT_USER_NAME%"
git config user.email "%GIT_USER_EMAIL%"
echo Identity set to: %GIT_USER_NAME% ^<%GIT_USER_EMAIL%^>

echo.
echo [5/6] Staging all files...
git add -A
echo All files staged.

echo.
echo [6/6] Creating initial commit...
git commit -m "chore: initialize HBI memory structure and Source of Truth (Phase 7)"

echo.
echo ====================================================
echo DONE. Local repository is ready.
echo Next step: Box 3 (connect to GitHub and push).
echo ====================================================
pause