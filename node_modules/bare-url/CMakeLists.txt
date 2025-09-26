cmake_minimum_required(VERSION 3.25)

find_package(cmake-bare REQUIRED PATHS node_modules/cmake-bare)
find_package(cmake-fetch REQUIRED PATHS node_modules/cmake-fetch)

project(bare_url C)

fetch_package("github:holepunchto/libutf#9c5d642")
fetch_package("github:holepunchto/liburl#03f1488")

add_bare_module(bare_url)

target_sources(
  ${bare_url}
  PRIVATE
    binding.c
)

target_link_libraries(
  ${bare_url}
  PRIVATE
    $<TARGET_OBJECTS:url>
  PUBLIC
    url
)
