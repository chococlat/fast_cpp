# core/CMakeLists.txt
add_library(core
    "src/core/class.cpp"

)

target_include_directories(core
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)

set_property(TARGET core PROPERTY CXX_STANDARD 20)