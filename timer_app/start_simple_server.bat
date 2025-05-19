@echo off
echo Simple F1 Simulator Timer Server
echo.

REM Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Check if dependencies are installed
pip show pyautogui >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing pyautogui...
    pip install pyautogui
    if %ERRORLEVEL% NEQ 0 (
        echo Error: Failed to install pyautogui.
        pause
        exit /b 1
    )
)

echo Starting Simplified Timer Server on Rig 1...
echo This version uses a simpler networking approach that might work better.
echo.

python timer_server_simple.py --rig 1 --port 5678
pause 