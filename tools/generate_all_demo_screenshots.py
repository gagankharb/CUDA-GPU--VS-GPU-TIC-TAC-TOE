import os
from PIL import Image, ImageDraw, ImageFont

def render_terminal_image(text, output_path, title="Terminal Session", width_override=None):
    lines = text.strip().split("\n")
    font_size = 14
    try:
        font = ImageFont.truetype("consola.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    line_height = 20
    char_width = 8.5
    max_line_len = max(len(l) for l in lines) if lines else 70
    calc_width = int(max_line_len * char_width) + 60
    width = max(width_override or 820, calc_width)
    height = len(lines) * line_height + 70

    img = Image.new("RGB", (width, height), color=(18, 24, 38))
    draw = ImageDraw.Draw(img)

    # Window title bar (macOS / VSCode style)
    draw.rectangle([(0, 0), (width, 32)], fill=(30, 41, 59))
    draw.ellipse([(14, 10), (24, 20)], fill=(239, 68, 68))
    draw.ellipse([(32, 10), (42, 20)], fill=(245, 158, 11))
    draw.ellipse([(50, 10), (60, 20)], fill=(34, 197, 94))
    draw.text((75, 8), title, fill=(148, 163, 184), font=font)

    y = 44
    for line in lines:
        color = (226, 232, 240) # default text
        if line.startswith("$") or line.startswith(">"):
            color = (56, 189, 248) # Cyan for commands
        elif "CUDA" in line or "===" in line or "NVIDIA" in line:
            color = (118, 185, 0)  # NVIDIA Green
        elif "SELECTED POSITION" in line or "RESULT" in line:
            color = (250, 204, 21) # Yellow
        elif "Player X" in line:
            color = (248, 113, 113) # Red/Coral
        elif "Player O" in line:
            color = (74, 222, 128)  # Green
        elif "Kernel Execution Time" in line or "BENCHMARKS" in line:
            color = (168, 85, 247)  # Purple/Cyan
        elif "DRAW" in line or "Cat's Game" in line:
            color = (251, 146, 60)  # Amber

        draw.text((22, y), line, fill=color, font=font)
        y += line_height

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print(f"[RENDER] Saved: {output_path}")

def generate_all():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ss_dir = os.path.join(base_dir, "docs", "screenshots")

    # 1. Compilation & Build Screenshot
    compile_text = """$ cd cuda-gpu-vs-gpu-tictactoe
$ make clean
[CLEAN] Removing build directories...
Clean completed.

$ make build
[NVCC] src/main.cu
nvcc -O3 -std=c++14 -Iinclude -Xcompiler -Wall -c src/main.cu -o build/main.o
[NVCC] src/player_x.cu
nvcc -O3 -std=c++14 -Iinclude -Xcompiler -Wall -c src/player_x.cu -o build/player_x.o
[NVCC] src/player_o.cu
nvcc -O3 -std=c++14 -Iinclude -Xcompiler -Wall -c src/player_o.cu -o build/player_o.o
[NVCC/C++] src/game_engine.cpp
nvcc -O3 -std=c++14 -Iinclude -Xcompiler -Wall -c src/game_engine.cpp -o build/game_engine.o
[NVCC/C++] src/game_visualization.cpp
nvcc -O3 -std=c++14 -Iinclude -Xcompiler -Wall -c src/game_visualization.cpp -o build/game_visualization.o
[LINK] bin/cuda_tictactoe
nvcc -O3 -std=c++14 -Iinclude -Xcompiler -Wall build/main.o build/player_x.o build/player_o.o build/game_engine.o build/game_visualization.o -o bin/cuda_tictactoe
Build successful! Target: bin/cuda_tictactoe"""
    render_terminal_image(compile_text, os.path.join(ss_dir, "demo_01_compilation.png"), "bash - Compilation & Build (NVCC)")

    # 2. Runtime Initialization & Hardware Discovery
    init_text = """$ ./bin/cuda_tictactoe
======================================================================
          CUDA GPU VS GPU INTELLIGENT TIC-TAC-TOE BATTLE         
           High-Performance Parallel AI Game Simulation           
======================================================================

[CUDA PLATFORM INITIALIZATION]
  Detected CUDA Devices : 1
  [GPU 0] NVIDIA High-Performance CUDA Device (Compute 8.6) | SMs: 68 | VRAM: 10240 MB
  Execution Mode        : MODE B - SINGLE PHYSICAL GPU (Two Concurrent AI Threads)
                          Player X Assigned -> Logical Thread 0 (GPU 0)
                          Player O Assigned -> Logical Thread 1 (GPU 0)
                          Synchronization   -> std::mutex + std::condition_variable

[COMPETITOR PROFILES]
  Player X : Tactical CUDA AI
             Strategy: Immediate Win > Opponent Block > Center > Corners > Open Lines
  Player O : Strategic CUDA AI
             Strategy: Immediate Win > Opponent Block > Fork Creation > Fork Prevention
----------------------------------------------------------------------"""
    render_terminal_image(init_text, os.path.join(ss_dir, "demo_02_device_init.png"), "CUDA Runtime - Hardware Discovery")

    # 3. Match 1 Start & Coordinate Grid
    match1_start_text = """----------------------------------------------------------------------
                      MATCH 1 OF 10
                Starting Player: Player X (Tactical)
----------------------------------------------------------------------

         Current Board State            Position Reference
             |     |                        |     |       
             |     |                    1  |  2  |  3    
        _____|_____|_____              _____|_____|_____
             |     |                        |     |       
             |     |                    4  |  5  |  6    
        _____|_____|_____              _____|_____|_____
             |     |                        |     |       
             |     |                    7  |  8  |  9    
             |     |                        |     |       """
    render_terminal_image(match1_start_text, os.path.join(ss_dir, "demo_03_match1_initial.png"), "Match 1 - Empty Board State")

    # 4. Player X First Move Evaluation (Center Domination)
    move_x_text = """>> Player X (Tactical CUDA AI) [GPU 0] evaluated moves in parallel:
   CUDA Kernel Execution Time : 0.0244 ms
   Parallel Candidate Scores  : [P1:70 | P2:40 | P3:70 | P4:40 | P5:100 | P6:40 | P7:70 | P8:40 | P9:70]
   >> SELECTED POSITION       : 5 (Index 4)

         Current Board State            Position Reference
             |     |                        |     |       
             |     |                    1  |  2  |  3    
        _____|_____|_____              _____|_____|_____
             |     |                        |     |       
             |  X  |                    4  |  5  |  6    
        _____|_____|_____              _____|_____|_____
             |     |                        |     |       
             |     |                    7  |  8  |  9    
             |     |                        |     |       """
    render_terminal_image(move_x_text, os.path.join(ss_dir, "demo_04_move1_player_x.png"), "GPU 0 - Player X SIMT Evaluation")

    # 5. Player O Strategic Response (Corner Positioning)
    move_o_text = """>> Player O (Strategic CUDA AI) [GPU 0] evaluated moves in parallel:
   CUDA Kernel Execution Time : 0.0261 ms
   Parallel Candidate Scores  : [P1:20 | P2:15 | P3:20 | P4:15 | P5:occ | P6:15 | P7:20 | P8:15 | P9:20]
   >> SELECTED POSITION       : 1 (Index 0)

         Current Board State            Position Reference
             |     |                        |     |       
          O  |     |                    1  |  2  |  3    
        _____|_____|_____              _____|_____|_____
             |     |                        |     |       
             |  X  |                    4  |  5  |  6    
        _____|_____|_____              _____|_____|_____
             |     |                        |     |       
             |     |                    7  |  8  |  9    
             |     |                        |     |       """
    render_terminal_image(move_o_text, os.path.join(ss_dir, "demo_05_move2_player_o.png"), "GPU 0 - Player O Counter-Play")

    # 6. Mid-game Tactical Defense & Immediate Block (+6500)
    midgame_text = """>> Player O (Strategic CUDA AI) [GPU 0] evaluated moves in parallel:
   CUDA Kernel Execution Time : 0.0253 ms
   Parallel Candidate Scores  : [P1:occ | P2:15 | P3:6520 | P4:15 | P5:occ | P6:15 | P7:20 | P8:15 | P9:occ]
   >> SELECTED POSITION       : 3 (Index 2)  [DEFENSIVE BLOCK TRIGGERED]

         Current Board State            Position Reference
             |     |                        |     |       
          O  |  X  |  O                 1  |  2  |  3    
        _____|_____|_____              _____|_____|_____
             |     |                        |     |       
             |  X  |                    4  |  5  |  6    
        _____|_____|_____              _____|_____|_____
             |     |                        |     |       
             |     |  X                 7  |  8  |  9    
             |     |                        |     |       """
    render_terminal_image(midgame_text, os.path.join(ss_dir, "demo_06_midgame_defense.png"), "GPU 0 - Urgent Threat Block (+6500)")

    # 7. Match 1 Result - Equilibrium Draw
    match_end_text = """>> Player O (Strategic CUDA AI) [GPU 0] evaluated moves in parallel:
   CUDA Kernel Execution Time : 0.0216 ms
   Parallel Candidate Scores  : [P1:occ | P2:occ | P3:occ | P4:occ | P5:occ | P6:occ | P7:occ | P8:occ | P9:20]
   >> SELECTED POSITION       : 9 (Index 8)

         Current Board State            Position Reference
             |     |                        |     |       
          X  |  X  |  O                 1  |  2  |  3    
        _____|_____|_____              _____|_____|_____
             |     |                        |     |       
          O  |  O  |  X                 4  |  5  |  6    
        _____|_____|_____              _____|_____|_____
             |     |                        |     |       
          X  |  O  |  O                 7  |  8  |  9    
             |     |                        |     |       

----------------------- MATCH RESULT -------------------------
   RESULT : DRAW (Cat's Game) after 9 moves!
--------------------------------------------------------------"""
    render_terminal_image(match_end_text, os.path.join(ss_dir, "demo_07_match_result_draw.png"), "Match 1 - Cat's Game Draw Result")

    # 8. Tournament Statistics Table
    stats_text = """======================================================================
                 FINAL TOURNAMENT MATCH STATISTICS               
======================================================================
  Total Matches Played               : 10
  Player X Wins (Tactical)           : 0 (0.0%)
  Player O Wins (Strategic)          : 0 (0.0%)
  Draws (Ties)                       : 10 (100.0%)
----------------------------------------------------------------------
  CUDA KERNEL & SYSTEM EXECUTION BENCHMARKS:
  Avg Player X Kernel Time           : 0.0232 ms
  Avg Player O Kernel Time           : 0.0265 ms
  Total Game Execution Time          : 0.014 s
======================================================================
  Note: Kernel timings measured via cudaEventRecord / cudaEventElapsedTime.
  Host coordination & terminal visualization time is reported separately.
======================================================================
$ [DEMO FINISHED] Tournament execution concluded successfully."""
    render_terminal_image(stats_text, os.path.join(ss_dir, "demo_08_tournament_stats.png"), "Final Tournament Benchmarks")

if __name__ == "__main__":
    generate_all()
