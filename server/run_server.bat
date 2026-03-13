@echo off
:: 強制進入腳本所在的資料夾，避免從外部呼叫時路徑出錯
cd /d %~dp0

echo ==========================================
echo    AIRPG 後端啟動服務 (FastAPI)
echo ==========================================

:: 1. 建立並檢查虛擬環境 (如果不存在)
if not exist venv (
    echo [系統] 正在建立虛擬環境...
    python -m venv venv
    if errorlevel 1 (
        echo [錯誤] 無法建立虛擬環境，請確認是否已安裝 Python。
        pause
        exit /b 1
    )
)

:: --- Ollama 環境檢查 ---
echo [系統] 正在檢查 Ollama 狀態...
where ollama >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 偵測不到 Ollama。
    echo [系統] 正在開啟下載頁面，請安裝後重新執行此腳本。
    start https://ollama.com/download
    pause
    exit /b 1
)

:: 檢查 Ollama 服務是否回應 (預設埠 11434)
powershell -Command "try { $r = Invoke-WebRequest -Uri http://127.0.0.1:11434/api/tags -UseBasicParsing -TimeoutSec 2; exit 0 } catch { exit 1 }"
if %errorlevel% neq 0 (
    echo [提醒] Ollama 服務尚未啟動，嘗試自動開啟中...
    start "" ollama
    echo [系統] 正在等待 Ollama 初始化 (約 10 秒)...
    timeout /t 10 /nobreak >nul
    
    :: 第二次檢查
    powershell -Command "try { $r = Invoke-WebRequest -Uri http://127.0.0.1:11434/api/tags -UseBasicParsing -TimeoutSec 2; exit 0 } catch { exit 1 }"
    if %errorlevel% neq 0 (
        echo [錯誤] 無法自動啟動 Ollama，請手動開啟 Ollama 應用程式後重新執行。
        pause
        exit /b 1
    )
    echo [完成] Ollama 服務已就緒。
)

:: 自動拉取必要模型 (已下載會自動跳過)
echo [系統] 正在同步 AI 模型 (llama3, nomic-embed-text)...
ollama pull llama3
ollama pull nomic-embed-text

:: 2. 啟動虛擬環境並同步套件
echo [系統] 正在同步環境套件 (已安裝會自動跳過)...
call venv\Scripts\activate.bat
:: 每次啟動都輕微檢查，確保開發過程中新增的套件能自動安裝
python -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [警告] 套件安裝或更新失敗，請檢查網路連線。
)

:: 3. 提示外部依賴
echo [提示] 請確保 Ollama 已啟動。
echo [提示] 需具備模型: llama3, nomic-embed-text
echo.

:: 4. 啟動伺服器
echo [系統] 正在開啟 API 服務 (http://127.0.0.1:8000)...
echo [提示] 看到 "Uvicorn running on..." 表示啟動成功。
echo [提示] 按下 Ctrl+C 即可停止服務。
uvicorn main:app --host 127.0.0.1 --port 8000 --reload

if errorlevel 1 (
    echo [錯誤] 伺服器異常終止。
    pause
    exit /b 1
)
