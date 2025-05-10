import platform

BUILD_DIR = "build"
IS_WINDOWS = platform.system() == "Windows"


CMAKELISTS_ROOT = """
# CMakeList.txt : Top-level CMake project file, do global configuration
# and include sub-projects here.
#
cmake_minimum_required (VERSION 3.12)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED YES)

# Create project
project({{PROJ_NAME}} VERSION 0.1.0 LANGUAGES C CXX)

include(FetchContent)

{{EXTERNAL_DEPENDENCIES}}

# Add subdirectories
add_subdirectory(core)
{{APP_INCLUSIONS}}
"""

CMAKELISTS_CORE = """
# core/CMakeLists.txt
add_library(core
{{SRC_FILES}}
)

target_include_directories(core
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)

{{LIBRARIES}}

set_property(TARGET core PROPERTY CXX_STANDARD 20)
"""

CMAKELISTS_APP = """
# CMakeList.txt : CMake project for cmake_app, include source and define
# project specific logic here.
#
include(CTest)
enable_testing()

# Add source to this project's executable.
set(SRC_FILES_APP
{{SRC_FILES}}
    )

add_executable ({{APP_NAME}} ${SRC_FILES_APP})
target_include_directories({{APP_NAME}} PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_link_libraries({{APP_NAME}} PRIVATE core)

# TODO: Add tests and install targets if needed.

set(CPACK_PROJECT_NAME ${PROJECT_NAME})
set(CPACK_PROJECT_VERSION ${PROJECT_VERSION})
include(CPack)
"""

CMAKE_CORE_EDITABLE = """# Add the needed external dependencies here.

# FetchContent_Declare(
#     fmt
#     GIT_REPOSITORY https://github.com/fmtlib/fmt.git
#     GIT_TAG        9.1.0
# )
# FetchContent_MakeAvailable(fmt)
# target_link_libraries(core PUBLIC fmt::fmt)


# FetchContent_Declare(
#     nlohmann_json
#     GIT_REPOSITORY https://github.com/nlohmann/json.git
#     GIT_TAG        v3.11.3
# )
# FetchContent_MakeAvailable(nlohmann_json)
# target_link_libraries(core PUBLIC nlohmann_json::nlohmann_json)


#find_package(Boost 1.83 REQUIRED)
#target_include_directories(core PRIVATE ${Boost_INCLUDE_DIRS})

"""


DEFAULT_MAINCPP = """
#include <iostream>
#include <string>
#include <filesystem>

#include "subdir/class.hpp"

using std::cin;
using std::cout;
using std::string;
namespace fs = std::filesystem;

int main(){
    std::cout << "Hello World!\\n";
    return 0;
}
"""

DEFAULT_CLASSCPP = """
#include "subdir/class.hpp"
"""

DEFAULT_CLASSHPP = """
#pragma once
"""


DEFAULT_CORECLASSHPP = """
#pragma once

namespace core
{
    class MyClass
    {
    public:
        void say_hello();
    };
}
"""

DEFAULT_CORECLASSCPP = """
#include "core/class.hpp"
#include <iostream>

void core::MyClass::say_hello() {
    std::cout << "Hello from core!\\n";
}
"""