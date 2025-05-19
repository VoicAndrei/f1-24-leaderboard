@echo off
echo F1 Simulator Timer Application
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

REM Check if pyautogui is installed
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

echo Starting the F1 Simulator Timer Launcher...
python timer_launcher.py
exit /b 0 