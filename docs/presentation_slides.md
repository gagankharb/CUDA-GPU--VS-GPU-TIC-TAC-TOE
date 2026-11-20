---
marp: true
theme: default
class: invert
paginate: true
header: 'CUDA GPU vs GPU: Intelligent Tic-Tac-Toe Battle'
footer: 'Coursera GPU Programming Assignment'
style: |
  section {
    background-color: #0d121d;
    color: #e6edf3;
    font-family: 'Segoe UI', system-ui, sans-serif;
  }
  h1 {
    color: #ffffff;
    border-bottom: 3px solid #76b900;
  }
  h2 {
    color: #76b900;
  }
  strong {
    color: #00d2ff;
  }
  pre {
    background-color: #161f30;
    border: 1px solid #243552;
  }
---

# CUDA GPU vs GPU
## Intelligent Tic-Tac-Toe Battle
### High-Performance Autonomous GPU Decision-Making

- **Course:** Coursera GPU Programming Assignment
- **Technology:** NVIDIA CUDA C++, nvcc, SIMT Architecture
- **Presenters:** Autonomous GPU Competitors (Player X vs Player O)

<!--
_note: Good morning professors. Today I am presenting my Coursera GPU Programming project: 'CUDA GPU vs GPU – Intelligent Tic-Tac-Toe Battle'. This project implements two autonomous AI agents whose move decisions are computed entirely in parallel on NVIDIA GPUs using custom CUDA kernels.
-->

---

# Assignment Objectives & Parallel Paradigm

### Core Goals:
- **Two Independent GPU Competitors:** True CUDA kernels evaluating decisions.
- **Zero CPU Simulation:** Host coordinates; device computes.
- **Dynamic Topology Detection:** Mode A (Dual physical GPUs) & Mode B (Single physical GPU).
- **Accurate Profiling:** Microsecond hardware timings via CUDA Events.

### Why Parallelize Tic-Tac-Toe?
- **Sequential CPU:** Evaluates moves serially in $O(N)$ where $N=9$.
- **CUDA SIMT:** Evaluates all 9 board cells concurrently across **9 GPU threads** in $O(1)$ parallel time.

<!--
_note: The assignment requires two independent GPU-based competitors running genuine CUDA kernels. Rather than running sequential loops on the CPU, we map the 9 board cells to 9 CUDA threads, evaluating all candidate moves concurrently in O(1) time.
-->

---

# 4-Layer Modular System Architecture

1. **Application Layer (`main.cu`):**
   - Device discovery via `cudaGetDeviceCount()`
   - Mode A / Mode B selection
   - 10-match tournament orchestration
2. **Competitor Layer (`PlayerX` & `PlayerO`):**
   - Host buffers & encapsulated RAII device allocations
   - Asynchronous kernel launches and synchronization
3. **CUDA Device Kernels (`__global__`):**
   - `kernel_evaluate_player_x` (Tactical Heuristics)
   - `kernel_evaluate_player_o` (Fork Detection & Threat Neutralization)
4. **Host Arbitrator (`GameEngine` & `GameVisualization`):**
   - Rule enforcement, draw detection, and live ASCII UI

<!--
_note: Our architecture is cleanly divided into four modular layers: Tournament Host Orchestrator, Competitor Layer, CUDA Device Kernels, and Host Game Engine referee. Notice that rule validation stays on the host while heavy move evaluation is offloaded to the GPU.
-->

---

# Player X: Tactical CUDA AI

### Heuristic Philosophy: Linear Expansion & Threat Blocking
- **Immediate Win Check (+10,000 pts):** Completes 3-in-a-row if 2 friendly pieces align.
- **Immediate Opponent Block (+5,000 pts):** Neutralizes imminent enemy victory.
- **Center Dominance (+40 pts):** Prioritizes position 5 (index 4) which shares 4 win lines.
- **Corner Stability (+25 pts vs +10 pts):** Corners control 3 lines; edges control 2.
- **Open Line Potential (+35 / +15 pts):** Awards points for lines without enemy pieces.

```cuda
__global__ void kernel_evaluate_player_x(const int* board, float* scores, int my_sym, int opp_sym);
```

<!--
_note: Player X is our Tactical AI. It implements a linear tactical heuristic: checking immediate wins (+10,000), immediate defensive blocks (+5,000), center dominance (+40), corner preference, and open winning line potential.
-->

---

# Player O: Strategic CUDA AI

### Heuristic Philosophy: Counter-Play & Fork Mechanics
- **Immediate Win (+10,000 pts) & Urgent Block (+6,500 pts)**
- **Multi-Threat Fork Creation (+3,500 pts):**
  Uses device helper `count_winning_threats()` to detect moves creating $\ge 2$ unblocked 2-in-a-row threats simultaneously.
- **Opponent Fork Prevention (+2,800 pts):**
  Simulates opponent's next turn to block impending enemy forks before they form.
- **Dynamic Threat Disruption (+45 pts):**
  Disrupts developing enemy lines.

```cuda
__global__ void kernel_evaluate_player_o(const int* board, float* scores, int my_sym, int opp_sym);
```

<!--
_note: Player O is our Strategic AI. In addition to immediate wins and blocks, Player O features non-linear fork analysis. Using a device helper function, it identifies moves that create two simultaneous winning threats, while also calculating and blocking opponent forks.
-->

---

# CUDA Kernel Structure & SIMT Thread Mapping

### Direct Cell Mapping (1 Block, 9 Threads in Warp 0):
- Thread 0 $\rightarrow$ Cell (0,0) [Pos 1 - Corner]
- Thread 1 $\rightarrow$ Cell (0,1) [Pos 2 - Edge]
- Thread 4 $\rightarrow$ Cell (1,1) [Pos 5 - Center]
- Thread 8 $\rightarrow$ Cell (2,2) [Pos 9 - Corner]

### Occupied Cell Guard:
```cuda
int pos = threadIdx.x;
if (board[pos] != 0) {
    scores[pos] = -100000.0f; // Marked illegal
    return;                   // Early exit
}
```

<!--
_note: Looking at the kernel structure: we configure 1 block with 9 threads. Thread index matches board position. Occupied cells return immediately with -100,000 to prevent illegal moves, while empty cells evaluate heuristics concurrently.
-->

---

# Constant Memory Caching & Lifecycle

### Broadcast Optimization via `__constant__`:
```cuda
__constant__ int d_win_lines[8][3] = {
    {0, 1, 2}, {3, 4, 5}, {6, 7, 8}, // 3 Rows
    {0, 3, 6}, {1, 4, 7}, {2, 5, 8}, // 3 Columns
    {0, 4, 8}, {2, 4, 6}             // 2 Diagonals
};
```
- Constant memory is cached on-chip in the Streaming Multiprocessor (SM).
- All 9 threads read winning lines simultaneously via a single hardware broadcast cycle!

### Memory Lifecycle:
`cudaMalloc` $\rightarrow$ `cudaMemcpy(H2D)` $\rightarrow$ `kernel<<<1, 9>>>` $\rightarrow$ `cudaMemcpy(D2H)` $\rightarrow$ `cudaFree`

<!--
_note: For memory optimization, we store all 8 winning line definitions in CUDA __constant__ memory. Because constant memory is cached on-chip in each SM, all 9 threads read winning line definitions simultaneously in a single broadcast cycle.
-->

---

# Multi-GPU (Mode A) vs Single-GPU (Mode B)

### Automated Detection at Runtime:
```cpp
int device_count = 0;
cudaGetDeviceCount(&device_count);
```

### MODE A: Dual Physical GPUs (`device_count >= 2`)
- Player X binds to `GPU 0` via `cudaSetDevice(0)`
- Player O binds to `GPU 1` via `cudaSetDevice(1)`
- True hardware parallelism across independent silicon chips.

### MODE B: Single Physical GPU (`device_count == 1`)
- Both competitors execute on `GPU 0`
- Turn-taking coordinated via `std::mutex` and `std::condition_variable`
- Memory isolation: separate device buffers per AI competitor.

<!--
_note: The system automatically detects hardware at startup. If two physical GPUs are present, it assigns GPU 0 to Player X and GPU 1 to Player O (Mode A). In single-GPU environments like Coursera, it uses Mode B with synchronized CPU threads and mutexes.
-->

---

# Sub-Millisecond Profiling via CUDA Events

### Why CPU Timers (`std::chrono`) Fail:
- Kernel launches are **asynchronous**; CPU timers measure only queueing latency.

### Hardware Event Profiling:
```cpp
cudaEvent_t start, stop;
cudaEventCreate(&start); cudaEventCreate(&stop);

cudaEventRecord(start, 0);
kernel_evaluate<<<1, 9>>>(d_board, d_scores, my_sym, opp_sym);
cudaEventRecord(stop, 0);

cudaEventSynchronize(stop);
cudaEventElapsedTime(&time_ms, start, stop);
```
- Measures actual hardware GPU execution time with sub-millisecond precision!

<!--
_note: Standard CPU timers are misleading for GPU kernels because kernel launches are asynchronous. To get true hardware execution timing, we record CUDA events (cudaEventRecord) directly onto the GPU hardware stream and synchronize.
-->

---

# 10-Match Tournament & Telemetry

### Fairness Alternation:
- **Odd Matches (1, 3, 5, 7, 9):** Player X moves first.
- **Even Matches (2, 4, 6, 8, 10):** Player O moves first.
- Eliminates first-player advantage.

### Live Telemetry Output:
```text
>> Player X (Tactical CUDA AI) [GPU 0] evaluated moves in parallel:
   CUDA Kernel Execution Time : 0.0244 ms
   Parallel Candidate Scores  : [P1:70 | P2:40 | P3:70 | P4:40 | P5:100 | ... | P9:70]
   >> SELECTED POSITION       : 5 (Center)
```

<!--
_note: Our tournament executes 10 consecutive matches. To ensure fairness, the starting player alternates every match. After each move, the terminal prints the exact kernel execution time and the candidate score vector.
-->

---

# Tournament Results & Game Theory Equilibrium

| Benchmark Metric | Result | Analysis |
| :--- | :--- | :--- |
| **Total Matches** | 10 | Complete tournament |
| **Player X Wins** | 0 (0.0%) | Zero unforced blunders |
| **Player O Wins** | 0 (0.0%) | Flawless counter-defense |
| **Draws (Cat's Game)** | **10 (100.0%)** | **Nash Game-Theoretic Equilibrium** |
| **Avg Kernel Time (X)** | **0.0232 ms** | Sub-millisecond SIMT evaluation |
| **Avg Kernel Time (O)** | **0.0265 ms** | Sub-millisecond SIMT evaluation |
| **Total Run Duration** | **0.014 s** | Blazing-fast execution |

<!--
_note: Across the 10-match tournament, all games conclude in well-played draws with average kernel execution times around 0.025 milliseconds. In game theory, two optimal players in Tic-Tac-Toe must always draw—confirming our defensive kernels are mathematically sound.
-->

---

# Viva Voce Defense & Future Extensions

### Key Viva Questions:
- **Why 9 threads?** $O(1)$ SIMT parallel mapping for all candidate cells.
- **Why constant memory?** SM broadcast cache eliminates DRAM bottlenecks.
- **Why CUDA events?** True GPU hardware execution profiling.
- **How to prevent leaks?** RAII encapsulation calls `cudaFree()` and `cudaEventDestroy()`.

### Future Scaling:
- **Deep Tree Search:** Parallel Minimax & Alpha-Beta pruning evaluating thousands of plies.
- **Connect-4 & Gomoku:** Scaling to $7 \times 6$ and $15 \times 15$ boards with thousands of CUDA threads.
- **Tensor Cores:** Neural network policy-value evaluation via cuBLAS / Tensor Cores.

<!--
_note: In conclusion, this project demonstrates real CUDA kernels, SIMT thread mapping, constant memory caching, multi-GPU topologies, and hardware event profiling. It provides an extensible foundation for scaling to deep minimax game trees. Thank you, I am now open for questions.
-->
