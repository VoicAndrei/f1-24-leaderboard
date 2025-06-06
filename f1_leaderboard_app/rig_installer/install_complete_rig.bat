@echo off
echo ========================================
echo F1 Leaderboard - Complete Rig Installer
echo ========================================
echo.
echo This installer will set up BOTH:
echo 1. Timer Client (session time limits)
echo 2. Telemetry Listener (lap time capture)
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo This installer needs to run as Administrator.
    echo Please right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo Running as Administrator - Good!
echo.

REM Get the directory where this batch file is located
set INSTALLER_DIR=%~dp0
set INSTALL_PATH=C:\F1LeaderboardRig

echo Creating installation directory...
mkdir "%INSTALL_PATH%" 2>nul

REM Copy all files
echo Copying F1 Leaderboard client files...
copy "%INSTALLER_DIR%rig_timer_client.py" "%INSTALL_PATH%\" >nul
copy "%INSTALLER_DIR%rig_listener.py" "%INSTALL_PATH%\" >nul
copy "%INSTALLER_DIR%app_config.py" "%INSTALL_PATH%\" >nul
copy "%INSTALLER_DIR%requirements_complete.txt" "%INSTALL_PATH%\" >nul
copy "%INSTALLER_DIR%start_rig_complete.bat" "%INSTALL_PATH%\" >nul

REM Check for Python installation
echo Checking for Python installation...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo.
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    echo After installing Python, run this installer again.
    pause
    exit /b 1
)

echo Python found - Good!
python --version

REM Install required packages
echo.
echo Installing required Python packages...
cd /d "%INSTALL_PATH%"
python -m pip install --upgrade pip
python -m pip install -r requirements_complete.txt

if %errorLevel% neq 0 (
    echo.
    echo Error installing Python packages.
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)

REM Check for F1 telemetry repository
echo.
echo ========================================
echo F1 TELEMETRY REPOSITORY CHECK
echo ========================================
echo.
echo Checking for F1 2024 telemetry repository...

REM Check multiple possible locations
set TELEMETRY_FOUND=false
if exist "C:\Users\landg\Desktop\f1-24-app\f1-24-telemetry-application" (
    echo F1 telemetry repository found at: C:\Users\landg\Desktop\f1-24-app\f1-24-telemetry-application
    set TELEMETRY_FOUND=true
)
if exist "C:\F1Telemetry\f1-24-telemetry-application" (
    echo F1 telemetry repository found at: C:\F1Telemetry\f1-24-telemetry-application
    set TELEMETRY_FOUND=true
)
if exist "C:\f1-24-telemetry-application" (
    echo F1 telemetry repository found at: C:\f1-24-telemetry-application
    set TELEMETRY_FOUND=true
)
if exist "%USERPROFILE%\Desktop\f1-24-telemetry-application" (
    echo F1 telemetry repository found at: %USERPROFILE%\Desktop\f1-24-telemetry-application
    set TELEMETRY_FOUND=true
)
if exist "%USERPROFILE%\Documents\f1-24-telemetry-application" (
    echo F1 telemetry repository found at: %USERPROFILE%\Documents\f1-24-telemetry-application
    set TELEMETRY_FOUND=true
)
REM Check relative to installer location
if exist "%INSTALLER_DIR%..\f1-24-telemetry-application" (
    echo F1 telemetry repository found at: %INSTALLER_DIR%..\f1-24-telemetry-application
    set TELEMETRY_FOUND=true
)

if "%TELEMETRY_FOUND%"=="true" (
    echo F1 telemetry repository found - Good!
) else (
    echo WARNING: F1 telemetry repository not found in common locations.
    echo.
    echo For lap time capture to work, you need the F1 telemetry repository.
    echo.
    echo OPTION 1 - Auto-download ^(Recommended^):
    echo The installer can download it for you automatically.
    echo.
    echo OPTION 2 - Manual download:
    echo 1. Go to https://github.com/Fredrik2002/f1-24-telemetry-application
    echo 2. Click "Code" ^> "Download ZIP"
    echo 3. Extract to C:\f1-24-telemetry-application
    echo.
    echo OPTION 3 - Timer only:
    echo Continue without telemetry - timer will work but no lap times captured
    echo.
    set /p AUTO_DOWNLOAD="Auto-download F1 telemetry repository now? (y/n): "
    if /i "%AUTO_DOWNLOAD%"=="y" (
        echo.
        echo Downloading F1 telemetry repository...
        echo This may take a few minutes depending on your internet connection.
        echo.
        
        REM Download using PowerShell
        powershell -Command "& {Invoke-WebRequest -Uri 'https://github.com/Fredrik2002/f1-24-telemetry-application/archive/refs/heads/main.zip' -OutFile 'f1-telemetry.zip'}"
        
        if exist "f1-telemetry.zip" (
            echo Download completed. Extracting...
            powershell -Command "& {Expand-Archive -Path 'f1-telemetry.zip' -DestinationPath '.' -Force}"
            
            if exist "f1-24-telemetry-application-main" (
                move "f1-24-telemetry-application-main" "C:\f1-24-telemetry-application"
                del "f1-telemetry.zip"
                echo F1 telemetry repository installed successfully!
                set TELEMETRY_FOUND=true
            ) else (
                echo Error: Failed to extract F1 telemetry repository.
                del "f1-telemetry.zip" 2>nul
            )
        ) else (
            echo Error: Failed to download F1 telemetry repository.
            echo Please check your internet connection and try manual download.
        )
    )
    
    if "%TELEMETRY_FOUND%"=="false" (
        set /p CONTINUE="Continue installation without telemetry? (y/n): "
        if /i not "%CONTINUE%"=="y" (
            echo Installation cancelled. Please set up the telemetry repository first.
            pause
            exit /b 1
        )
        echo.
        echo Continuing with timer-only installation...
    )
)

REM Get the RIG ID from user input
echo.
echo ========================================
echo RIG CONFIGURATION
echo ========================================
echo.
echo Available RIG IDs: RIG1, RIG2, RIG3, RIG4
echo.
set /p RIG_ID="Enter the RIG ID for this computer (e.g., RIG1): "

REM Validate RIG ID
if /i "%RIG_ID%"=="RIG1" goto :valid_rig
if /i "%RIG_ID%"=="RIG2" goto :valid_rig
if /i "%RIG_ID%"=="RIG3" goto :valid_rig
if /i "%RIG_ID%"=="RIG4" goto :valid_rig

echo Invalid RIG ID. Please use RIG1, RIG2, RIG3, or RIG4
pause
exit /b 1

:valid_rig
echo RIG ID set to: %RIG_ID%

REM Set static IP based on RIG ID
echo.
echo ========================================
echo NETWORK CONFIGURATION
echo ========================================
echo.
if /i "%RIG_ID%"=="RIG1" set SHOP_IP=192.168.0.210
if /i "%RIG_ID%"=="RIG1" set MOBILE_IP=192.168.1.103
if /i "%RIG_ID%"=="RIG2" set SHOP_IP=192.168.0.211
if /i "%RIG_ID%"=="RIG2" set MOBILE_IP=192.168.1.104
if /i "%RIG_ID%"=="RIG3" set SHOP_IP=192.168.0.212
if /i "%RIG_ID%"=="RIG3" set MOBILE_IP=192.168.1.105
if /i "%RIG_ID%"=="RIG4" set SHOP_IP=192.168.0.213
if /i "%RIG_ID%"=="RIG4" set MOBILE_IP=192.168.1.106

echo This rig (%RIG_ID%) should use these static IP addresses:
echo.
echo SHOP Network (192.168.0.x):
echo   IP: %SHOP_IP%
echo   Subnet: 255.255.255.0
echo   Gateway: 192.168.0.1
echo.
echo MOBILE Network (192.168.1.x):
echo   IP: %MOBILE_IP%
echo   Subnet: 255.255.255.0
echo   Gateway: 192.168.1.1
echo.
echo IMPORTANT: Set the appropriate IP address for your current network.
echo You can switch between networks by changing the IP in Windows settings.
echo.
echo Instructions:
echo 1. Go to Network Settings
echo 2. Change adapter options
echo 3. Right-click your network connection - Properties
echo 4. Select IPv4 - Properties
echo 5. Use the following IP address (choose based on your network):
echo    - For SHOP: %SHOP_IP%
echo    - For MOBILE: %MOBILE_IP%
echo 6. Set appropriate subnet mask and gateway (see above)
echo 7. Set DNS: 8.8.8.8
echo.
set /p CONTINUE="Have you set the appropriate static IP for this rig? (y/n): "
if /i not "%CONTINUE%"=="y" (
    echo Please set the static IP first, then run this installer again.
    pause
    exit /b 1
)

REM F1 2024 telemetry configuration reminder
echo.
echo ========================================
echo F1 2024 GAME CONFIGURATION
echo ========================================
echo.
echo IMPORTANT: Configure F1 2024 telemetry settings:
echo 1. Start F1 2024 game
echo 2. Go to Settings ^> Telemetry Settings
echo 3. Set UDP Telemetry: ON
echo 4. Set UDP Broadcast Mode: ON
echo 5. Set UDP Port: 20777
echo 6. Set UDP Send Rate: 60Hz (recommended)
echo.
echo This must be done for lap times to be captured!
echo.
pause

REM Create the complete startup script
echo.
echo Creating startup scripts for %RIG_ID%...

REM Create SHOP network startup script
echo Creating SHOP network startup script...
(
echo @echo off
echo REM F1 Leaderboard Complete System - %RIG_ID% - SHOP Network
echo echo ========================================
echo echo F1 Leaderboard System - %RIG_ID% - SHOP
echo echo ========================================
echo echo.
echo echo Network: 192.168.0.x ^(Shop/Home^)
echo echo Server: 192.168.0.224:8000
echo echo.
echo echo Starting both Timer Client and Telemetry Listener...
echo echo.
echo echo Timer: Receives timer commands from operator
echo echo Telemetry: Captures lap times from F1 2024
echo echo.
echo echo IMPORTANT:
echo echo - Keep this window open ^(you can minimize it^)
echo echo - Make sure F1 2024 telemetry is configured
echo echo - Both systems will start automatically
echo echo.
echo cd /d "%%~dp0"
echo.
echo REM Start both components simultaneously for SHOP network
echo start "Timer Client - %RIG_ID% - SHOP" python rig_timer_client.py --rig-id %RIG_ID%
echo start "Telemetry Listener - %RIG_ID% - SHOP" python rig_listener.py --rig-id %RIG_ID% --api-host 192.168.0.224 --api-port 8000
echo.
echo echo Both F1 Leaderboard components are now running:
echo echo - Timer Client: Controls session time limits
echo echo - Telemetry Listener: Captures lap times from F1 2024
echo echo - Network: SHOP ^(192.168.0.x^)
echo echo.
echo echo You can close this window. The other windows can be minimized.
echo echo.
echo pause
) > "%INSTALL_PATH%\start_shop_%RIG_ID%.bat"

REM Create MOBILE network startup script
echo Creating MOBILE network startup script...
(
echo @echo off
echo REM F1 Leaderboard Complete System - %RIG_ID% - MOBILE Network
echo echo ========================================
echo echo F1 Leaderboard System - %RIG_ID% - MOBILE
echo echo ========================================
echo echo.
echo echo Network: 192.168.1.x ^(Mobile/Event^)
echo echo Server: 192.168.1.100:8000
echo echo.
echo echo Starting both Timer Client and Telemetry Listener...
echo echo.
echo echo Timer: Receives timer commands from operator
echo echo Telemetry: Captures lap times from F1 2024
echo echo.
echo echo IMPORTANT:
echo echo - Keep this window open ^(you can minimize it^)
echo echo - Make sure F1 2024 telemetry is configured
echo echo - Both systems will start automatically
echo echo.
echo cd /d "%%~dp0"
echo.
echo REM Start both components simultaneously for MOBILE network
echo start "Timer Client - %RIG_ID% - MOBILE" python rig_timer_client.py --rig-id %RIG_ID%
echo start "Telemetry Listener - %RIG_ID% - MOBILE" python rig_listener.py --rig-id %RIG_ID% --api-host 192.168.1.100 --api-port 8000
echo.
echo echo Both F1 Leaderboard components are now running:
echo echo - Timer Client: Controls session time limits
echo echo - Telemetry Listener: Captures lap times from F1 2024
echo echo - Network: MOBILE ^(192.168.1.x^)
echo echo.
echo echo You can close this window. The other windows can be minimized.
echo echo.
echo pause
) > "%INSTALL_PATH%\start_mobile_%RIG_ID%.bat"

REM Create desktop shortcuts for both networks
echo Creating desktop shortcuts...
set DESKTOP=%USERPROFILE%\Desktop

REM SHOP network shortcut
(
echo @echo off
echo cd /d "%INSTALL_PATH%"
echo start "" "%INSTALL_PATH%\start_shop_%RIG_ID%.bat"
) > "%DESKTOP%\Start F1 System %RIG_ID% - SHOP.bat"

REM MOBILE network shortcut
(
echo @echo off
echo cd /d "%INSTALL_PATH%"
echo start "" "%INSTALL_PATH%\start_mobile_%RIG_ID%.bat"
) > "%DESKTOP%\Start F1 System %RIG_ID% - MOBILE.bat"

REM Test the installation
echo.
echo ========================================
echo TESTING INSTALLATION
echo ========================================
echo.
echo Testing timer client...
cd /d "%INSTALL_PATH%"
python rig_timer_client.py --rig-id %RIG_ID% --help >nul 2>&1
if %errorLevel% neq 0 (
    echo Error: Timer client test failed.
    echo Please check the installation and try again.
    pause
    exit /b 1
)

echo Testing telemetry listener...
python rig_listener.py --rig-id %RIG_ID% --help >nul 2>&1
if %errorLevel% neq 0 (
    echo Error: Telemetry listener test failed.
    echo This might be due to missing F1 telemetry repository.
    echo The timer will still work, but lap times won't be captured.
    echo.
    set /p CONTINUE="Continue anyway? (y/n): "
    if /i not "%CONTINUE%"=="y" (
        pause
        exit /b 1
    )
) else (
    echo All tests successful!
)

REM Success message
echo.
echo ========================================
echo INSTALLATION COMPLETE!
echo ========================================
echo.
echo Installation Summary:
echo - RIG ID: %RIG_ID%
echo - Static IP should be: %SHOP_IP% and %MOBILE_IP%
echo - Installation path: %INSTALL_PATH%
echo - Desktop shortcuts: "Start F1 System %RIG_ID% - SHOP" and "Start F1 System %RIG_ID% - MOBILE"
echo.
echo COMPONENTS INSTALLED:
echo 1. Timer Client - Session time limits and auto-pause
echo 2. Telemetry Listener - Lap time capture for leaderboard
echo.
echo TO START THE COMPLETE SYSTEM:
echo 1. Double-click "Start F1 System %RIG_ID% - SHOP" or "Start F1 System %RIG_ID% - MOBILE" on desktop
echo 2. Two command windows will open (can be minimized)
echo 3. The operator can now control this rig from admin panel
echo 4. Lap times will automatically appear on the leaderboard
echo.
echo TROUBLESHOOTING:
echo - Verify static IP: %SHOP_IP% and %MOBILE_IP%
echo - Configure F1 2024 telemetry settings
echo - Allow Python through Windows Firewall
echo - Operator PC should be at 192.168.0.224:8000 for SHOP network
echo - Operator PC should be at 192.168.1.100:8000 for MOBILE network
echo.
echo Installation completed successfully!
pause 