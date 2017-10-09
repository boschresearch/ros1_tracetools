#include <ros/ros.h>
#include <tracetools/tracetools.h>
#include <iostream>

int main(int argc, char* argv[])
{
    ros::trace::node_init("tracetools test", ROS_VERSION);
    
    return 0;
}
