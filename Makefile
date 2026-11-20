# ==============================================================================
# Makefile: CUDA GPU vs GPU Intelligent Tic-Tac-Toe Battle
# Course: Coursera GPU Programming Assignment
# ==============================================================================

# Compiler & Linker
NVCC        := nvcc
CXX         := g++

# Compiler Flags
# -O3: Maximum optimization
# -std=c++14: C++14 standard for modern thread / chrono support
# -Iinclude: Include search directory
# -Xcompiler -Wall: Enable host compiler warnings
NVCC_FLAGS  := -O3 -std=c++14 -Iinclude -Xcompiler "-Wall"
LDFLAGS     := 

# Project Directories
SRC_DIR     := src
INC_DIR     := include
BUILD_DIR   := build
BIN_DIR     := bin

# Executable Target
TARGET      := $(BIN_DIR)/cuda_tictactoe

# Source Files
CU_SRCS     := $(SRC_DIR)/main.cu $(SRC_DIR)/player_x.cu $(SRC_DIR)/player_o.cu
CPP_SRCS    := $(SRC_DIR)/game_engine.cpp $(SRC_DIR)/game_visualization.cpp

# Object Files
CU_OBJS     := $(patsubst $(SRC_DIR)/%.cu, $(BUILD_DIR)/%.o, $(CU_SRCS))
CPP_OBJS    := $(patsubst $(SRC_DIR)/%.cpp, $(BUILD_DIR)/%.o, $(CPP_SRCS))
OBJS        := $(CU_OBJS) $(CPP_OBJS)

# Default Target
.PHONY: all build run clean rebuild help

all: build

build: $(TARGET)

# Link executable
$(TARGET): $(OBJS) | $(BIN_DIR)
	@echo "[LINK] $@"
	$(NVCC) $(NVCC_FLAGS) $(OBJS) -o $@ $(LDFLAGS)
	@echo "Build successful! Target: $@"

# Compile CUDA source files (.cu)
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.cu | $(BUILD_DIR)
	@echo "[NVCC] $<"
	$(NVCC) $(NVCC_FLAGS) -c $< -o $@

# Compile C++ source files (.cpp)
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.cpp | $(BUILD_DIR)
	@echo "[NVCC/C++] $<"
	$(NVCC) $(NVCC_FLAGS) -c $< -o $@

# Create directories if they do not exist
$(BUILD_DIR):
	@mkdir -p $(BUILD_DIR)

$(BIN_DIR):
	@mkdir -p $(BIN_DIR)

# Run target
run: build
	@echo "[EXECUTE] Running $(TARGET)..."
	./$(TARGET)

# Clean build artifacts
clean:
	@echo "[CLEAN] Removing build directories..."
	@rm -rf $(BUILD_DIR) $(BIN_DIR)
	@echo "Clean completed."

# Rebuild target
rebuild: clean build

# Help
help:
	@echo "Available targets:"
	@echo "  make         - Build the project executable (default)"
	@echo "  make build   - Build the project executable"
	@echo "  make run     - Build and run the project executable"
	@echo "  make clean   - Remove build and bin directories"
	@echo "  make rebuild - Clean and rebuild the project"
	@echo "  make help    - Display this help message"
