# CMakeList.txt: cmake_test 的 CMake 项目，在此处包括源代码并定义
# 项目特定的逻辑。
#
cmake_minimum_required (VERSION 3.8)

if (POLICY CMP0141) # 
  cmake_policy(SET CMP0141 NEW)
  set(CMAKE_MSVC_DEBUG_INFORMATION_FORMAT "$<IF:$<AND:$<C_COMPILER_ID:MSVC>,$<CXX_COMPILER_ID:MSVC>>,$<$<CONFIG:Debug,RelWithDebInfo>:EditAndContinue>,$<$<CONFIG:Debug,RelWithDebInfo>:ProgramDatabase>>")
endif()

project ("cmake_test")
find_package(OpenCV REQUIRED)
include_directories(${OpenCV_INCLUDE_DIRS})  
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)
if (OFF)
    add_executable (cmake_test demo.cpp Curves.cpp)
    target_link_libraries(cmake_test PRIVATE ${OpenCV_LIBS})
else()
    add_subdirectory(include/pybind11)
    SET(SOURCES
        ${CMAKE_CURRENT_SOURCE_DIR}/src/Cpp/pybind11.cpp
        ${CMAKE_CURRENT_SOURCE_DIR}/src/Cpp/Curves.cpp
        ${CMAKE_CURRENT_SOURCE_DIR}/include/Curves.hpp
        ${CMAKE_CURRENT_SOURCE_DIR}/include/cvbind.hpp
        )
	  pybind11_add_module(cmake_test ${SOURCES})
    target_link_libraries(cmake_test PRIVATE ${OpenCV_LIBS})
endif()


if (CMAKE_VERSION VERSION_GREATER 3.12)
  set_property(TARGET cmake_test PROPERTY CXX_STANDARD 20)
endif()
