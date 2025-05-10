# Add the needed external dependencies here.

FetchContent_Declare(
    fmt
    GIT_REPOSITORY https://github.com/fmtlib/fmt.git
    GIT_TAG        9.1.0
)
FetchContent_MakeAvailable(fmt)
target_link_libraries(core PUBLIC fmt::fmt)


FetchContent_Declare(
    nlohmann_json
    GIT_REPOSITORY https://github.com/nlohmann/json.git
    GIT_TAG        v3.11.3
)
FetchContent_MakeAvailable(nlohmann_json)
target_link_libraries(core PUBLIC nlohmann_json::nlohmann_json)


find_package(Boost 1.83 REQUIRED)
target_include_directories(core PRIVATE ${Boost_INCLUDE_DIRS})

