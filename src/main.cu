#include <iostream>
#include <vector>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <chrono>
#include <cuda_runtime.h>

#include "game_engine.h"
#include "game_visualization.h"
#include "player_x.h"
#include "player_o.h"

// Synchronization state for thread-safe turn coordination
struct GameSync {
    std::mutex mtx;
    std::condition_variable cv;
    CellState turn;
    bool match_active;
    bool tournament_done;
    bool move_pending;
};

int main(int argc, char* argv[]) {
    auto tournament_start_time = std::chrono::high_resolution_clock::now();

    GameVisualization::printBanner();

    // ----------------------------------------------------
    // PHASE 1: Detect CUDA Devices and Select Execution Mode
    // ----------------------------------------------------
    int device_count = 0;
    cudaError_t device_err = cudaGetDeviceCount(&device_count);

    if (device_err != cudaSuccess || device_count == 0) {
        std::cerr << "\n[CUDA INITIALIZATION ERROR]\n";
        std::cerr << "  cudaGetDeviceCount failed or returned 0 devices.\n";
        std::cerr << "  CUDA Error: " << cudaGetErrorString(device_err) << "\n";
        std::cerr << "  Please ensure an NVIDIA GPU is installed with current drivers\n";
        std::cerr << "  and CUDA Toolkit is present in the environment.\n\n";
        return 1;
    }

    std::vector<DeviceInfo> devices;
    for (int i = 0; i < device_count; ++i) {
        cudaDeviceProp prop;
        cudaGetDeviceProperties(&prop, i);
        DeviceInfo info;
        info.id = i;
        info.name = prop.name;
        info.major = prop.major;
        info.minor = prop.minor;
        info.total_memory_mb = prop.totalGlobalMem / (1024 * 1024);
        info.multi_processor_count = prop.multiProcessorCount;
        devices.push_back(info);
    }

    // Determine execution mode
    ExecutionMode mode;
    int device_x = 0;
    int device_o = 0;

    if (device_count >= 2) {
        mode = MODE_A_DUAL_GPU;
        device_x = 0;
        device_o = 1;
    } else {
        mode = MODE_B_SINGLE_GPU;
        device_x = 0;
        device_o = 0;
    }

    GameVisualization::printDeviceInfo(devices, mode);

    // ----------------------------------------------------
    // PHASE 2: Initialize Competitors
    // ----------------------------------------------------
    PlayerX player_x(device_x);
    PlayerO player_o(device_o);

    // ----------------------------------------------------
    // PHASE 3: Tournament Execution (10 Matches)
    // ----------------------------------------------------
    constexpr int TOTAL_MATCHES = 10;
    MatchStats stats = {};
    stats.total_matches = TOTAL_MATCHES;

    double sum_time_x = 0.0;
    int move_count_x = 0;
    double sum_time_o = 0.0;
    int move_count_o = 0;

    for (int match_idx = 1; match_idx <= TOTAL_MATCHES; ++match_idx) {
        GameEngine engine;

        // Alternate starting competitor:
        // Odd matches: Player X starts
        // Even matches: Player O starts
        CellState starting_player = (match_idx % 2 == 1) ? CELL_X : CELL_O;
        CellState current_turn = starting_player;

        GameVisualization::printMatchHeader(match_idx, TOTAL_MATCHES, starting_player);
        GameVisualization::printBoard(engine.getBoard());

        // Thread synchronization constructs for single/multi GPU coordination
        GameSync sync;
        sync.turn = current_turn;
        sync.match_active = true;
        sync.tournament_done = false;
        sync.move_pending = false;

        // Shared turn variables
        bool match_running = true;

        while (match_running && !engine.isGameOver()) {
            if (sync.turn == CELL_X) {
                // Player X's Turn
                int board_snapshot[BOARD_SIZE];
                engine.getBoardCopy(board_snapshot);

                // GPU Kernel execution on assigned device
                MoveResultX res = player_x.selectMove(board_snapshot, CELL_X, CELL_O);

                if (res.has_legal_move) {
                    sum_time_x += res.kernel_time_ms;
                    move_count_x++;

                    engine.makeMove(res.best_position, CELL_X);

                    GameVisualization::printMoveEvaluation(
                        player_x.getName(),
                        res.best_position,
                        res.kernel_time_ms,
                        res.scores,
                        player_x.getDeviceId()
                    );
                    GameVisualization::printBoard(engine.getBoard());
                } else {
                    std::cerr << "[Warning] Player X found no legal moves.\n";
                    break;
                }

                GameState state = engine.checkGameState();
                if (state != STATE_IN_PROGRESS) {
                    match_running = false;
                    GameVisualization::printMatchResult(state, engine.getMoveCount());
                    if (state == STATE_WIN_X) stats.x_wins++;
                    else if (state == STATE_WIN_O) stats.o_wins++;
                    else if (state == STATE_DRAW) stats.draws++;
                } else {
                    sync.turn = CELL_O;
                }

            } else if (sync.turn == CELL_O) {
                // Player O's Turn
                int board_snapshot[BOARD_SIZE];
                engine.getBoardCopy(board_snapshot);

                // GPU Kernel execution on assigned device
                MoveResultO res = player_o.selectMove(board_snapshot, CELL_O, CELL_X);

                if (res.has_legal_move) {
                    sum_time_o += res.kernel_time_ms;
                    move_count_o++;

                    engine.makeMove(res.best_position, CELL_O);

                    GameVisualization::printMoveEvaluation(
                        player_o.getName(),
                        res.best_position,
                        res.kernel_time_ms,
                        res.scores,
                        player_o.getDeviceId()
                    );
                    GameVisualization::printBoard(engine.getBoard());
                } else {
                    std::cerr << "[Warning] Player O found no legal moves.\n";
                    break;
                }

                GameState state = engine.checkGameState();
                if (state != STATE_IN_PROGRESS) {
                    match_running = false;
                    GameVisualization::printMatchResult(state, engine.getMoveCount());
                    if (state == STATE_WIN_X) stats.x_wins++;
                    else if (state == STATE_WIN_O) stats.o_wins++;
                    else if (state == STATE_DRAW) stats.draws++;
                } else {
                    sync.turn = CELL_X;
                }
            }
        }
    }

    // ----------------------------------------------------
    // PHASE 4: Compute and Display Tournament Statistics
    // ----------------------------------------------------
    auto tournament_end_time = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = tournament_end_time - tournament_start_time;

    stats.total_execution_time_sec = elapsed.count();
    stats.x_win_pct = (static_cast<double>(stats.x_wins) / stats.total_matches) * 100.0;
    stats.o_win_pct = (static_cast<double>(stats.o_wins) / stats.total_matches) * 100.0;
    stats.draw_pct = (static_cast<double>(stats.draws) / stats.total_matches) * 100.0;

    stats.avg_kernel_time_x_ms = (move_count_x > 0) ? (sum_time_x / move_count_x) : 0.0f;
    stats.avg_kernel_time_o_ms = (move_count_o > 0) ? (sum_time_o / move_count_o) : 0.0f;

    GameVisualization::printTournamentStatistics(stats);

    return 0;
}
