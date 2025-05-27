@echo off
REM F1 Leaderboard - RIG4 Timer Client Startup
echo Starting Timer Client for RIG4...

REM Change to the scripts directory
cd /d "%~dp0"

REM Run the timer client for RIG4
python rig_timer_client.py --rig-id RIG4

echo Timer client for RIG4 has stopped.
pause 