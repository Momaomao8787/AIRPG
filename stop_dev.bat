@echo off
setlocal
cd /d %~dp0

echo ==========================================
echo    AIRPG 停止所有開發服務
echo ==========================================

:: 1. 停止 uvicorn (後端伺服器)
echo [系統] 正在尋找並終止 uvicorn 進程...
taskkill /F /IM uvicorn.exe /T 2>nul
if %errorlevel% equ 0 (
    echo [完成] 已成功關閉後端伺服器。
) else (
    echo [提示] 找不到運行中的 uvicorn 伺服器。
)

:: 2. 停止 python (如果有的話，通常 uvicorn 就夠了)
:: 為了安全起見，我們只針對 python，但不強制殺掉避免影響其他程式
:: 如果你確定要強力清除，可以取消下面這行註解
:: taskkill /F /IM python.exe /T 2>nul

echo ==========================================
echo [結束] 所有 AIRPG 相關服務已嘗試關機。
echo ==========================================
pause
