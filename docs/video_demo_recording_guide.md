# Video Demo Recording Guide & Presenter Script
## CUDA GPU vs GPU – Intelligent Tic-Tac-Toe Battle

This guide explains how to record your video demonstration using the presentation deck containing embedded screenshots of the compilation, runtime device initialization, parallel GPU move evaluations, and tournament benchmarks.

---

## 1. Available Presentation Files

Both presentation files contain the embedded high-resolution screenshots:

| File | Type | How to Use |
| :--- | :--- | :--- |
| **[`docs/CUDA_TicTacToe_Demo_Video_Presentation.pptx`](CUDA_TicTacToe_Demo_Video_Presentation.pptx)** | Microsoft PowerPoint Deck (16:9) | Double-click to open in PowerPoint. Click **Record** &rarr; **From Beginning** to record your webcam, microphone, and slides directly into an MP4 video. |
| **[`docs/video_demo_slides.html`](video_demo_slides.html)** | Interactive Web Deck | Open in Google Chrome or Microsoft Edge. Press <kbd>F</kbd> for fullscreen and press <kbd>N</kbd> to view your script. Record your screen using OBS, Loom, or Windows Game Bar. |

---

## 2. Recommended Recording Methods

### Method A: Microsoft PowerPoint Built-in Recording (Easiest)
1. Open [`docs/CUDA_TicTacToe_Demo_Video_Presentation.pptx`](CUDA_TicTacToe_Demo_Video_Presentation.pptx).
2. Go to the **Record** tab on the PowerPoint ribbon (or **Slide Show** &rarr; **Record Slide Show**).
3. Enable your microphone and optionally your webcam in the corner.
4. Click **Record** (red circle). Walk through the slides reading the provided script.
5. When finished, click **Export** &rarr; **Create a Video** (choose Full HD 1080p) to export your `.mp4` video file!

### Method B: Windows Xbox Game Bar (Native & Free)
1. Open [`docs/video_demo_slides.html`](video_demo_slides.html) in your browser.
2. Press <kbd>F</kbd> to enter Fullscreen.
3. Press <kbd>Windows Key + Alt + R</kbd> to start recording your screen.
4. Advance slides with <kbd>Space</kbd> or <kbd>&rarr;</kbd> while speaking into your microphone.
5. Press <kbd>Windows Key + Alt + R</kbd> again to stop recording. Your MP4 video is saved in `Videos\Captures`.

### Method C: OBS Studio / Loom
- Select window capture on either PowerPoint or your browser and record with your webcam in the corner.

---

## 3. Slide-by-Slide Video Narration Script (4–6 Minutes)

### Slide 1: Title & Introduction (0:00 – 0:30)
- **Visual on Screen**: Title slide with project badges (CUDA C++, SIMT, Hardware Profiling).
- **Spoken Script**:
  > *"Hello everyone and professors. Today, I am demonstrating my Coursera GPU Programming project: **CUDA GPU vs GPU – Intelligent Tic-Tac-Toe Battle**. In this project, I have designed and implemented two autonomous AI competitors that offload 100% of their candidate move evaluations to custom CUDA kernels running on NVIDIA GPU hardware."*

---

### Slide 2: Project Architecture & Execution Pipeline (0:30 – 1:00)
- **Visual on Screen**: 4-Layer system architecture breakdown.
- **Spoken Script**:
  > *"Before showing the execution, let's look at the system architecture. We designed a decoupled 4-layer system. The host CPU manages the 3x3 board and enforces the rules through the GameEngine referee, while candidate move evaluation is completely offloaded to our CUDA kernels executing across 9 GPU threads. This guarantees zero CPU simulation or cheating."*

---

### Slide 3: Clean Compilation & NVCC Build Verification (1:00 – 1:35)
- **Visual on Screen**: Embedded terminal capture showing `make clean` and `make build` with `nvcc`.
- **Spoken Script**:
  > *"Here is our actual build verification. We execute `make clean` to wipe intermediate files, followed by `make build`. The NVIDIA CUDA Compiler (`nvcc`) compiles our CUDA kernels and C++ modules with `-O3` maximum optimization, linking them into our target binary in `bin/cuda_tictactoe` with zero compilation warnings."*

---

### Slide 4: Launching & CUDA Device Discovery (1:35 – 2:10)
- **Visual on Screen**: Embedded terminal capture of runtime initialization and GPU specifications.
- **Spoken Script**:
  > *"Next, we launch the executable. The program automatically calls `cudaGetDeviceCount()` to detect physical hardware. In this environment, it detects an NVIDIA GPU with 68 streaming multiprocessors and 10 gigabytes of VRAM. Because one physical GPU is available, the program automatically selects **Mode B**, coordinating two concurrent AI threads synchronized with mutexes on the single physical GPU."*

---

### Slide 5: Tournament Match 1 Initialization (2:10 – 2:35)
- **Visual on Screen**: Match 1 header and initial empty 3x3 board with coordinate references.
- **Spoken Script**:
  > *"The tournament begins with Match 1 of 10. The terminal renders our 3x3 board grid alongside the 1-to-9 position coordinate references. In Match 1, Player X—our Tactical AI—takes the first move on the empty board."*

---

### Slide 6: Player X GPU Move Evaluation (2:35 – 3:10)
- **Visual on Screen**: Terminal capture showing Player X parallel scores `[P1:70 | ... | P5:100]` and selection of Position 5.
- **Spoken Script**:
  > *"Here is our first GPU move. When Player X's turn arrives, the host copies the board to GPU memory and launches our 9-thread CUDA kernel. In just **0.0244 milliseconds**, all 9 candidate positions are evaluated simultaneously in parallel. Position 5, the center cell, achieves the highest score of 100 points because it controls 4 winning lines, so Player X places an 'X' in the center."*

---

### Slide 7: Player O Strategic Counter-Play (3:10 – 3:45)
- **Visual on Screen**: Terminal capture showing Player O evaluating moves, Thread 4 early exit, and corner selection.
- **Spoken Script**:
  > *"Player O responds on its assigned logical thread. In **0.0261 milliseconds**, Player O's kernel evaluates all available positions. Thread 4 immediately detects that the center is already occupied by X and exits with an illegal score marker. Player O selects corner Position 1 to establish defensive balance and disrupt diagonal fork paths."*

---

### Slide 8: Mid-Game Defense: Urgent Threat Block (+6500) (3:45 – 4:20)
- **Visual on Screen**: Terminal capture showing Defensive Block triggered on Position 3 with score 6520.
- **Spoken Script**:
  > *"At move 6, Player X attempts to complete a 3-in-a-row winning line. Look at the candidate score vector: thread 2 identifies the imminent threat and awards **+6500 points** to Position 3. In just **0.0253 milliseconds**, Player O triggers an emergency defensive block on Position 3, averting defeat."*

---

### Slide 9: Match 1 Result: Equilibrium Draw (4:20 – 4:50)
- **Visual on Screen**: Final board state of Match 1 with all 9 cells occupied and Cat's Game declaration.
- **Spoken Script**:
  > *"Match 1 concludes after 9 moves in a Draw. In game theory, when two optimal heuristic algorithms compete in Tic-Tac-Toe, the mathematical equilibrium is always a Draw. This proves that both AI competitors are operating with complete defensive correctness and zero blunders."*

---

### Slide 10: 10-Match Autonomous Tournament (4:50 – 5:15)
- **Visual on Screen**: Explanation of alternating starting players across the 10 matches.
- **Spoken Script**:
  > *"The tournament now proceeds through 10 consecutive matches. To ensure complete fairness, the starting player alternates every single match: odd matches start with Player X, and even matches start with Player O. This completely eliminates first-mover advantage."*

---

### Slide 11: Final Tournament Benchmarks & Statistics (5:15 – 5:50)
- **Visual on Screen**: Embedded terminal capture of the final 10-match tournament statistics table.
- **Spoken Script**:
  > *"Here are our final tournament benchmark results. Across all 10 matches, we achieve a 100% draw rate. Look at our micro-benchmarks: the average kernel execution time is **0.0232 milliseconds** for Player X and **0.0265 milliseconds** for Player O, measured directly on the silicon via CUDA Events. Total execution time for all 10 matches was just **0.014 seconds**."*

---

### Slide 12: CUDA Constant Memory Caching (5:50 – 6:15)
- **Visual on Screen**: Technical slide on `__constant__ int d_win_lines[8][3]`.
- **Spoken Script**:
  > *"A key performance optimization in our CUDA code is using `__constant__` memory for the 8 winning lines. Because constant memory is cached directly inside the Streaming Multiprocessor, all 9 threads read winning lines in a single broadcast cycle, completely avoiding global DRAM stalls."*

---

### Slide 13: Conclusion & Summary (6:15 – 6:35)
- **Visual on Screen**: Final conclusion slide with checkmarks.
- **Spoken Script**:
  > *"In summary, this project proves genuine CUDA kernel execution, SIMT parallelization across 9 threads, accurate CUDA event profiling, dynamic multi-GPU support, and 100% tournament equilibrium. The complete project code, Makefile, and documentation are ready on GitHub. Thank you for watching!"*

---

## 4. Key Evidence to Highlight in Your Video

When evaluators review your video demo, they look for these specific technical indicators:
1. **Compilation Command**: Point your mouse to `nvcc -O3 -std=c++14` to prove it is compiled with NVIDIA's official CUDA compiler.
2. **Device Detection**: Highlight `Compute 8.6`, `68 SMs`, and `Mode B` to show automated hardware adaptation.
3. **Microsecond Kernel Timings**: Point out `0.0244 ms` and explain that it is measured using `cudaEventRecord` on GPU hardware queues.
4. **Candidate Score Vectors**: Show `[P1:70 | ... | P5:100]` to demonstrate that all 9 positions were evaluated in parallel.
5. **100% Draw Equilibrium**: Explain that perfect defensive AI in Tic-Tac-Toe must result in a draw according to game theory.
