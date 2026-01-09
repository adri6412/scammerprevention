@echo off
title ElderlyMonitor - Scammer Simulation
color 4f

echo ===================================================
echo      SCAMMER ATTACK SIMULATION
echo ===================================================
echo.
echo This script will:
echo 1. Create a fake "AnyDesk.exe" (using cmd.exe)
echo 2. Open a fake "Bank Login" window
echo.
echo Make sure 'ElderlyMonitor' is ALREADY RUNNING!
echo.
pause

python tests/simulate_attack.py

pause
