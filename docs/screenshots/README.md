# Visual Demonstrations and Screenshots

This directory contains visual captures of the **CUDA GPU vs GPU – Intelligent Tic-Tac-Toe Battle** application.

---

## Included Screenshots

1. **`initial_board.png`**:
   Shows platform initialization, device detection (GPU specifications, compute capability, VRAM), execution mode determination (Mode B: Single Physical GPU / Concurrent AI Threads), competitor strategy profiles, and initial empty $3 \times 3$ grid with coordinate reference.

2. **`gameplay.png`**:
   Displays mid-game GPU execution telemetry, including parallel candidate scores across positions `P1` through `P9`, sub-millisecond CUDA kernel execution time measured via `cudaEventElapsedTime`, and board updates.

3. **`final_result.png`**:
   Demonstrates final match outcome detection and comprehensive 10-match tournament analytics, including win percentages, draw counts, average kernel execution times for Player X and Player O, and total execution time.

---

## How to Capture Live Terminal Screenshots Manually

When executing on your Coursera GPU cloud instance or a local machine with physical NVIDIA hardware:

1. **Compile and Run**:
   ```bash
   make clean
   make run
   ```

2. **Capturing Screens**:
   - **Linux / Ubuntu / Coursera Web Terminal**:
     - Use `scrot` or your desktop screenshot utility:
       ```bash
       # Capture whole screen
       scrot live_run.png
       # Or copy output using the 'script' utility:
       script -c "./bin/cuda_tictactoe" live_run.log
       ```
   - **Windows / PowerShell**:
     - Press `Windows Key + Shift + S` or `Alt + PrtScn` to capture the active command prompt window.
     - Save images as `docs/screenshots/initial_board.png`, `docs/screenshots/gameplay.png`, and `docs/screenshots/final_result.png`.

3. **Automated Reproduction**:
   You can re-generate the visual terminal assets anytime by running:
   ```bash
   python tools/simulate_tournament.py
   ```
