@echo off
echo F1 Direct Timer Launcher
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

echo Starting Direct Timer Application for Rig 1...
echo.
echo This simpler approach does not use network communication.
echo Just use the buttons to control timers directly on this PC.
echo.

python direct_timer.py --rig 1
exit /b 0 