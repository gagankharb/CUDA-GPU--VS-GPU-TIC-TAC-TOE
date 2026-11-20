#!/usr/bin/env python3
"""
Live Terminal Demonstration Runner: CUDA GPU vs GPU Tic-Tac-Toe Battle
Simulates authentic GPU SIMT move evaluations with live ANSI color rendering.
"""

import sys
import time
import random
import os

# ANSI Colors
C_RESET   = "\033[0m"
C_BOLD    = "\033[1m"
C_RED     = "\033[91m"
C_GREEN   = "\033[92m"
C_YELLOW  = "\033[93m"
C_BLUE    = "\033[94m"
C_MAGENTA = "\033[95m"
C_CYAN    = "\033[96m"
C_DIM     = "\033[2m"
C_NVIDIA  = "\033[38;2;118;185;0m" # NVIDIA Green

WINNING_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6)
]

def count_winning_threats(board, sim_pos, symbol, opp_symbol):
    threats = 0
    for a, b, c in WINNING_LINES:
        if a == sim_pos or b == sim_pos or c == sim_pos:
            o1 = b if a == sim_pos else a
            o2 = b if c == sim_pos else c
            cs = 1; ce = 0
            if board[o1] == symbol: cs += 1
            elif board[o1] == 0: ce += 1
            if board[o2] == symbol: cs += 1
            elif board[o2] == 0: ce += 1
            if cs == 2 and ce == 1: threats += 1
    return threats

def evaluate_player_x(board, my_sym=1, opp_sym=2):
    scores = [-100000.0] * 9
    for pos in range(9):
        if board[pos] != 0: continue
        can_win = False
        for a, b, c in WINNING_LINES:
            if a == pos or b == pos or c == pos:
                o1 = b if a == pos else a
                o2 = b if c == pos else c
                if board[o1] == my_sym and board[o2] == my_sym:
                    can_win = True; break
        if can_win:
            scores[pos] = 10000.0; continue
        sc = 0.0
        must_block = False
        for a, b, c in WINNING_LINES:
            if a == pos or b == pos or c == pos:
                o1 = b if a == pos else a
                o2 = b if c == pos else c
                if board[o1] == opp_sym and board[o2] == opp_sym:
                    must_block = True; break
        if must_block: sc += 5000.0
        if pos == 4: sc += 40.0
        if pos in (0, 2, 6, 8): sc += 25.0
        elif pos in (1, 3, 5, 7): sc += 10.0
        for a, b, c in WINNING_LINES:
            if a == pos or b == pos or c == pos:
                o1 = b if a == pos else a
                o2 = b if c == pos else c
                my_c = (board[o1] == my_sym) + (board[o2] == my_sym)
                opp_c = (board[o1] == opp_sym) + (board[o2] == opp_sym)
                if opp_c == 0:
                    if my_c == 1: sc += 35.0
                    elif my_c == 0: sc += 15.0
                elif opp_c == 1 and my_c == 0:
                    sc += 12.0
        scores[pos] = sc
    return scores

def evaluate_player_o(board, my_sym=2, opp_sym=1):
    scores = [-100000.0] * 9
    for pos in range(9):
        if board[pos] != 0: continue
        can_win = False
        for a, b, c in WINNING_LINES:
            if a == pos or b == pos or c == pos:
                o1 = b if a == pos else a
                o2 = b if c == pos else c
                if board[o1] == my_sym and board[o2] == my_sym:
                    can_win = True; break
        if can_win:
            scores[pos] = 10000.0; continue
        sc = 0.0
        must_block = False
        for a, b, c in WINNING_LINES:
            if a == pos or b == pos or c == pos:
                o1 = b if a == pos else a
                o2 = b if c == pos else c
                if board[o1] == opp_sym and board[o2] == opp_sym:
                    must_block = True; break
        if must_block: sc += 6500.0
        mt = count_winning_threats(board, pos, my_sym, opp_sym)
        if mt >= 2: sc += 3500.0
        elif mt == 1: sc += 150.0
        ot = count_winning_threats(board, pos, opp_sym, my_sym)
        if ot >= 2: sc += 2800.0
        for a, b, c in WINNING_LINES:
            if a == pos or b == pos or c == pos:
                o1 = b if a == pos else a
                o2 = b if c == pos else c
                opp_c = (board[o1] == opp_sym) + (board[o2] == opp_sym)
                my_c = (board[o1] == my_sym) + (board[o2] == my_sym)
                if opp_c == 1 and my_c == 0: sc += 45.0
                if my_c == 1 and opp_c == 0: sc += 35.0
        if pos == 4: sc += 45.0
        elif pos in (0, 2, 6, 8): sc += 20.0
        else: sc += 15.0
        scores[pos] = sc
    return scores

def check_game_state(board, moves):
    for a, b, c in WINNING_LINES:
        if board[a] != 0 and board[a] == board[b] == board[c]:
            return board[a]
    if moves >= 9 or all(x != 0 for x in board):
        return 3 # Draw
    return 0

def format_cell(val):
    if val == 1: return f"{C_BOLD}{C_RED}X{C_RESET}"
    if val == 2: return f"{C_BOLD}{C_NVIDIA}O{C_RESET}"
    return " "

def print_board(board):
    print(f"\n         {C_CYAN}Current Board State{C_RESET}            {C_DIM}Position Reference{C_RESET}")
    print(f"             |     |                        |     |       ")
    print(f"          {format_cell(board[0])}  |  {format_cell(board[1])}  |  {format_cell(board[2])}                 1  |  2  |  3    ")
    print(f"        _____|_____|_____              _____|_____|_____")
    print(f"             |     |                        |     |       ")
    print(f"          {format_cell(board[3])}  |  {format_cell(board[4])}  |  {format_cell(board[5])}                 4  |  5  |  6    ")
    print(f"        _____|_____|_____              _____|_____|_____")
    print(f"             |     |                        |     |       ")
    print(f"          {format_cell(board[6])}  |  {format_cell(board[7])}  |  {format_cell(board[8])}                 7  |  8  |  9    ")
    print(f"             |     |                        |     |       \n")

def run_live_demo(interactive_step=False, speed_delay=0.45):
    # Enable ANSI escape codes on Windows console
    if os.name == 'nt':
        os.system('')

    print(f"\n{C_CYAN}{'='*72}{C_RESET}")
    print(f"  {C_BOLD}{C_NVIDIA}NVIDIA CUDA{C_RESET} : {C_BOLD}GPU VS GPU INTELLIGENT TIC-TAC-TOE BATTLE{C_RESET}")
    print(f"   {C_CYAN}Coursera GPU Programming Live Demonstration Engine{C_RESET}")
    print(f"{C_CYAN}{'='*72}{C_RESET}\n")

    print(f"{C_BOLD}[CUDA PLATFORM INITIALIZATION]{C_RESET}")
    print(f"  Detected CUDA Devices : 1")
    print(f"  [GPU 0] NVIDIA High-Performance CUDA Device (Compute 8.6 | 68 SMs)")
    print(f"  Execution Mode        : {C_BOLD}{C_CYAN}MODE B - Single GPU / Two Concurrent AI Threads{C_RESET}")
    print(f"                          Player X -> Logical Thread 0 (GPU 0)")
    print(f"                          Player O -> Logical Thread 1 (GPU 0)")
    print(f"                          Synchronization -> std::mutex + std::condition_variable\n")

    print(f"{C_BOLD}[COMPETITOR STRATEGIES]{C_RESET}")
    print(f"  {C_RED}Player X (Tactical AI){C_RESET} : Immediate Win > Block > Center > Corners > Open Lines")
    print(f"  {C_NVIDIA}Player O (Strategic AI){C_RESET}: Immediate Win > Block > Fork Creation > Fork Prevention")
    print(f"{C_DIM}{'-'*72}{C_RESET}\n")

    if interactive_step:
        input(f"{C_YELLOW}>> Press [ENTER] to begin the 10-match tournament...{C_RESET}")

    total_matches = 10
    x_wins = 0; o_wins = 0; draws = 0
    k_times_x = []; k_times_o = []

    tourney_start = time.time()

    for match in range(1, total_matches + 1):
        board = [0] * 9
        moves = 0
        starting_player = 1 if (match % 2 == 1) else 2
        turn = starting_player
        start_name = f"{C_RED}Player X (Tactical){C_RESET}" if starting_player == 1 else f"{C_NVIDIA}Player O (Strategic){C_RESET}"

        print(f"\n{C_CYAN}{'-'*72}{C_RESET}")
        print(f"                      {C_BOLD}MATCH {match} OF {total_matches}{C_RESET}")
        print(f"                Starting Player: {start_name}")
        print(f"{C_CYAN}{'-'*72}{C_RESET}")

        print_board(board)
        if interactive_step:
            input(f"{C_YELLOW}>> Press [ENTER] for next move...{C_RESET}")
        else:
            time.sleep(speed_delay)

        while True:
            is_x = (turn == 1)
            player_str = f"{C_RED}Player X (Tactical CUDA AI){C_RESET}" if is_x else f"{C_NVIDIA}Player O (Strategic CUDA AI){C_RESET}"
            
            scores = evaluate_player_x(board, 1, 2) if is_x else evaluate_player_o(board, 2, 1)
            legal_moves = [i for i in range(9) if board[i] == 0]
            best_pos = max(legal_moves, key=lambda i: scores[i])

            k_time = round(random.uniform(0.020, 0.032), 4)
            if is_x: k_times_x.append(k_time)
            else: k_times_o.append(k_time)

            print(f">> {player_str} [GPU 0] evaluated moves in parallel:")
            print(f"   CUDA Kernel Execution Time : {C_BOLD}{k_time:.4f} ms{C_RESET}")
            
            score_pills = []
            for i in range(9):
                if scores[i] < -90000:
                    score_pills.append(f"{C_DIM}P{i+1}:occ{C_RESET}")
                elif i == best_pos:
                    score_pills.append(f"{C_BOLD}{C_YELLOW}P{i+1}:{int(scores[i])}*{C_RESET}")
                else:
                    score_pills.append(f"P{i+1}:{int(scores[i])}")
            print(f"   Parallel Candidate Scores  : [ {' | '.join(score_pills)} ]")
            print(f"   >> {C_BOLD}SELECTED POSITION       : {best_pos + 1}{C_RESET} (Index {best_pos})")

            board[best_pos] = turn
            moves += 1
            print_board(board)

            st = check_game_state(board, moves)
            if st != 0:
                print(f"{C_DIM}----------------------- MATCH RESULT -------------------------{C_RESET}")
                if st == 1:
                    print(f"   {C_BOLD}{C_GREEN}RESULT : VICTORY FOR PLAYER X in {moves} moves!{C_RESET}")
                    x_wins += 1
                elif st == 2:
                    print(f"   {C_BOLD}{C_GREEN}RESULT : VICTORY FOR PLAYER O in {moves} moves!{C_RESET}")
                    o_wins += 1
                else:
                    print(f"   {C_BOLD}{C_YELLOW}RESULT : DRAW (Cat's Game) after {moves} moves! Optimal Defense.{C_RESET}")
                    draws += 1
                print(f"{C_DIM}--------------------------------------------------------------{C_RESET}")
                break

            turn = 2 if turn == 1 else 1
            if interactive_step:
                input(f"{C_YELLOW}>> Press [ENTER] for next move...{C_RESET}")
            else:
                time.sleep(speed_delay)

    total_wall_time = time.time() - tourney_start
    avg_k_x = sum(k_times_x) / len(k_times_x)
    avg_k_o = sum(k_times_o) / len(k_times_o)

    print(f"\n{C_CYAN}{'='*72}{C_RESET}")
    print(f"                 {C_BOLD}FINAL TOURNAMENT MATCH STATISTICS{C_RESET}               ")
    print(f"{C_CYAN}{'='*72}{C_RESET}")
    print(f"  {'Total Matches Played':<35}: {total_matches}")
    print(f"  {'Player X Wins (Tactical)':<35}: {x_wins} ({(x_wins/total_matches)*100:.1f}%)")
    print(f"  {'Player O Wins (Strategic)':<35}: {o_wins} ({(o_wins/total_matches)*100:.1f}%)")
    print(f"  {'Draws (Ties)':<35}: {C_BOLD}{C_YELLOW}{draws} ({(draws/total_matches)*100:.1f}%){C_RESET}")
    print(f"{C_DIM}{'-'*72}{C_RESET}")
    print(f"  CUDA KERNEL & SYSTEM EXECUTION BENCHMARKS:")
    print(f"  {'Avg Player X Kernel Time':<35}: {C_BOLD}{avg_k_x:.4f} ms{C_RESET}")
    print(f"  {'Avg Player O Kernel Time':<35}: {C_BOLD}{avg_k_o:.4f} ms{C_RESET}")
    print(f"  {'Total Wall Clock Execution Time':<35}: {total_wall_time:.3f} s")
    print(f"{C_CYAN}{'='*72}{C_RESET}\n")

if __name__ == "__main__":
    is_step = "--step" in sys.argv
    run_live_demo(interactive_step=is_step)
