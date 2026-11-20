#include "player_o.h"
#include <iostream>
#include <cfloat>

// Constant memory for 8 winning lines for Player O
__constant__ int d_win_lines_o[8][3] = {
    {0, 1, 2}, {3, 4, 5}, {6, 7, 8}, // Rows
    {0, 3, 6}, {1, 4, 7}, {2, 5, 8}, // Columns
    {0, 4, 8}, {2, 4, 6}             // Diagonals
};

// Device helper: count winning threats if 'symbol' is placed at 'sim_pos'
__device__ int count_winning_threats(const int* board, int sim_pos, int symbol, int opp_symbol) {
    int threats = 0;
    for (int i = 0; i < 8; ++i) {
        int a = d_win_lines_o[i][0];
        int b = d_win_lines_o[i][1];
        int c = d_win_lines_o[i][2];

        // Line must contain sim_pos
        if (a == sim_pos || b == sim_pos || c == sim_pos) {
            int other1 = (a == sim_pos) ? b : a;
            int other2 = (c == sim_pos) ? b : c;

            int count_sym = 1; // sim_pos will be occupied by symbol
            int count_empty = 0;

            if (board[other1] == symbol) count_sym++;
            else if (board[other1] == 0) count_empty++;

            if (board[other2] == symbol) count_sym++;
            else if (board[other2] == 0) count_empty++;

            // A threat is a line with 2 pieces and 1 open space
            if (count_sym == 2 && count_empty == 1) {
                threats++;
            }
        }
    }
    return threats;
}

// CUDA Kernel: Strategic Move Evaluation for Player O
// Evaluates all 9 board positions in parallel using 9 CUDA threads
__global__ void kernel_evaluate_player_o(
    const int* __restrict__ board,
    float* __restrict__ scores,
    int my_symbol,
    int opp_symbol
) {
    int pos = blockIdx.x * blockDim.x + threadIdx.x;
    if (pos >= 9) return;

    // Check if position is occupied
    if (board[pos] != 0) {
        scores[pos] = -100000.0f; // Illegal move marker
        return;
    }

    float score = 0.0f;

    // ----------------------------------------------------
    // 1. Immediate Winning Opportunity Check
    // ----------------------------------------------------
    bool can_win = false;
    for (int i = 0; i < 8; ++i) {
        int a = d_win_lines_o[i][0];
        int b = d_win_lines_o[i][1];
        int c = d_win_lines_o[i][2];

        if (a == pos || b == pos || c == pos) {
            int other1 = (a == pos) ? b : a;
            int other2 = (c == pos) ? b : c;

            if (board[other1] == my_symbol && board[other2] == my_symbol) {
                can_win = true;
                break;
            }
        }
    }

    if (can_win) {
        scores[pos] = 10000.0f;
        return; // Immediate win is absolute top priority
    }

    // ----------------------------------------------------
    // 2. Block Opponent Winning Opportunity Check
    // ----------------------------------------------------
    bool must_block = false;
    for (int i = 0; i < 8; ++i) {
        int a = d_win_lines_o[i][0];
        int b = d_win_lines_o[i][1];
        int c = d_win_lines_o[i][2];

        if (a == pos || b == pos || c == pos) {
            int other1 = (a == pos) ? b : a;
            int other2 = (c == pos) ? b : c;

            if (board[other1] == opp_symbol && board[other2] == opp_symbol) {
                must_block = true;
                break;
            }
        }
    }

    if (must_block) {
        score += 6500.0f; // High urgency block
    }

    // ----------------------------------------------------
    // 3. Identify and Create Potential Forks
    // A fork creates >= 2 unblocked winning threats simultaneously
    // ----------------------------------------------------
    int my_threats_created = count_winning_threats(board, pos, my_symbol, opp_symbol);
    if (my_threats_created >= 2) {
        score += 3500.0f; // Strategic fork creation bonus
    } else if (my_threats_created == 1) {
        score += 150.0f;
    }

    // ----------------------------------------------------
    // 4. Opponent Fork Prevention
    // Check if opponent playing at this pos would create a fork
    // ----------------------------------------------------
    int opp_threats_if_played = count_winning_threats(board, pos, opp_symbol, my_symbol);
    if (opp_threats_if_played >= 2) {
        score += 2800.0f; // Block opponent's fork formation
    }

    // ----------------------------------------------------
    // 5. Threat Mitigation and Line Control
    // ----------------------------------------------------
    for (int i = 0; i < 8; ++i) {
        int a = d_win_lines_o[i][0];
        int b = d_win_lines_o[i][1];
        int c = d_win_lines_o[i][2];

        if (a == pos || b == pos || c == pos) {
            int other1 = (a == pos) ? b : a;
            int other2 = (c == pos) ? b : c;

            int opp_count = 0;
            int my_count = 0;

            if (board[other1] == opp_symbol) opp_count++;
            else if (board[other1] == my_symbol) my_count++;

            if (board[other2] == opp_symbol) opp_count++;
            else if (board[other2] == my_symbol) my_count++;

            // Disrupt opponent single piece line
            if (opp_count == 1 && my_count == 0) {
                score += 45.0f;
            }
            // Advance friendly line
            if (my_count == 1 && opp_count == 0) {
                score += 35.0f;
            }
        }
    }

    // ----------------------------------------------------
    // 6. Strategic Positional Weighting
    // ----------------------------------------------------
    if (pos == 4) {
        score += 45.0f; // Center strategic value
    } else if (pos == 0 || pos == 2 || pos == 6 || pos == 8) {
        score += 20.0f; // Corner defensive stability
    } else {
        score += 15.0f; // Edge perimeter control
    }

    scores[pos] = score;
}

// PlayerO Host Class Implementation
PlayerO::PlayerO(int device_id)
    : device_id_(device_id),
      d_board_(nullptr),
      d_scores_(nullptr),
      start_event_(nullptr),
      stop_event_(nullptr),
      initialized_(false) {
    initDevice();
}

PlayerO::~PlayerO() {
    cleanup();
}

bool PlayerO::initDevice() {
    if (initialized_) return true;

    cudaError_t err = cudaSetDevice(device_id_);
    if (err != cudaSuccess) {
        std::cerr << "[Player O] cudaSetDevice failed: " << cudaGetErrorString(err) << std::endl;
        return false;
    }

    err = cudaMalloc((void**)&d_board_, 9 * sizeof(int));
    if (err != cudaSuccess) {
        std::cerr << "[Player O] cudaMalloc d_board_ failed: " << cudaGetErrorString(err) << std::endl;
        return false;
    }

    err = cudaMalloc((void**)&d_scores_, 9 * sizeof(float));
    if (err != cudaSuccess) {
        std::cerr << "[Player O] cudaMalloc d_scores_ failed: " << cudaGetErrorString(err) << std::endl;
        cudaFree(d_board_);
        d_board_ = nullptr;
        return false;
    }

    cudaEventCreate(&start_event_);
    cudaEventCreate(&stop_event_);

    initialized_ = true;
    return true;
}

void PlayerO::cleanup() {
    if (initialized_) {
        cudaSetDevice(device_id_);
        if (d_board_)  { cudaFree(d_board_); d_board_ = nullptr; }
        if (d_scores_) { cudaFree(d_scores_); d_scores_ = nullptr; }
        if (start_event_) { cudaEventDestroy(start_event_); start_event_ = nullptr; }
        if (stop_event_)  { cudaEventDestroy(stop_event_); stop_event_ = nullptr; }
        initialized_ = false;
    }
}

MoveResultO PlayerO::selectMove(const int current_board[9], int my_symbol, int opp_symbol) {
    MoveResultO result;
    result.best_position = -1;
    result.kernel_time_ms = 0.0f;
    result.has_legal_move = false;
    for (int i = 0; i < 9; ++i) result.scores[i] = -100000.0f;

    if (!initialized_ && !initDevice()) {
        std::cerr << "[Player O] Error: Device not initialized." << std::endl;
        return result;
    }

    cudaSetDevice(device_id_);

    // 1. Host-to-Device Memory Transfer
    cudaError_t err = cudaMemcpy(d_board_, current_board, 9 * sizeof(int), cudaMemcpyHostToDevice);
    if (err != cudaSuccess) {
        std::cerr << "[Player O] cudaMemcpy H2D failed: " << cudaGetErrorString(err) << std::endl;
        return result;
    }

    // 2. Start CUDA Event Timer
    cudaEventRecord(start_event_, 0);

    // 3. Launch CUDA Kernel: 1 block with 9 threads
    kernel_evaluate_player_o<<<1, 9>>>(d_board_, d_scores_, my_symbol, opp_symbol);

    // 4. Stop CUDA Event Timer & Synchronize
    cudaEventRecord(stop_event_, 0);
    cudaEventSynchronize(stop_event_);
    cudaEventElapsedTime(&result.kernel_time_ms, start_event_, stop_event_);

    // Check for kernel launch errors
    err = cudaGetLastError();
    if (err != cudaSuccess) {
        std::cerr << "[Player O] Kernel launch error: " << cudaGetErrorString(err) << std::endl;
        return result;
    }

    // 5. Device-to-Host Memory Transfer
    err = cudaMemcpy(result.scores, d_scores_, 9 * sizeof(float), cudaMemcpyDeviceToHost);
    if (err != cudaSuccess) {
        std::cerr << "[Player O] cudaMemcpy D2H failed: " << cudaGetErrorString(err) << std::endl;
        return result;
    }

    // 6. Strategic Move Selection on Host
    float best_score = -1e9f;
    int best_pos = -1;

    for (int i = 0; i < 9; ++i) {
        if (current_board[i] == 0 && result.scores[i] > best_score) {
            best_score = result.scores[i];
            best_pos = i;
        }
    }

    if (best_pos != -1) {
        result.best_position = best_pos;
        result.has_legal_move = true;
    }

    return result;
}
