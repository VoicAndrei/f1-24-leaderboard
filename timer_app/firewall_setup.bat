@echo off
echo F1 Timer - Windows Firewall Setup
echo.
echo This script will create firewall rules to allow communication between the timer server and clients.
echo It must be run with Administrator privileges on the rig PC.
echo.

REM Check for Administrator privileges
NET SESSION >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: This script requires Administrator privileges.
    echo Please right-click on this batch file and select "Run as administrator".
    echo.
    pause
    exit /b 1
)

echo Creating firewall rules...

REM Delete existing rules if they exist (to avoid duplicates)
netsh advfirewall firewall delete rule name="F1 Timer Server" >nul 2>&1

REM Create inbound rule for port 8080
netsh advfirewall firewall add rule name="F1 Timer Server" dir=in action=allow protocol=TCP localport=8080 profile=any

echo.
echo Firewall rules created successfully!
echo.
echo Please run start_timer_server.bat with the following command on the rig PC:
echo   start_timer_server.bat --port 8080
echo.

pause 