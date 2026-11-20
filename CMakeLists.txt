cmake_minimum_required(VERSION 3.18)
project(cuda_gpu_vs_gpu_tictactoe LANGUAGES CXX CUDA)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CUDA_STANDARD 14)
set(CMAKE_CUDA_STANDARD_REQUIRED ON)

include_directories(include)

set(SOURCES
    src/main.cu
    src/player_x.cu
    src/player_o.cu
    src/game_engine.cpp
    src/game_visualization.cpp
)

add_executable(cuda_tictactoe ${SOURCES})

set_target_properties(cuda_tictactoe PROPERTIES
    CUDA_SEPARABLE_COMPILATION OFF
    CUDA_ARCHITECTURES "all"
)

# Output directory
set_target_properties(cuda_tictactoe PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
)
