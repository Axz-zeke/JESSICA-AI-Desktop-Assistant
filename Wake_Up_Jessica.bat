@echo off
title Wake Up Jessica - 1-Click Recovery & Mission Control
cd /d "E:\Documents\GitHub\JESSICA"

rem ============================================================
rem PERMANENT E-DRIVE STORAGE & CACHE ROUTING (EMERGENCY C-DRIVE LOCK)
rem ============================================================
set "CACHE_VAULT=E:\GitHub\JESSICA_STORAGE\cache"
set "HF_HOME=%CACHE_VAULT%\huggingface"
set "HUGGINGFACE_HUB_CACHE=%CACHE_VAULT%\huggingface\hub"
set "TORCH_HOME=%CACHE_VAULT%\torch"
set "PIP_CACHE_DIR=%CACHE_VAULT%\pip"
set "TEMP=%CACHE_VAULT%\temp"
set "TMP=%CACHE_VAULT%\temp"
set "ULTRALYTICS_CONFIG_DIR=%CACHE_VAULT%\ultralytics"
if not exist "%TEMP%" mkdir "%TEMP%"
rem ============================================================

echo ============================================================
echo           WAKE UP JESSICA - 1-CLICK SYSTEM RESTORE
echo ============================================================
echo [*] Terminating any running training tasks or zombie processes...

for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo [*] Freeing port 8000 (PID %%a)...
    taskkill /F /PID %%a >nul 2>&1
)

echo [*] Checking local Python environment...
if exist "venv\Scripts\python.exe" (
    set "PYTHON_EXE=venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python.exe"
)

echo [*] Launching clean detached Jessica Mission Control Server...
powershell -Command "Start-Process -FilePath '%PYTHON_EXE%' -ArgumentList 'run_server.py' -WorkingDirectory 'E:\Documents\GitHub\JESSICA' -WindowStyle Hidden"

echo [*] Waiting for Jessica Sovereign Cortex to initialize (5s)...
timeout /t 5 /nobreak >nul

echo [*] Launching Mission Control UI with E: Drive Cache Lock...
start msedge --app="http://127.0.0.1:8000" --disk-cache-dir="E:\GitHub\JESSICA_STORAGE\cache\browser_cache" --user-data-dir="E:\GitHub\JESSICA_STORAGE\cache\browser_profile" --window-size=1440,900

echo ============================================================
echo   [+] Jessica is awake, fully restored, and ready for you!
echo ============================================================
timeout /t 3 /nobreak >nul
exit /b

