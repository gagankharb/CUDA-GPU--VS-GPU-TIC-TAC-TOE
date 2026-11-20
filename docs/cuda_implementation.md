# CUDA Implementation Details

This guide explains the technical details of the CUDA implementation for the **GPU vs GPU Intelligent Tic-Tac-Toe Battle**. It is written to be accessible, technically precise, and directly suitable for an undergraduate B.Tech Computer Science and Engineering curriculum.

---

## 1. Problem Formulation in Parallel Computing

In sequential CPU programming, evaluating candidate moves requires looping through all empty cells on the board one by one:
```cpp
// Traditional Sequential CPU Approach: O(N) where N = 9
for (int i = 0; i < 9; ++i) {
    if (board[i] == EMPTY) {
        scores[i] = evaluateMoveHeuristic(board, i);
    }
}
```

In CUDA GPU programming, we exploit the SIMT (Single Instruction, Multiple Threads) architecture. We launch a grid containing **9 CUDA threads simultaneously**. Each thread is mapped directly to one candidate cell on the $3 \times 3$ board:

```
Thread 0 -> Cell (0,0) [Index 0]
Thread 1 -> Cell (0,1) [Index 1]
Thread 2 -> Cell (0,2) [Index 2]
Thread 3 -> Cell (1,0) [Index 3]
Thread 4 -> Cell (1,1) [Index 4]
Thread 5 -> Cell (1,2) [Index 5]
Thread 6 -> Cell (2,0) [Index 6]
Thread 7 -> Cell (2,1) [Index 7]
Thread 8 -> Cell (2,2) [Index 8]
```

All 9 board positions are analyzed concurrently in parallel, achieving $O(1)$ parallel evaluation complexity across the candidate space.

---

## 2. CUDA Kernel Structure & Organization

### 2.1 Thread & Block Configuration
- **Grid Dimension**: 1 Block.
- **Block Dimension**: 9 Threads (can be rounded to 16 or 32 for warp alignment).
- **Execution Syntax**:
  ```cuda
  kernel_evaluate_player_x<<<1, 9>>>(d_board, d_scores, my_symbol, opp_symbol);
  ```

### 2.2 Global Thread Identification
Inside the kernel, each thread computes its unique 1D cell index using standard CUDA indexing:
```cuda
int pos = blockIdx.x * blockDim.x + threadIdx.x;
if (pos >= 9) return; // Boundary guard
```

### 2.3 Occupied vs Empty Cell Handling
If a cell is already occupied by an 'X' or 'O', the thread marks it with an illegal score marker (-100,000) and terminates early:
```cuda
if (board[pos] != 0) {
    scores[pos] = -100000.0f; // Position already occupied
    return;
}
```

---

## 3. Constant Memory for Winning Lines

Tic-Tac-Toe has 8 fixed geometric winning lines (3 horizontal rows, 3 vertical columns, and 2 diagonals). In our implementation, these lines are placed in **CUDA Constant Memory** (`__constant__`):

```cuda
__constant__ int d_win_lines[8][3] = {
    {0, 1, 2}, {3, 4, 5}, {6, 7, 8}, // Rows
    {0, 3, 6}, {1, 4, 7}, {2, 5, 8}, // Columns
    {0, 4, 8}, {2, 4, 6}             // Diagonals
};
```

### Why Constant Memory?
- Constant memory is cached on the Streaming Multiprocessor (SM).
- When all 9 threads read the same winning line definitions simultaneously, the hardware performs a broadcast read in a single clock cycle, eliminating repeated global memory read latency.

---

## 4. Competitor Kernel Implementations

### 4.1 Player X: Tactical CUDA Kernel (`kernel_evaluate_player_x`)
Player X focuses on immediate linear evaluation:
1. **Immediate Win**: Simulates placing `my_symbol` at `pos`. If any line completes 3-in-a-row, writes $+10,000$ and returns.
2. **Immediate Opponent Block**: Simulates placing `opp_symbol` at `pos`. If opponent would win, writes $+5,000$.
3. **Center Bonus**: If `pos == 4`, adds $+40.0$.
4. **Corner Priority**: Corners (0, 2, 6, 8) control 3 potential lines, adding $+25.0$. Edges (1, 3, 5, 7) control only 2 lines, adding $+10.0$.
5. **Open Line Valuation**: Accumulates points for lines passing through `pos` that have no opponent markers.

### 4.2 Player O: Strategic CUDA Kernel (`kernel_evaluate_player_o`)
Player O incorporates non-linear threat detection and fork calculations:
1. **Immediate Win**: $+10,000$.
2. **Immediate Block**: $+6,500$.
3. **Fork Creation (`count_winning_threats`)**:
   A helper device function calculates how many 2-in-a-row lines would exist if Player O plays `pos`. If $\ge 2$, this move creates an unstoppable **Fork** ($+3,500$ points).
4. **Opponent Fork Prevention**: Simulates if the opponent playing `pos` would produce a fork. If so, awards $+2,800$ points to block the opponent's fork.
5. **Threat Disruption**: Grants $+45.0$ points per opponent line disrupted.

---

## 5. Host-Device Memory Lifecycle

The lifecycle follows rigorous CUDA memory standards:

```
[Host RAM]                                           [GPU VRAM]
  h_board (9 ints)     --- cudaMemcpy(H2D) --->      d_board (9 ints)
                                                           |
                                                  [Kernel Execution]
                                                  9 Threads in Parallel
                                                           |
  h_scores (9 floats)  <--- cudaMemcpy(D2H) ---      d_scores (9 floats)
```

### Step-by-Step API Sequence:
1. **Allocation (`cudaMalloc`)**:
   ```cpp
   cudaMalloc((void**)&d_board_, 9 * sizeof(int));
   cudaMalloc((void**)&d_scores_, 9 * sizeof(float));
   ```
2. **Transfer to Device (`cudaMemcpyHostToDevice`)**:
   ```cpp
   cudaMemcpy(d_board_, current_board, 9 * sizeof(int), cudaMemcpyHostToDevice);
   ```
3. **Execution & Event Timing**:
   ```cpp
   cudaEventRecord(start_event_, 0);
   kernel_evaluate<<<1, 9>>>(d_board_, d_scores_, my_sym, opp_sym);
   cudaEventRecord(stop_event_, 0);
   cudaEventSynchronize(stop_event_);
   cudaEventElapsedTime(&time_ms, start_event_, stop_event_);
   ```
4. **Transfer to Host (`cudaMemcpyDeviceToHost`)**:
   ```cpp
   cudaMemcpy(result.scores, d_scores_, 9 * sizeof(float), cudaMemcpyDeviceToHost);
   ```
5. **Cleanup (`cudaFree`)**:
   ```cpp
   cudaFree(d_board_);
   cudaFree(d_scores_);
   cudaEventDestroy(start_event_);
   cudaEventDestroy(stop_event_);
   ```

---

## 6. Accurate GPU Timing with CUDA Events

Using standard CPU timers (like `clock()` or `gettimeofday()`) to measure GPU operations is flawed because CUDA kernel launches are **asynchronous**. CPU timers would measure launch queue latency rather than actual GPU silicon execution time.

To guarantee accurate timing, we use **CUDA Events**:
- `cudaEventRecord(start, stream)` timestamps the start of the kernel on the GPU hardware queue.
- `cudaEventRecord(stop, stream)` timestamps the finish of the kernel on the GPU hardware queue.
- `cudaEventSynchronize(stop)` forces the host to wait until the GPU signals completion.
- `cudaEventElapsedTime(&ms, start, stop)` calculates the exact execution time in milliseconds with sub-millisecond precision.

---

## 7. Multi-GPU vs Single-GPU Handling

### Multi-GPU Detection:
```cpp
int deviceCount = 0;
cudaGetDeviceCount(&deviceCount);
```

- **Mode A ($\ge 2$ GPUs)**:
  ```cpp
  // Player X Worker
  cudaSetDevice(0);
  player_x.selectMove(...);

  // Player O Worker
  cudaSetDevice(1);
  player_o.selectMove(...);
  ```
- **Mode B (1 GPU)**:
  Both competitors operate on `cudaSetDevice(0)`. Host synchronization guarantees exclusive turn execution on the board while each competitor evaluates moves through its own allocated GPU memory buffers.
