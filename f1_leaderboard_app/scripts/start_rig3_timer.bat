@echo off
REM F1 Leaderboard - RIG3 Timer Client Startup
echo Starting Timer Client for RIG3...

REM Change to the scripts directory
cd /d "%~dp0"

REM Run the timer client for RIG3
python rig_timer_client.py --rig-id RIG3

echo Timer client for RIG3 has stopped.
pause 