#include "game_visualization.h"
#include <iostream>
#include <iomanip>

void GameVisualization::printDivider(char ch, int length) {
    for (int i = 0; i < length; ++i) {
        std::cout << ch;
    }
    std::cout << "\n";
}

void GameVisualization::printBanner() {
    printDivider('=', 70);
    std::cout << "          CUDA GPU VS GPU INTELLIGENT TIC-TAC-TOE BATTLE         \n";
    std::cout << "           High-Performance Parallel AI Game Simulation           \n";
    printDivider('=', 70);
}

void GameVisualization::printDeviceInfo(const std::vector<DeviceInfo>& devices, ExecutionMode mode) {
    std::cout << "\n[CUDA PLATFORM INITIALIZATION]\n";
    std::cout << "  Detected CUDA Devices : " << devices.size() << "\n";

    for (const auto& dev : devices) {
        std::cout << "  [GPU " << dev.id << "] " << dev.name
                  << " (Compute " << dev.major << "." << dev.minor << ")"
                  << " | SMs: " << dev.multi_processor_count
                  << " | VRAM: " << dev.total_memory_mb << " MB\n";
    }

    std::cout << "  Execution Mode        : ";
    if (mode == MODE_A_DUAL_GPU) {
        std::cout << "MODE A - DUAL PHYSICAL GPUs\n";
        std::cout << "                          Player X Assigned -> GPU 0\n";
        std::cout << "                          Player O Assigned -> GPU 1\n";
    } else if (mode == MODE_B_SINGLE_GPU) {
        std::cout << "MODE B - SINGLE PHYSICAL GPU (Two Concurrent AI Threads)\n";
        std::cout << "                          Player X Assigned -> Logical Thread 0 (GPU 0)\n";
        std::cout << "                          Player O Assigned -> Logical Thread 1 (GPU 0)\n";
        std::cout << "                          Synchronization   -> std::mutex + std::condition_variable\n";
    } else {
        std::cout << "MODE C - REFERENCE / DEMONSTRATION FALLBACK\n";
    }

    std::cout << "\n[COMPETITOR PROFILES]\n";
    std::cout << "  Player X : Tactical CUDA AI\n";
    std::cout << "             Strategy: Immediate Win > Opponent Block > Center > Corners > Open Lines\n";
    std::cout << "  Player O : Strategic CUDA AI\n";
    std::cout << "             Strategy: Immediate Win > Opponent Block > Fork Creation > Fork Prevention\n";
    printDivider('-', 70);
}

void GameVisualization::printMatchHeader(int match_idx, int total_matches, CellState starting_player) {
    std::cout << "\n";
    printDivider('-', 70);
    std::cout << "                      MATCH " << match_idx << " OF " << total_matches << "\n";
    std::cout << "                Starting Player: "
              << (starting_player == CELL_X ? "Player X (Tactical)" : "Player O (Strategic)") << "\n";
    printDivider('-', 70);
}

void GameVisualization::printBoard(const int board[BOARD_SIZE]) {
    auto symbol = [](int val) -> char {
        if (val == CELL_X) return 'X';
        if (val == CELL_O) return 'O';
        return ' ';
    };

    std::cout << "\n";
    std::cout << "         Current Board State            Position Reference\n";
    std::cout << "             |     |                        |     |       \n";
    std::cout << "          " << symbol(board[0]) << "  |  " << symbol(board[1]) << "  |  " << symbol(board[2])
              << "                 1  |  2  |  3    \n";
    std::cout << "        _____|_____|_____              _____|_____|_____\n";
    std::cout << "             |     |                        |     |       \n";
    std::cout << "          " << symbol(board[3]) << "  |  " << symbol(board[4]) << "  |  " << symbol(board[5])
              << "                 4  |  5  |  6    \n";
    std::cout << "        _____|_____|_____              _____|_____|_____\n";
    std::cout << "             |     |                        |     |       \n";
    std::cout << "          " << symbol(board[6]) << "  |  " << symbol(board[7]) << "  |  " << symbol(board[8])
              << "                 7  |  8  |  9    \n";
    std::cout << "             |     |                        |     |       \n\n";
}

void GameVisualization::printMoveEvaluation(
    const std::string& player_name,
    int selected_pos,
    float kernel_time_ms,
    const float scores[BOARD_SIZE],
    int device_id
) {
    std::cout << ">> " << player_name << " [GPU " << device_id << "] evaluated moves in parallel:\n";
    std::cout << "   CUDA Kernel Execution Time : " << std::fixed << std::setprecision(4)
              << kernel_time_ms << " ms\n";

    std::cout << "   Parallel Candidate Scores  : [";
    for (int i = 0; i < BOARD_SIZE; ++i) {
        std::cout << "P" << (i + 1) << ":";
        if (scores[i] < -90000.0f) {
            std::cout << "occ";
        } else {
            std::cout << std::fixed << std::setprecision(0) << scores[i];
        }
        if (i < BOARD_SIZE - 1) std::cout << " | ";
    }
    std::cout << "]\n";

    std::cout << "   >> SELECTED POSITION       : " << (selected_pos + 1)
              << " (Index " << selected_pos << ")\n";
}

void GameVisualization::printMatchResult(GameState state, int move_count) {
    std::cout << "\n----------------------- MATCH RESULT -------------------------\n";
    if (state == STATE_WIN_X) {
        std::cout << "   RESULT : VICTORY FOR PLAYER X (Tactical CUDA AI) in " << move_count << " moves!\n";
    } else if (state == STATE_WIN_O) {
        std::cout << "   RESULT : VICTORY FOR PLAYER O (Strategic CUDA AI) in " << move_count << " moves!\n";
    } else if (state == STATE_DRAW) {
        std::cout << "   RESULT : DRAW (Cat's Game) after " << move_count << " moves!\n";
    }
    std::cout << "--------------------------------------------------------------\n";
}

void GameVisualization::printTournamentStatistics(const MatchStats& stats) {
    std::cout << "\n";
    printDivider('=', 70);
    std::cout << "                 FINAL TOURNAMENT MATCH STATISTICS               \n";
    printDivider('=', 70);

    std::cout << std::left << std::setw(35) << "  Total Matches Played"
              << ": " << stats.total_matches << "\n";
    std::cout << std::left << std::setw(35) << "  Player X Wins (Tactical)"
              << ": " << stats.x_wins << " (" << std::fixed << std::setprecision(1)
              << stats.x_win_pct << "%)\n";
    std::cout << std::left << std::setw(35) << "  Player O Wins (Strategic)"
              << ": " << stats.o_wins << " (" << std::fixed << std::setprecision(1)
              << stats.o_win_pct << "%)\n";
    std::cout << std::left << std::setw(35) << "  Draws (Ties)"
              << ": " << stats.draws << " (" << std::fixed << std::setprecision(1)
              << stats.draw_pct << "%)\n";

    printDivider('-', 70);
    std::cout << "  CUDA KERNEL & SYSTEM EXECUTION BENCHMARKS:\n";
    std::cout << std::left << std::setw(35) << "  Avg Player X Kernel Time"
              << ": " << std::fixed << std::setprecision(4)
              << stats.avg_kernel_time_x_ms << " ms\n";
    std::cout << std::left << std::setw(35) << "  Avg Player O Kernel Time"
              << ": " << std::fixed << std::setprecision(4)
              << stats.avg_kernel_time_o_ms << " ms\n";
    std::cout << std::left << std::setw(35) << "  Total Game Execution Time"
              << ": " << std::fixed << std::setprecision(3)
              << stats.total_execution_time_sec << " s\n";

    printDivider('=', 70);
    std::cout << "  Note: Kernel timings measured via cudaEventRecord / cudaEventElapsedTime.\n";
    std::cout << "  Host coordination & terminal visualization time is reported separately.\n";
    printDivider('=', 70);
    std::cout << "\n";
}
