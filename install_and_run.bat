@echo off
title ElderlyMonitor Installer and Launcher
color 1f

echo ===================================================
echo      ELDERLY MONITOR - ANTI-SCAM PROTECTION
echo ===================================================
echo.
echo [1/2] Checking and Installing Dependencies...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    color 4f
    echo.
    echo [ERROR] Python not found or installation failed!
    echo Please install Python from python.org and try again.
    pause
    exit /b
)

echo.
echo [2/2] Starting Protection Service...
echo The application will appear in your System Tray.
echo.
python src/main.py

pause
