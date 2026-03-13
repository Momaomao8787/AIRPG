@echo off
setlocal
cd /d "%~dp0"

REM ------------------------------------------
REM    AIRPG Control Center Startup
REM ------------------------------------------

REM 1. Check Python
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.10+.
    pause
    exit /b 1
)

REM 2. Ensure venv exists
if not exist "server\venv\Scripts\python.exe" (
    echo [SYSTEM] First run detected. Creating virtual environment
    python -m venv server\venv
    if errorlevel 1 (
        echo [ERROR] Failed to create venv.
        pause
        exit /b 1
    )
    echo [SYSTEM] Installing dependencies
    "server\venv\Scripts\python.exe" -m pip install -r server\requirements.txt
)

REM 3. Kill existing launcher if any
taskkill /F /FI "WINDOWTITLE eq AIRPG-Launcher*" /T >nul 2>&1

REM 4. Start Launcher
echo [SYSTEM] Starting AIRPG Control Center
start "AIRPG-Launcher" "server\venv\Scripts\python.exe" launcher\launcher_server.py

REM 5. Wait for readiness
echo [SYSTEM] Waiting for console to be ready 8s
timeout /t 8 /nobreak >nul

REM 6. Open Browser
echo [SYSTEM] Opening dashboard
start "" "http://localhost:8080"

echo [OK] AIRPG Control Center is running at http://localhost:8080.
echo.
pause
