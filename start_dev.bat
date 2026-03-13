@echo off
setlocal
cd /d %~dp0

echo ==========================================
echo    AIRPG Control Center
echo ==========================================

:: --- 檢查 Python ---
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [錯誤] 找不到 Python，請先安裝 Python 3.10+。
    pause & exit /b 1
)

:: --- 確保 venv 存在 (供 Launcher 使用) ---
if not exist "server\venv\Scripts\python.exe" (
    echo [系統] 初次執行，正在建立虛擬環境...
    python -m venv server\venv
    call server\venv\Scripts\activate.bat
    python -m pip install -q -r server\requirements.txt
)

:: --- 啟動 Launcher 控制台 ---
echo [系統] 正在啟動 AIRPG Control Center...
start "AIRPG-Launcher" /min cmd /c "server\venv\Scripts\python.exe launcher\launcher_server.py"

:: --- 等待 Launcher 就緒 ---
echo [系統] 等待控制台準備就緒...
timeout /t 2 /nobreak >nul

:: --- 開啟瀏覽器 ---
echo [系統] 正在開啟控制台介面...
start "" http://localhost:8080

echo.
echo ==========================================
echo [完成] AIRPG Control Center 已開啟。
echo          http://localhost:8080
echo [提示] 請在介面中設定 AI 模型後啟動後端。
echo ==========================================
