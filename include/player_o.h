#ifndef PLAYER_O_H
#define PLAYER_O_H

#include <string>
#include <cuda_runtime.h>

// Result of a move evaluation by Player O
struct MoveResultO {
    int best_position;        // Selected position (0..8)
    float kernel_time_ms;     // CUDA kernel execution time in ms
    float scores[9];          // Parallel strategic evaluation score for each position
    bool has_legal_move;      // True if a valid move was found
};

// Player O: Strategic CUDA AI Competitor
class PlayerO {
public:
    explicit PlayerO(int device_id = 0);
    ~PlayerO();

    // Initialize CUDA device context
    bool initDevice();

    // Execute parallel move evaluation on assigned GPU
    MoveResultO selectMove(const int current_board[9], int my_symbol = 2, int opp_symbol = 1);

    // Getters
    int getDeviceId() const { return device_id_; }
    std::string getName() const { return "Player O (Strategic CUDA AI)"; }
    std::string getStrategyDescription() const {
        return "Strategic Depth: Immediate Win > Opponent Block > Fork Creation > Fork Prevention > Threat Neutralization";
    }

private:
    int device_id_;
    int* d_board_;            // Device memory for 3x3 board
    float* d_scores_;         // Device memory for 9 position scores
    cudaEvent_t start_event_; // CUDA timing event
    cudaEvent_t stop_event_;  // CUDA timing event
    bool initialized_;

    // Release allocated device resources
    void cleanup();
};

#endif // PLAYER_O_H
