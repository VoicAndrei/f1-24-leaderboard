@echo off
echo ==========================================
echo F1 Leaderboard - Network Configuration
echo Profile: MOBILE (Mobile/Event Network)
echo Rig: RIG1
echo ==========================================
echo.
echo Setting IP: 192.168.1.103
echo Gateway: 192.168.1.1
echo Subnet: 255.255.255.0
echo.

REM Get the network adapter name
for /f "tokens=1,2*" %%i in ('netsh interface show interface ^| findstr /C:"Connected"') do (
    set adapter_name=%%k
)

echo Configuring adapter: %adapter_name%
echo.

REM Set static IP
netsh interface ip set address name="%adapter_name%" static 192.168.1.103 255.255.255.0 192.168.1.1

REM Set DNS (Google's public DNS)
netsh interface ip set dns name="%adapter_name%" static 8.8.8.8
netsh interface ip add dns name="%adapter_name%" 8.8.4.4 index=2

echo.
echo ✅ Network configuration complete for RIG1!
echo Profile: MOBILE
echo IP: 192.168.1.103
echo Gateway: 192.168.1.1
echo.
echo The rig is now configured for: Mobile/Event Network
echo.
pause 