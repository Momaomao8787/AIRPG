@echo off
setlocal
cd /d %~dp0

echo ==========================================
echo    AIRPG Stop All Development Services
echo ==========================================

:: 1. Stop uvicorn (Backend Server)
echo [SYSTEM] Searching and terminating uvicorn processes...
taskkill /F /IM uvicorn.exe /T 2>nul
if %errorlevel% equ 0 (
    echo [OK] Backend server stopped successfully.
) else (
    echo [INFO] No running uvicorn server found.
)

:: 2. Stop Launcher (AIRPG-Launcher)
echo [SYSTEM] Terminating Launcher service...
taskkill /F /FI "WINDOWTITLE eq AIRPG-Launcher*" /T 2>nul
if %errorlevel% equ 0 (
    echo [OK] Launcher closed.
)

echo ==========================================
echo [DONE] All AIRPG related services are closed.
echo ==========================================
exit /b 0
