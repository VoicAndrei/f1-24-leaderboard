@echo off
REM F1 Leaderboard - RIG2 Timer Client Startup
echo Starting Timer Client for RIG2...

REM Change to the scripts directory
cd /d "%~dp0"

REM Run the timer client for RIG2
python rig_timer_client.py --rig-id RIG2

echo Timer client for RIG2 has stopped.
pause 