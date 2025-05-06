# core/CMakeLists.txt
add_library(core
    "src/core/class.cpp"

)

target_include_directories(core
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_link_libraries(core PUBLIC fmt::fmt)
target_link_libraries(core PUBLIC nlohmann_json::nlohmann_json)


set_property(TARGET core PROPERTY CXX_STANDARD 20)