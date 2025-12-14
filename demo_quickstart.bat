@echo off
echo ===========================================
echo Setting up PrintFarm ERP Demo (Local Mode)
echo ===========================================

cd /d "%~dp0"

echo.
echo [1/6] Creating local .env configuration (Using SQLite)...
echo SECRET_KEY=demo-local-key > .env
echo FLASK_APP=wsgi.py >> .env
echo FLASK_DEBUG=1 >> .env
rem Using SQLite for zero-config local demo
echo DATABASE_URL=sqlite:///printfarm.db >> .env

echo.
echo [2/6] Installing dependencies (this may take a minute)...
pip install -r requirements.txt > nul
if %errorlevel% neq 0 (
    echo Error installing dependencies. Please ensure Python and Pip are installed.
    pause
    exit /b
)

echo.
echo [3/6] Initializing Database...
python scripts/init_db.py

echo.
echo [4/6] Seeding Default Data...
python scripts/seed_demo_data.py

echo.
echo [5/6] Creating Admin User...
rem Creates admin / password
python scripts/create_admin.py "Local Admin" "admin@example.com" "password"

echo.
echo ===========================================
echo DEMO READY!
echo ===========================================
echo.
echo Opening browser...
start http://127.0.0.1:5000/
echo.
echo Starting Server...
echo Use Ctrl+C to stop.
echo.
echo CREDENTIALS:
echo Admin: admin@example.com / password
echo Customer: customer@demo.com / password
echo Operator: operator@demo.com / password
echo.

flask run

pause
