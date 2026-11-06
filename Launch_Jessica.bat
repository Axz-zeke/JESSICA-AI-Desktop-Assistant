@echo off
title Jessica Sovereign Mission Control
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
echo         JESSICA SOVEREIGN AI - 1-CLICK LAUNCHER
echo ============================================================
echo [*] Cleaning up any stale port-8000 processes...

for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo [*] Terminating zombie process PID %%a on port 8000...
    taskkill /F /PID %%a >nul 2>&1
)

echo [*] Checking local environment and Python virtual environment...

if exist "venv\Scripts\python.exe" (
    set "PYTHON_EXE=venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python.exe"
)

echo [*] Launching Jessica Mission Control Native Desktop Client...
"%PYTHON_EXE%" desktop_app\launch_desktop.py

echo [+] Jessica is running. This launcher will close in 3 seconds.
timeout /t 3 /nobreak >nul
exit /b

