@echo off
chcp 65001
cd /d E:\HBI

echo ====================================================
echo HBI Cleanup and Push to GitHub
echo ====================================================

echo.
echo [1/6] Removing stray and temporary files...
if exist cd del cd && echo Removed: cd
if exist python del python && echo Removed: python
if exist type del type && echo Removed: type
if exist hbi_setup_memory.py del hbi_setup_memory.py && echo Removed: hbi_setup_memory.py
if exist create_reference_docs.py del create_reference_docs.py && echo Removed: create_reference_docs.py
if exist setup_git.bat del setup_git.bat && echo Removed: setup_git.bat
if exist setup_git_v2.bat del setup_git_v2.bat && echo Removed: setup_git_v2.bat

echo.
echo [2/6] Updating .gitignore...
(
echo.
echo # Temporary setup scripts
echo setup_git*.bat
echo hbi_setup_memory.py
echo create_reference_docs.py
echo.
echo # Stray files
echo cd
echo python
echo type
) >> .gitignore
echo .gitignore updated.

echo.
echo [3/6] Staging changes...
git add -A
echo All changes staged.

echo.
echo [4/6] Creating cleanup commit...
git commit -m "chore: cleanup temporary files and update .gitignore"
if errorlevel 1 (
    echo No changes to commit, continuing...
)

echo.
echo [5/6] Setting up GitHub remote...
git remote remove origin 2>nul
git remote add origin https://github.com/vahidmaghsoudi2/hbi.git
echo Remote set to: https://github.com/vahidmaghsoudi2/hbi.git

echo.
echo [6/6] Pushing to GitHub...
echo.
echo IMPORTANT: If prompted for credentials:
echo   - Username: vahidmaghsoudi2
echo   - Password: Use your Personal Access Token (NOT your account password)
echo.
echo If you don't have a Personal Access Token, press Ctrl+C now and I'll help you create one.
echo.
git push -u origin master

if errorlevel 1 (
    echo.
    echo ====================================================
    echo PUSH FAILED
    echo ====================================================
    echo Possible reasons:
    echo 1. Repository 'hbi' does not exist on GitHub
    echo 2. Personal Access Token is required but not provided
    echo 3. Repository name is different from 'hbi'
    echo.
    echo Please let me know what happened and I'll help fix it.
) else (
    echo.
    echo ====================================================
    echo SUCCESS! Repository is now on GitHub.
    echo ====================================================
    echo Visit: https://github.com/vahidmaghsoudi2/hbi
)

echo.
pause