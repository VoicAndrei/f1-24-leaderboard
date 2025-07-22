@echo off
echo Starting F1 Leaderboard to Supabase Sync Service...
echo.

cd /d "%~dp0f1_leaderboard_app"

python services/supabase_sync.py

pause