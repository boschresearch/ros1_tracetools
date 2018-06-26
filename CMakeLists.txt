cmake_minimum_required(VERSION 2.8.3)
project(tracetools)

## Check if we have catkin
find_package(catkin REQUIRED)
find_package(PkgConfig REQUIRED)

## need boost shared_ptr
find_package(Boost REQUIRED)

option(WITH_LTTNG "Include support for tracing with LTTng" OFF)
if(WITH_LTTNG)
	pkg_check_modules(LTTNG REQUIRED lttng-ust)
endif()

if(LTTNG_FOUND)
  message(STATUS "Using LTTng: ${WITH_LTTNG}")
  add_definitions(-DWITH_LTTNG)
endif()

# evaluate tracepoint definitions
if(WITH_LTTNG)
	add_custom_command(OUTPUT ${PROJECT_SOURCE_DIR}/src/${PROJECT_NAME}/tp_call.c
		COMMAND lttng-gen-tp tp_call.tp -o ../src/${PROJECT_NAME}/tp_call.c -o ../src/${PROJECT_NAME}/tp_call.h
#		COMMAND mv tp_call.c tp_call.h ${PROJECT_SOURCE_DIR}/src/${PROJECT_NAME}/
		WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}/lttng
		DEPENDS ${PROJECT_SOURCE_DIR}/lttng/tp_call.tp
)
	set(LTTNG_GENERATED
		${PROJECT_SOURCE_DIR}/src/${PROJECT_NAME}/tp_call.h
		${PROJECT_SOURCE_DIR}/src/${PROJECT_NAME}/tp_call.c
	)
	message(STATUS ${LTTNG_GENERATED})
endif()


###################################
## catkin specific configuration ##
###################################
## The catkin_package macro generates cmake config files for your package
## Declare things to be passed to dependent projects
## INCLUDE_DIRS: uncomment this if you package contains header files
## LIBRARIES: libraries you create in this project that dependent projects also need
## CATKIN_DEPENDS: catkin_packages dependent projects also need
## DEPENDS: system dependencies of this project that dependent projects also need
catkin_package(
	INCLUDE_DIRS include
	LIBRARIES ${PROJECT_NAME}
#  CATKIN_DEPENDS other_catkin_pkg
#  DEPENDS system_lib
)

###########
## Build ##
###########

## Specify additional locations of header files
## Your package locations should be listed before other locations
include_directories(include ${catkin_INCLUDE_DIRS})
if(WITH_LTTNG)
	include_directories(${LTTNG_INCLUDEDIR})
endif()

## Declare a C++ library
set(TT_SOURCES src/${PROJECT_NAME}/tracetools.cpp)
if(WITH_LTTNG)
  set(TT_SOURCES src/${PROJECT_NAME}/tp_call.c ${TT_SOURCES})
endif()

add_library(${PROJECT_NAME} ${TT_SOURCES})
target_link_libraries(${PROJECT_NAME})
if(WITH_LTTNG)
	target_link_libraries(${PROJECT_NAME} ${LTTNG_LIBRARIES})
endif()

# status executable
add_executable(${PROJECT_NAME}_status src/${PROJECT_NAME}/status.cpp)
add_dependencies(${PROJECT_NAME}_status ${PROJECT_NAME})
target_link_libraries(${PROJECT_NAME}_status
  ${PROJECT_NAME}
)

# test trace executable
add_executable(${PROJECT_NAME}_test src/${PROJECT_NAME}/test.cpp)
add_dependencies(${PROJECT_NAME}_test ${PROJECT_NAME})
target_link_libraries(${PROJECT_NAME}_test
  ${PROJECT_NAME}
)

## Declare a C++ executable
# add_executable(tracetools_node src/tracetools_node.cpp)

## Add cmake target dependencies of the executable
## same as for the library above
# add_dependencies(tracetools_node ${${PROJECT_NAME}_EXPORTED_TARGETS} ${catkin_EXPORTED_TARGETS})

## Specify libraries to link a library or executable target against
# target_link_libraries(tracetools_node
#   ${catkin_LIBRARIES}
# )

#############
## Install ##
#############

# all install targets should use catkin DESTINATION variables
# See http://ros.org/doc/api/catkin/html/adv_user_guide/variables.html

## Mark executable scripts (Python etc.) for installation
## in contrast to setup.py, you can choose the destination
install(PROGRAMS
  scripts/setup-lttng-roscpp.sh
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

## Mark executables and/or libraries for installation
install(TARGETS ${PROJECT_NAME} ${PROJECT_NAME}_status ${PROJECT_NAME}_test
  ARCHIVE DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
  LIBRARY DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
  RUNTIME DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

## Mark cpp header files for installation
install(DIRECTORY include/${PROJECT_NAME}/
  DESTINATION ${CATKIN_PACKAGE_INCLUDE_DESTINATION}
  FILES_MATCHING PATTERN "*.h"
  PATTERN ".svn" EXCLUDE
)

## Mark other files for installation (e.g. launch and bag files, etc.)
# install(FILES
#   # myfile1
#   # myfile2
#   DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
# )

#############
## Testing ##
#############

if(CATKIN_ENABLE_TESTING)
  add_executable(test_get_ptr test/test_get_ptr.cpp)
endif()

# test LTTNG works
if(WITH_LTTNG)
	add_test(NAME test_event COMMAND rosrun tracetools event_test.sh)
endif(WITH_LTTNG)
## Add folders to be run by python nosetests
# catkin_add_nosetests(test)
