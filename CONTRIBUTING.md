# Contributing to CUDA GPU vs GPU Tic-Tac-Toe

Thank you for your interest in contributing to the **CUDA GPU vs GPU – Intelligent Tic-Tac-Toe Battle** project! This repository serves as a Coursera GPU programming assignment demonstrating parallel GPU decision-making, CUDA kernel execution, and multi-GPU/single-GPU synchronization.

---

## 1. Project Structure

Before making changes, familiarize yourself with the organization of the codebase:

```text
cuda-gpu-vs-gpu-tictactoe/
├── src/
│   ├── main.cu                  # Entry point, GPU detection, tournament orchestrator
│   ├── game_engine.cpp          # Board representation, move validation, win/draw detection
│   ├── player_x.cu              # Player X (Tactical CUDA AI) kernel and device management
│   ├── player_o.cu              # Player O (Strategic CUDA AI) kernel and device management
│   └── game_visualization.cpp   # Terminal rendering and tournament statistical analytics
├── include/
│   ├── game_engine.h            # Board structures, winning lines, match stats
│   ├── player_x.h               # Player X class interface and MoveResult definition
│   ├── player_o.h               # Player O class interface and MoveResult definition
│   └── game_visualization.h     # Visualization interface and DeviceInfo struct
├── docs/
│   ├── architecture.md          # Architectural blueprints and game flowcharts
│   ├── cuda_implementation.md   # CUDA kernel architecture, threads, and memory lifecycle
│   ├── presentation_script.md   # Presentation script and viva voce preparation
│   └── screenshots/             # Terminal execution visual captures
├── demo/
│   └── sample_output.txt        # Full terminal trace log from tournament execution
├── Makefile                     # Standard GNU Makefile for compilation
├── CMakeLists.txt               # Cross-platform CMake build configuration
├── build.bat                    # Windows NVCC build script
├── .gitignore                   # Ignore build artifacts and temporary files
├── LICENSE                      # MIT Open Source License
└── README.md                    # Comprehensive repository documentation
```

---

## 2. Setting Up the Development Environment

### Prerequisites
1. **NVIDIA GPU** with Compute Capability $\ge$ 3.5.
2. **NVIDIA CUDA Toolkit** (version 11.0 or newer recommended):
   ```bash
   nvcc --version
   nvidia-smi
   ```
3. **C++ Host Compiler**:
   - Linux: GCC / G++ (version 7.5 or higher).
   - Windows: Microsoft Visual Studio C++ (MSVC 2019/2022) with CUDA integration.
4. **Build Tools**:
   - GNU `make` or `cmake` ($\ge$ 3.18).

---

## 3. How to Compile and Run

### Using GNU Make (Linux / WSL / macOS):
```bash
# Clean build
make clean

# Compile executable
make build

# Run tournament
make run

# Clean and rebuild
make rebuild
```

### Using CMake:
```bash
mkdir build && cd build
cmake ..
cmake --build .
./bin/cuda_tictactoe
```

### Using Windows Batch Script:
```cmd
build.bat
bin\cuda_tictactoe.exe
```

---

## 4. Coding Conventions

- **CUDA Kernels**:
  - Keep `__global__` and `__device__` functions pure and memory-coalesced.
  - Explicitly use `const` qualifiers and `__restrict__` pointers where applicable.
  - Maintain defensive bounds checking: `if (idx >= 9) return;`.
- **Error Handling**:
  - Check return status of every CUDA runtime call (`cudaMalloc`, `cudaMemcpy`, `cudaSetDevice`).
  - Check `cudaGetLastError()` after kernel launches.
- **Timing**:
  - Measure kernel times using CUDA events (`cudaEventRecord`, `cudaEventSynchronize`, `cudaEventElapsedTime`).
  - Measure total wall-clock time using `std::chrono::high_resolution_clock`.
- **C++ Standards**:
  - Follow modern C++14/17 standards (`nullptr`, `constexpr`, RAII for resource management).
  - Encapsulate device pointers within classes to prevent GPU memory leaks.

---

## 5. How to Report Bugs

If you find a bug or unexpected behavior:
1. Check the [Issues](../../issues) tab to see if the issue is already reported.
2. If not, open a new issue with:
   - Your OS and hardware details (NVIDIA GPU model, driver version, CUDA Toolkit version).
   - Exact steps to reproduce the issue.
   - Terminal logs or error messages.

---

## 6. How to Suggest Improvements

We welcome enhancements, such as:
- Additional AI evaluation heuristics or minimax-based parallel GPU trees.
- Tensor Core or shared memory exploration.
- GUI or web visualization frontends.

Please submit a Pull Request (PR) with:
1. A clear description of the proposed feature or optimization.
2. Verification steps and benchmark comparison.
3. Clean, documented code adhering to project conventions.
