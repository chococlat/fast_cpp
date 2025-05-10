
# CMakeList.txt : Top-level CMake project file, do global configuration
# and include sub-projects here.
#
cmake_minimum_required (VERSION 3.12)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED YES)

# Create project
project(asdf VERSION 0.1.0 LANGUAGES C CXX)

include(FetchContent)



# Add subdirectories
add_subdirectory(core)
add_subdirectory(apps/asd)

