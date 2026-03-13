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
