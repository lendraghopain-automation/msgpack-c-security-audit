add_executable(simple simple.c)
target_link_libraries(simple msgpack-c)
find_package(cJSON)
