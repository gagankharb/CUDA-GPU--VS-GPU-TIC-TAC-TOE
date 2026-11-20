@echo off
REM ============================================================================
REM Live Terminal Demonstration Launcher (Windows)
REM ============================================================================
title CUDA GPU vs GPU Tic-Tac-Toe Live Demo

echo ============================================================================
echo   CUDA GPU vs GPU: Live Autonomous Game Battle Demonstration
echo ============================================================================
echo.
echo Choose demonstration mode:
echo   [1] Auto-Play (Real-time animated matches)
echo   [2] Step-by-Step (Press ENTER for each GPU move - Great for Viva/Demo)
echo.
set /p choice="Enter choice [1 or 2] (Default: 1): "

if "%choice%"=="2" (
    echo.
    echo Starting Step-by-Step Demo...
    python live_terminal_demo.py --step
) else (
    echo.
    echo Starting Auto-Play Demo...
    python live_terminal_demo.py
)

echo.
pause
