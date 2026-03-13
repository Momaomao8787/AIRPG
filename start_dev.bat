@echo off
setlocal
cd /d %~dp0

echo ==========================================
echo    AIRPG 整合式開發環境啟動
echo ==========================================

:: 1. 啟動後端 API (在新視窗中執行)
echo [1/2] 正在後台啟動後端伺服器...
start "AIRPG-Backend" cmd /c "cd server && run_server.bat"

:: 2. 啟動前端 Godot (預留未來連動位置)
echo [2/2] 正在檢查前端專案...

if exist "client" (
    echo [系統] 找到前端資料夾 (client)。
    echo [提示] 前端功能開發中... 未來將自動執行 Godot 引擎。
    :: 未來開發完畢後，取消下行註解並填入 Godot 執行檔路徑即可
    :: start "AIRPG-Frontend" "godot_engine_path.exe" --path client
) else (
    echo [系統] 目前 client 資料夾尚未建立。
)

echo.
echo ==========================================
echo [完成] 後端已啟動。
echo [請注意] 請檢查跳出的新視窗，確保後端沒有報錯。
echo ==========================================
pause
