#include <ros/ros.h>
#include <tracetools/tracetools.h>
#include <iostream>

int main(int argc, char* argv[])
{
    ros::TracingTools::trace_node_init("tracetools test", ROS_VERSION);
    
    return 0;
}