# Presentation Script & Viva Voce Guide
## Project: CUDA GPU vs GPU – Intelligent Tic-Tac-Toe Battle

> **Available Presentation Slide Decks:**
> - 🌐 **Interactive HTML5 Slides:** [`docs/presentation.html`](presentation.html) (Open in browser, press `F` for fullscreen, `N` for notes drawer, `P` to print/PDF)
> - 📊 **Microsoft PowerPoint:** [`docs/presentation.pptx`](presentation.pptx) (16:9 widescreen PowerPoint presentation)
> - 📝 **Marp / Markdown Deck:** [`docs/presentation_slides.md`](presentation_slides.md) (Standard developer slide deck)

---

## Part 1: 5–7 Minute Oral Presentation Script

### Slide 1 / Screen: Title & Introduction
- **What to Display on Screen**: Project Title slide or terminal window displaying the application banner:
  ```
  ======================================================================
            CUDA GPU VS GPU INTELLIGENT TIC-TAC-TOE BATTLE         
             High-Performance Parallel AI Game Simulation           
  ======================================================================
  ```
- **What to Say**:
  > "Good morning / afternoon professors and evaluators. Today, I am presenting my Coursera GPU Programming project: **CUDA GPU vs GPU – Intelligent Tic-Tac-Toe Battle**.
  > In this project, I have designed and implemented two autonomous AI competitors that compete against each other using NVIDIA CUDA GPU acceleration. Rather than running artificial intelligence algorithms sequentially on the CPU, each competitor offloads its entire decision-making process to custom CUDA kernels, evaluating all candidate board moves in parallel across GPU threads."

---

### Slide 2 / Screen: Assignment Objective & Motivation
- **What to Display on Screen**: Objective bullet points and system architecture diagram from `docs/architecture.md`.
- **What to Say**:
  > "The core assignment objective was to design a game featuring at least two GPU-based competitors running genuine CUDA kernels. 
  > I chose Tic-Tac-Toe because its discrete $3 \times 3$ state space allows us to clearly map physical board cells directly to individual CUDA threads within a warp. This makes the GPU memory hierarchy, thread parallelism, and host-device communication completely transparent and mathematically verifiable, without being obscured by complex game state overhead."

---

### Slide 3 / Screen: Two Independent Competitors & Strategies
- **What to Display on Screen**: Competitor comparison table:
  - **Player X**: Tactical CUDA AI (Immediate Win, Urgent Block, Center Dominance, Corner Bias, Open Line Expansion).
  - **Player O**: Strategic CUDA AI (Immediate Win, Urgent Block, Multi-threat Fork Creation, Opponent Fork Blocking, Threat Neutralization).
- **What to Say**:
  > "To ensure authentic competition, I developed two completely independent AI competitors with different underlying philosophies:
  > **Player X** is a Tactical AI. It evaluates linear winning lines, prioritizing center control, corner positioning, and opening lines with friendly pieces.
  > **Player O** is a Strategic AI. In addition to wins and blocks, Player O implements non-linear fork detection. It calculates moves that create two simultaneous winning threats, while also calculating and actively neutralizing forks that the opponent might be planning."

---

### Slide 4 / Screen: CUDA Kernel & Parallel Architecture
- **What to Display on Screen**: CUDA Kernel snippet showing `__global__ void kernel_evaluate_player_x<<<1, 9>>>` and constant memory `d_win_lines`.
- **What to Say**:
  > "Let's examine the CUDA implementation. When a competitor's turn arrives, the host copies the 9-element board array to GPU memory using `cudaMemcpy`.
  > We then launch a CUDA kernel configured with 1 block and 9 threads. Thread ID `threadIdx.x` corresponds directly to board position `i`. All 9 candidate positions are evaluated simultaneously.
  > If a cell is occupied, the thread assigns an illegal marker and returns immediately. If empty, the thread checks geometric lines using cached constant memory and computes the heuristic score. The results are copied back to the host via `cudaMemcpyDeviceToHost`, where the highest scoring valid move is selected."

---

### Slide 5 / Screen: Hardware Topologies (Dual-GPU vs Single-GPU)
- **What to Display on Screen**: Diagram of Mode A (Two Physical GPUs) vs Mode B (Single Physical GPU with concurrent threads).
- **What to Say**:
  > "Our system dynamically detects GPU hardware at startup:
  > If two or more physical GPUs are available, it enters **Mode A**, assigning GPU 0 to Player X and GPU 1 to Player O via `cudaSetDevice`.
  > If running in a single-GPU environment—such as the standard Coursera cloud environment—it automatically transitions to **Mode B**. In Mode B, both AI competitors run in separate CPU threads, but both execute their unique CUDA kernels on the single physical GPU. Mutexes and condition variables coordinate turn-taking to prevent race conditions while ensuring that all move evaluations remain 100% on the GPU."

---

### Slide 6 / Screen: Live Execution & Demonstration
- **What to Display on Screen**: Live terminal executing `make run` or displaying `demo/sample_output.txt`.
- **What to Say**:
  > "Now, let us observe a live execution. Here we see the initialization phase detecting our GPU device properties.
  > The tournament runs for 10 consecutive matches. To ensure complete fairness and eliminate the first-mover advantage, the starting player alternates every match.
  > Notice that after every move, the terminal prints the exact CUDA kernel execution time—measured directly on the silicon using `cudaEventElapsedTime`—along with the parallel score matrix computed by the 9 threads."

---

### Slide 7 / Screen: Match Statistics & Conclusion
- **What to Display on Screen**: Final Tournament Statistics table:
  - Total Matches, Win/Loss/Draw percentages, Average Kernel Execution Latency (sub-millisecond), Total Wall-Clock Time.
- **What to Say**:
  > "At the conclusion of the 10-match tournament, the system prints our statistical summary. We observe that because both AI algorithms are highly competent, games predominantly resolve in well-played draws or tactical wins, with kernel execution times typically under 0.05 milliseconds per evaluation.
  > In conclusion, this project successfully demonstrates host-device memory transfers, custom CUDA kernel design, SIMT thread mapping, multi-GPU topology detection, and thread-safe turn synchronization. Thank you, and I am now ready for your questions."

---

## Part 2: 15 Likely Viva Questions & Model Answers

### Q1: Why did you use 9 threads in your CUDA kernel?
**Answer**:
> "The Tic-Tac-Toe board consists of 9 distinct cells. By launching 9 threads in a single block, we achieve a direct 1-to-1 mapping where thread $i$ evaluates cell $i$. This eliminates sequential CPU loops and evaluates all candidate moves concurrently in $O(1)$ parallel time."

---

### Q2: Why did you place the 8 winning lines in `__constant__` memory instead of global memory?
**Answer**:
> "Constant memory resides in device memory but is cached directly on-chip in the Streaming Multiprocessor (SM). Since all 9 threads read the exact same 8 winning lines simultaneously to evaluate their cells, constant memory broadcasts the data to all threads in a single clock cycle, significantly reducing global memory bandwidth contention."

---

### Q3: What is the difference between Mode A and Mode B in your architecture?
**Answer**:
> "**Mode A** is for dual-GPU systems where Player X executes kernels on GPU 0 and Player O executes kernels on GPU 1 using `cudaSetDevice()`. **Mode B** is the single-GPU fallback where both competitors execute on GPU 0 using separate CPU coordinator threads synchronized via `std::mutex` and `std::condition_variable`."

---

### Q4: Why did you use CUDA Events instead of standard C++ `std::chrono` for kernel timing?
**Answer**:
> "CUDA kernel launches are asynchronous; the CPU resumes execution immediately after queueing the kernel on the GPU stream. A CPU timer would only measure launch-queue latency. CUDA Events (`cudaEventRecord`) insert hardware timestamps directly into the GPU command stream, providing true hardware execution timing."

---

### Q5: How does Player X's tactical strategy differ from Player O's strategic strategy?
**Answer**:
> "Player X uses a linear tactical heuristic prioritizing center control, corner stability, and open line creation. Player O uses a strategic threat heuristic that specifically calculates **forks**—moves that create two simultaneous winning threats—and performs counter-analysis to prevent opponent forks."

---

### Q6: What does your kernel do if a thread evaluates an occupied cell?
**Answer**:
> "The thread performs a boundary check `if (board[pos] != 0)`. If occupied, it immediately writes `-100000.0f` to `scores[pos]` and returns, ensuring the host argmax selector will never pick an illegal or occupied move."

---

### Q7: What is the purpose of `cudaEventSynchronize()`?
**Answer**:
> "`cudaEventSynchronize(stop_event)` blocks the host CPU thread until the GPU has completely finished executing all commands up to the specified stop event. This ensures the kernel has concluded before we calculate elapsed time or copy scores back."

---

### Q8: What would happen if you forgot to call `cudaFree()`?
**Answer**:
> "Failing to call `cudaFree()` causes a GPU memory leak. Over repeated matches, device memory would remain allocated on the VRAM until the host process terminates, potentially exhausting memory on long simulations."

---

### Q9: Could warp divergence occur in your 9-thread kernel?
**Answer**:
> "Yes, minor warp divergence occurs because occupied cells return early while empty cells execute heuristic evaluations. However, because our grid uses only 9 threads within a single 32-thread warp, the total execution cycle count is negligible (a fraction of a microsecond)."

---

### Q10: How do you alternate starting players across the 10 matches?
**Answer**:
> "We use modulo arithmetic on the match index: `CellState starting_player = (match_idx % 2 == 1) ? CELL_X : CELL_O;`. Odd matches start with Player X; even matches start with Player O. This guarantees 5 games starting as X and 5 starting as O."

---

### Q11: How do you verify that memory transfers succeeded?
**Answer**:
> "Every CUDA runtime call (`cudaMalloc`, `cudaMemcpy`, `cudaSetDevice`) returns a `cudaError_t` status code. We check this code against `cudaSuccess` and print descriptive diagnostics using `cudaGetErrorString(err)` if an error occurs."

---

### Q12: Why did you separate game state management from GPU decision-making?
**Answer**:
> "This follows the Single Responsibility Principle. The `GameEngine` acts as the authoritative referee on the host CPU, validating rules and detecting wins/draws. The GPU is treated strictly as an accelerated compute coprocessor that evaluates candidate move options."

---

### Q13: Can two CPU threads call CUDA functions on the same GPU simultaneously?
**Answer**:
> "Yes. The NVIDIA CUDA driver supports multi-threaded host access to a single device through CUDA contexts. In our implementation, we also use a mutex and turn-state variable to enforce disciplined turn-taking matching the game rules."

---

### Q14: How does Player O calculate a fork on the GPU?
**Answer**:
> "Inside Player O's kernel, the device helper `count_winning_threats()` simulates placing Player O's symbol at the candidate cell and iterates across all 8 lines. If $\ge 2$ lines now have two Player O pieces and one empty cell, the move generates two simultaneous winning paths that the opponent cannot simultaneously block."

---

### Q15: How can this project be scaled to larger games like Connect-4 or Gomoku?
**Answer**:
> "The architecture scales naturally. In Connect-4 (7 columns), a kernel of 7 threads can evaluate columns. For Gomoku or Chess, we can expand from 1 thread per move to a parallel minimax tree where thousands of CUDA threads evaluate deep search plies in parallel."
