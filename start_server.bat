@echo off
echo Starting F1 Leaderboard Application Server...

REM Navigate to the directory where this script is located
cd /D "%~dp0"

REM Navigate into the application folder
cd f1_leaderboard_app

echo Launching Python server (backend/main.py)...
python backend/main.py

echo.
echo The server should now be running.
echo If the server started successfully, this window will remain open.
echo Close this window to stop the server. 