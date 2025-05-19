@echo off
REM Get the directory of the batch file
SET SCRIPT_DIR=%~dp0

REM Full path to the python script
SET PYTHON_SCRIPT="%SCRIPT_DIR%operator_timer_control.py"

echo Starting 10-minute timer for Rig 1...

REM Ensure python is in PATH or provide full path to python.exe
REM For example: C:\Python39\python.exe %PYTHON_SCRIPT% --quick10

python %PYTHON_SCRIPT% --quick10

REM The python script now has its own pause, so this might be redundant
REM if you want the window to close automatically after the script finishes.
REM If the python script closes itself too fast, you can add a pause here.

REM echo.
REM pause 