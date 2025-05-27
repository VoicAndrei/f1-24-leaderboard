@echo off
REM F1 Leaderboard - RIG1 Timer Client Startup
echo Starting Timer Client for RIG1...

REM Change to the scripts directory
cd /d "%~dp0"

REM Run the timer client for RIG1
python rig_timer_client.py --rig-id RIG1

echo Timer client for RIG1 has stopped.
pause 