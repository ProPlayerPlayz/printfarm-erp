@echo off
echo ========================================
echo  PrintFarm ERP - Push Changes to GitHub
echo ========================================
echo.
echo This script will add all new files, commit them, and push to GitHub.
echo.

:: Check status
git status

echo.
set /p msg="Enter a commit message (e.g., 'Implemented Printer Management and Gallery'): "

if "%msg%"=="" set msg=Update from Antigravity session

echo.
echo Adding files...
git add .

echo.
echo Committing...
git commit -m "%msg%"

echo.
echo Pushing to origin main...
git push origin main

echo.
if %errorlevel% neq 0 (
    echo [ERROR] Push failed. You might need to authenticate or pull first.
    pause
    exit /b %errorlevel%
)

echo [SUCCESS] Changes pushed to GitHub!
echo Now you can go to your Raspberry Pi and run:
echo    cd printfarm-erp
echo    git pull origin main
echo.
pause
