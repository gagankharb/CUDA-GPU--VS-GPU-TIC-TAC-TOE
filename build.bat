@echo off
REM ============================================================================
REM Build script for Windows (using NVCC)
REM ============================================================================

echo [BUILD] Creating output directories...
if not exist "build" mkdir build
if not exist "bin" mkdir bin

echo [BUILD] Checking NVCC compiler...
where nvcc >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] nvcc is not found in your PATH.
    echo Please install NVIDIA CUDA Toolkit and ensure nvcc is in your environment PATH.
    exit /b 1
)

echo [NVCC] Compiling CUDA and C++ source files...
nvcc -O3 -std=c++14 -Iinclude src\main.cu src\player_x.cu src\player_o.cu src\game_engine.cpp src\game_visualization.cpp -o bin\cuda_tictactoe.exe

if %ERRORLEVEL% equ 0 (
    echo [SUCCESS] Build succeeded! Executable located at bin\cuda_tictactoe.exe
    echo [RUN] To execute, run: bin\cuda_tictactoe.exe
) else (
    echo [ERROR] Compilation failed.
    exit /b %ERRORLEVEL%
)
