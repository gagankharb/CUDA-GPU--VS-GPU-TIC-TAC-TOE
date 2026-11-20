#include "game_engine.h"
#include <cstring>
#include <iostream>

GameEngine::GameEngine() : moveCount(0) {
    resetBoard();
}

void GameEngine::resetBoard() {
    for (int i = 0; i < BOARD_SIZE; ++i) {
        board[i] = CELL_EMPTY;
    }
    moveCount = 0;
}

bool GameEngine::isValidMove(int position) const {
    if (position < 0 || position >= BOARD_SIZE) {
        return false;
    }
    return board[position] == CELL_EMPTY;
}

bool GameEngine::isCellEmpty(int position) const {
    if (position < 0 || position >= BOARD_SIZE) {
        return false;
    }
    return board[position] == CELL_EMPTY;
}

bool GameEngine::makeMove(int position, CellState player) {
    if (!isValidMove(position)) {
        return false;
    }
    board[position] = static_cast<int>(player);
    moveCount++;
    return true;
}

GameState GameEngine::checkGameState() const {
    // Check all 8 winning combinations
    for (int i = 0; i < 8; ++i) {
        int a = WINNING_LINES[i].c1;
        int b = WINNING_LINES[i].c2;
        int c = WINNING_LINES[i].c3;

        if (board[a] != CELL_EMPTY &&
            board[a] == board[b] &&
            board[b] == board[c]) {
            if (board[a] == CELL_X) {
                return STATE_WIN_X;
            } else if (board[a] == CELL_O) {
                return STATE_WIN_O;
            }
        }
    }

    // Check for draw (all 9 cells filled with no winner)
    if (moveCount >= BOARD_SIZE) {
        return STATE_DRAW;
    }

    // Still in progress
    return STATE_IN_PROGRESS;
}

bool GameEngine::isGameOver() const {
    return checkGameState() != STATE_IN_PROGRESS;
}

const int* GameEngine::getBoard() const {
    return board;
}

void GameEngine::getBoardCopy(int out_board[BOARD_SIZE]) const {
    std::memcpy(out_board, board, sizeof(int) * BOARD_SIZE);
}

int GameEngine::getMoveCount() const {
    return moveCount;
}

std::string GameEngine::cellToString(CellState cell) {
    switch (cell) {
        case CELL_X: return "X";
        case CELL_O: return "O";
        default:     return " ";
    }
}

std::string GameEngine::stateToString(GameState state) {
    switch (state) {
        case STATE_WIN_X:       return "Player X Wins";
        case STATE_WIN_O:       return "Player O Wins";
        case STATE_DRAW:        return "Draw (Cat's Game)";
        case STATE_IN_PROGRESS: return "In Progress";
        default:                return "Unknown";
    }
}
