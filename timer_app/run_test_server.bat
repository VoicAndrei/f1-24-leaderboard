@echo off
echo F1 Timer Connection Test Server
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

echo Starting test server on port 5678...
echo This will help check if your network connection is working.
echo.
echo Keep this window open and run the test_connection.bat on the operator PC.
echo.

python port_test_server.py
pause 