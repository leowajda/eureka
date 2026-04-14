cmake_minimum_required(VERSION 3.20)
project(cpp VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

file(GLOB_RECURSE EUREKA_CPP_SOURCES CONFIGURE_DEPENDS src/*.cpp)

add_library(eureka_cpp_objects OBJECT ${EUREKA_CPP_SOURCES})
target_include_directories(eureka_cpp_objects PUBLIC include)
