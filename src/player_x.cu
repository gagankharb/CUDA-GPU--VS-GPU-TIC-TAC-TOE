#include "player_x.h"
#include <iostream>
#include <cfloat>

// Constant memory for 8 winning lines
__constant__ int d_win_lines_x[8][3] = {
    {0, 1, 2}, {3, 4, 5}, {6, 7, 8}, // Rows
    {0, 3, 6}, {1, 4, 7}, {2, 5, 8}, // Columns
    {0, 4, 8}, {2, 4, 6}             // Diagonals
};

// CUDA Kernel: Tactical Move Evaluation for Player X
// Evaluates all 9 board positions in parallel using 9 CUDA threads
__global__ void kernel_evaluate_player_x(
    const int* __restrict__ board,
    float* __restrict__ scores,
    int my_symbol,
    int opp_symbol
) {
    int pos = blockIdx.x * blockDim.x + threadIdx.x;
    if (pos >= 9) return;

    // Check if the cell is already occupied
    if (board[pos] != 0) {
        scores[pos] = -100000.0f; // Illegal move marker
        return;
    }

    float score = 0.0f;

    // ----------------------------------------------------
    // 1. Immediate Winning Move Check
    // ----------------------------------------------------
    bool can_win_immediately = false;
    for (int i = 0; i < 8; ++i) {
        int a = d_win_lines_x[i][0];
        int b = d_win_lines_x[i][1];
        int c = d_win_lines_x[i][2];

        // Line must contain candidate position 'pos'
        if (a == pos || b == pos || c == pos) {
            int other1 = (a == pos) ? b : a;
            int other2 = (c == pos) ? b : c;

            // If other two positions are my_symbol, pos completes 3-in-a-row
            if (board[other1] == my_symbol && board[other2] == my_symbol) {
                can_win_immediately = true;
                break;
            }
        }
    }

    if (can_win_immediately) {
        scores[pos] = 10000.0f;
        return; // Immediate win overrides all other heuristics
    }

    // ----------------------------------------------------
    // 2. Immediate Opponent Block Check
    // ----------------------------------------------------
    bool must_block = false;
    for (int i = 0; i < 8; ++i) {
        int a = d_win_lines_x[i][0];
        int b = d_win_lines_x[i][1];
        int c = d_win_lines_x[i][2];

        if (a == pos || b == pos || c == pos) {
            int other1 = (a == pos) ? b : a;
            int other2 = (c == pos) ? b : c;

            // If opponent has other two positions, pos blocks opponent's immediate win
            if (board[other1] == opp_symbol && board[other2] == opp_symbol) {
                must_block = true;
                break;
            }
        }
    }

    if (must_block) {
        score += 5000.0f; // Highest priority after immediate win
    }

    // ----------------------------------------------------
    // 3. Center Priority
    // ----------------------------------------------------
    if (pos == 4) {
        score += 40.0f;
    }

    // ----------------------------------------------------
    // 4. Corners over Edges Priority
    // ----------------------------------------------------
    if (pos == 0 || pos == 2 || pos == 6 || pos == 8) {
        score += 25.0f; // Corners control 3 winning lines
    } else if (pos == 1 || pos == 3 || pos == 5 || pos == 7) {
        score += 10.0f; // Edges control only 2 winning lines
    }

    // ----------------------------------------------------
    // 5. Future Winning Combinations Evaluation
    // ----------------------------------------------------
    for (int i = 0; i < 8; ++i) {
        int a = d_win_lines_x[i][0];
        int b = d_win_lines_x[i][1];
        int c = d_win_lines_x[i][2];

        if (a == pos || b == pos || c == pos) {
            int other1 = (a == pos) ? b : a;
            int other2 = (c == pos) ? b : c;

            int my_count = 0;
            int opp_count = 0;

            if (board[other1] == my_symbol) my_count++;
            else if (board[other1] == opp_symbol) opp_count++;

            if (board[other2] == my_symbol) my_count++;
            else if (board[other2] == opp_symbol) opp_count++;

            // If opponent does not occupy this line, it's a viable future win
            if (opp_count == 0) {
                if (my_count == 1) {
                    score += 35.0f; // Creates two-in-a-row threat
                } else if (my_count == 0) {
                    score += 15.0f; // Opens a new candidate line
                }
            } else if (opp_count == 1 && my_count == 0) {
                // Disrupts an opponent's open line
                score += 12.0f;
            }
        }
    }

    scores[pos] = score;
}

// PlayerX Host Class Implementation
PlayerX::PlayerX(int device_id)
    : device_id_(device_id),
      d_board_(nullptr),
      d_scores_(nullptr),
      start_event_(nullptr),
      stop_event_(nullptr),
      initialized_(false) {
    initDevice();
}

PlayerX::~PlayerX() {
    cleanup();
}

bool PlayerX::initDevice() {
    if (initialized_) return true;

    cudaError_t err = cudaSetDevice(device_id_);
    if (err != cudaSuccess) {
        std::cerr << "[Player X] cudaSetDevice failed: " << cudaGetErrorString(err) << std::endl;
        return false;
    }

    err = cudaMalloc((void**)&d_board_, 9 * sizeof(int));
    if (err != cudaSuccess) {
        std::cerr << "[Player X] cudaMalloc d_board_ failed: " << cudaGetErrorString(err) << std::endl;
        return false;
    }

    err = cudaMalloc((void**)&d_scores_, 9 * sizeof(float));
    if (err != cudaSuccess) {
        std::cerr << "[Player X] cudaMalloc d_scores_ failed: " << cudaGetErrorString(err) << std::endl;
        cudaFree(d_board_);
        d_board_ = nullptr;
        return false;
    }

    cudaEventCreate(&start_event_);
    cudaEventCreate(&stop_event_);

    initialized_ = true;
    return true;
}

void PlayerX::cleanup() {
    if (initialized_) {
        cudaSetDevice(device_id_);
        if (d_board_)  { cudaFree(d_board_); d_board_ = nullptr; }
        if (d_scores_) { cudaFree(d_scores_); d_scores_ = nullptr; }
        if (start_event_) { cudaEventDestroy(start_event_); start_event_ = nullptr; }
        if (stop_event_)  { cudaEventDestroy(stop_event_); stop_event_ = nullptr; }
        initialized_ = false;
    }
}

MoveResultX PlayerX::selectMove(const int current_board[9], int my_symbol, int opp_symbol) {
    MoveResultX result;
    result.best_position = -1;
    result.kernel_time_ms = 0.0f;
    result.has_legal_move = false;
    for (int i = 0; i < 9; ++i) result.scores[i] = -100000.0f;

    if (!initialized_ && !initDevice()) {
        std::cerr << "[Player X] Error: Device not initialized." << std::endl;
        return result;
    }

    cudaSetDevice(device_id_);

    // 1. Host-to-Device Memory Transfer
    cudaError_t err = cudaMemcpy(d_board_, current_board, 9 * sizeof(int), cudaMemcpyHostToDevice);
    if (err != cudaSuccess) {
        std::cerr << "[Player X] cudaMemcpy H2D failed: " << cudaGetErrorString(err) << std::endl;
        return result;
    }

    // 2. Start CUDA Event Timer
    cudaEventRecord(start_event_, 0);

    // 3. Launch CUDA Kernel: 1 block with 9 threads (1 thread per cell)
    kernel_evaluate_player_x<<<1, 9>>>(d_board_, d_scores_, my_symbol, opp_symbol);

    // 4. Stop CUDA Event Timer & Synchronize
    cudaEventRecord(stop_event_, 0);
    cudaEventSynchronize(stop_event_);
    cudaEventElapsedTime(&result.kernel_time_ms, start_event_, stop_event_);

    // Check for kernel launch errors
    err = cudaGetLastError();
    if (err != cudaSuccess) {
        std::cerr << "[Player X] Kernel launch error: " << cudaGetErrorString(err) << std::endl;
        return result;
    }

    // 5. Device-to-Host Memory Transfer
    err = cudaMemcpy(result.scores, d_scores_, 9 * sizeof(float), cudaMemcpyDeviceToHost);
    if (err != cudaSuccess) {
        std::cerr << "[Player X] cudaMemcpy D2H failed: " << cudaGetErrorString(err) << std::endl;
        return result;
    }

    // 6. Best Move Selection on Host
    float best_score = -1e9f;
    int best_pos = -1;

    for (int i = 0; i < 9; ++i) {
        // Only legal moves have board[i] == 0 and score > -90000
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
