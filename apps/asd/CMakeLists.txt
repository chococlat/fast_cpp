
# CMakeList.txt : CMake project for cmake_app, include source and define
# project specific logic here.
#
include(CTest)
enable_testing()

# Add source to this project's executable.
set(SRC_FILES_APP
    "main.cpp"
    "src/subdir/class.cpp"

    )

add_executable (asd ${SRC_FILES_APP})
target_include_directories(asd PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_link_libraries(asd PRIVATE core)

# TODO: Add tests and install targets if needed.

set(CPACK_PROJECT_NAME ${PROJECT_NAME})
set(CPACK_PROJECT_VERSION ${PROJECT_VERSION})
include(CPack)
