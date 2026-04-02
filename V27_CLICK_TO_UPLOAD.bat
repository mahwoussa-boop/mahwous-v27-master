@echo off
setlocal
cd /d "%~dp0"
echo 🦅 Mahwous V27 Rebirth - Ultimate Sync Tool (Force Mode)
echo --------------------------------------------------------

:: Check for Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed on your system!
    echo Please install Git from: https://git-scm.com/
    pause
    exit /b
)

echo [1/4] Initializing Repository...
git init
git remote remove origin >nul 2>&1
git remote add origin https://github.com/mahwoussa-boop/mahwous-v27-master.git

echo [2/4] Preparing Files...
git add .

echo [3/4] Recording Changes (Commit)...
git commit -m "🦅 V27 Rebirth: Final Stable Release"

echo [4/4] FORCE Pushing to GitHub...
git branch -M master
git push -f origin master

echo.
echo --------------------------------------------------------
echo ✅ DONE! Your code is now sync'd to GitHub.
echo Railway should start building your app in a few seconds.
echo --------------------------------------------------------
pause
