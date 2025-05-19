@echo off
echo F1 Timer Connection Test
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

echo This test will check if your operator PC can connect to the rig PC.
echo.
set /p IP_ADDRESS=Enter the rig PC's IP address (e.g., 192.168.0.204): 

echo.
echo Testing connection to %IP_ADDRESS% on port 5678...
echo.

python port_test_client.py %IP_ADDRESS%
exit /b %ERRORLEVEL% 