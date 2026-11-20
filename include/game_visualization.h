#ifndef GAME_VISUALIZATION_H
#define GAME_VISUALIZATION_H

#include "game_engine.h"
#include <string>
#include <vector>

// Visualization execution modes
enum ExecutionMode {
    MODE_A_DUAL_GPU,
    MODE_B_SINGLE_GPU,
    MODE_FALLBACK_DEMO
};

// Information about detected GPU device
struct DeviceInfo {
    int id;
    std::string name;
    int major;
    int minor;
    size_t total_memory_mb;
    int multi_processor_count;
};

// Terminal visualization manager
class GameVisualization {
public:
    static void printBanner();
    static void printDeviceInfo(const std::vector<DeviceInfo>& devices, ExecutionMode mode);
    static void printMatchHeader(int match_idx, int total_matches, CellState starting_player);
    static void printBoard(const int board[BOARD_SIZE]);
    static void printMoveEvaluation(
        const std::string& player_name,
        int selected_pos,
        float kernel_time_ms,
        const float scores[BOARD_SIZE],
        int device_id
    );
    static void printMatchResult(GameState state, int move_count);
    static void printTournamentStatistics(const MatchStats& stats);
    static void printDivider(char ch = '=', int length = 70);
};

#endif // GAME_VISUALIZATION_H
