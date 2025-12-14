@echo off
echo ===========================================
echo Resetting PrintFarm ERP Demo Data
echo ===========================================

echo.
echo This will DELETE:
echo  - Local Database (printfarm.db)
echo  - All uploaded files (app/uploads/*)
echo  - Local configuration (.env)
echo.
echo Press Ctrl+C to cancel, or any key to continue.
pause

echo.
echo Deleting database...
if exist "printfarm.db" del "printfarm.db"

echo.
echo Deleting uploads...
rem Navigate to app/uploads if it exists
if exist "app\uploads" (
    del /q "app\uploads\*.*"
    rem Optionally keep the directory, just wipe files
)

echo.
echo Deleting local configuration...
if exist ".env" del ".env"

echo.
echo Cleaning up pycache...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

echo.
echo ===========================================
echo DEMO RESET COMPLETE
echo ===========================================
echo You can now run demo_quickstart.bat to start fresh.
echo.
pause
