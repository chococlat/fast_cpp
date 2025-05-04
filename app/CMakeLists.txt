# CMakeList.txt : CMake project for cmake_app, include source and define
# project specific logic here.
#
include(CTest)
enable_testing()

# Add source to this project's executable.
set(SRC_FILES_APP
    "main.cpp"
    "src/class.cpp"
    )

add_executable (${PROJECT_NAME} ${SRC_FILES_APP})
target_include_directories(${PROJECT_NAME} PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)

if (CMAKE_VERSION VERSION_GREATER 3.12)
  set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 20)
endif()

# TODO: Add tests and install targets if needed.

set(CPACK_PROJECT_NAME ${PROJECT_NAME})
set(CPACK_PROJECT_VERSION ${PROJECT_VERSION})
include(CPack)