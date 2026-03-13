@echo off
setlocal
cd /d "%~dp0"

REM ==========================================
REM    AIRPG Backend Service (FastAPI)
REM =================-------------------------

REM 1. Check/Create Environment
if not exist "venv" (
    echo [SYSTEM] Creating virtual environment
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create venv. Please install Python.
        pause
        exit /b 1
    )
)

REM --- Ollama Check ---
echo [SYSTEM] Checking Ollama status
where ollama >nul 2>&1
if errorlevel 1 (
    echo [WARN] Ollama not found.
    echo [SYSTEM] Opening download page
    start https://ollama.com/download
    pause
    exit /b 1
)

REM Check if Ollama service is responsive
powershell -Command "try { $r = Invoke-WebRequest -Uri http://127.0.0.1:11434/api/tags -UseBasicParsing -TimeoutSec 2; exit 0 } catch { exit 1 }"
if errorlevel 1 (
    echo [INFO] Ollama service not running, attempting background start
    REM Start ollama without showing a console window if possible
    start /min ollama serve
    echo [SYSTEM] Waiting for Ollama initialization 10s
    timeout /t 10 /nobreak >nul
    
    REM Second check
    powershell -Command "try { $r = Invoke-WebRequest -Uri http://127.0.0.1:11434/api/tags -UseBasicParsing -TimeoutSec 2; exit 0 } catch { exit 1 }"
    if errorlevel 1 (
        echo [ERROR] Failed to start Ollama. Please start it manually.
        pause
        exit /b 1
    )
    echo [DONE] Ollama service is ready.
)

REM Smart Model Sync (Only pull if missing)
echo [SYSTEM] Checking AI models
ollama list | findstr "llama3" >nul
if errorlevel 1 (
    echo [SYSTEM] Pulling llama3...
    ollama pull llama3
) else (
    echo [OK] llama3 exists.
)

ollama list | findstr "nomic-embed-text" >nul
if errorlevel 1 (
    echo [SYSTEM] Pulling nomic-embed-text...
    ollama pull nomic-embed-text
) else (
    echo [OK] nomic-embed-text exists.
)

REM 2. Activate venv and sync dependencies
echo [SYSTEM] Syncing environment packages
call "venv\Scripts\activate.bat"
python -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [WARN] Package update failed.
)

REM 3. Startup
echo [SYSTEM] Opening API service http://127.0.0.1:8000
echo [INFO] Ready when Uvicorn running on appears.
echo [INFO] Press Ctrl+C to stop.
uvicorn main:app --host 127.0.0.1 --port 8000 --reload

if errorlevel 1 (
    echo [ERROR] Server terminated abnormally.
    pause
    exit /b 1
)
