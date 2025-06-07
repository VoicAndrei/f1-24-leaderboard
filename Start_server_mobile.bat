@echo off
echo ========================================
echo F1 Leaderboard Server - MOBILE Network
echo ========================================
echo.
echo Network: 192.168.1.x (Mobile/Event)
echo Server IP: 192.168.1.100
echo.

cd /d "%~dp0"

REM Set network profile for this session
set NETWORK_PROFILE=MOBILE

echo Starting F1 Leaderboard Server (MOBILE Network - %NETWORK_PROFILE%)...
echo.
echo Admin Panel: http://192.168.1.100:8000/admin
echo Leaderboard: http://192.168.1.100:8000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Change to the f1_leaderboard_app directory so paths work correctly
cd f1_leaderboard_app

REM Start the server with mobile configuration
REM The main.py will read NETWORK_PROFILE environment variable
python backend/main.py

echo.
echo Server stopped.
pause 