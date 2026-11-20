#ifndef GAME_ENGINE_H
#define GAME_ENGINE_H

#include <vector>
#include <string>
#include <chrono>

// Board dimensions
constexpr int BOARD_SIZE = 9;
constexpr int GRID_DIM = 3;

// Cell states
enum CellState {
    CELL_EMPTY = 0,
    CELL_X     = 1,
    CELL_O     = 2
};

// Game outcomes
enum GameState {
    STATE_IN_PROGRESS = 0,
    STATE_WIN_X       = 1,
    STATE_WIN_O       = 2,
    STATE_DRAW        = 3
};

// Win line definition (indices 0..8)
struct WinLine {
    int c1, c2, c3;
};

// Winning combinations for 3x3 Tic-Tac-Toe
constexpr WinLine WINNING_LINES[8] = {
    // 3 Rows
    {0, 1, 2}, {3, 4, 5}, {6, 7, 8},
    // 3 Columns
    {0, 3, 6}, {1, 4, 7}, {2, 5, 8},
    // 2 Diagonals
    {0, 4, 8}, {2, 4, 6}
};

// Match statistics structure
struct MatchStats {
    int total_matches;
    int x_wins;
    int o_wins;
    int draws;
    double x_win_pct;
    double o_win_pct;
    double draw_pct;
    float avg_kernel_time_x_ms;
    float avg_kernel_time_o_ms;
    double total_execution_time_sec;
};

// Game Engine class managing board state and rules
class GameEngine {
public:
    GameEngine();
    ~GameEngine() = default;

    // Reset board for a new match
    void resetBoard();

    // Move execution
    bool makeMove(int position, CellState player);

    // Validation
    bool isValidMove(int position) const;
    bool isCellEmpty(int position) const;

    // Game status detection
    GameState checkGameState() const;
    bool isGameOver() const;

    // Board access
    const int* getBoard() const;
    void getBoardCopy(int out_board[BOARD_SIZE]) const;
    int getMoveCount() const;

    // Helper functions
    static std::string cellToString(CellState cell);
    static std::string stateToString(GameState state);

private:
    int board[BOARD_SIZE];
    int moveCount;
};

#endif // GAME_ENGINE_H
