#include <tracetools/tracetools.h>
#include <iostream>

int main(int argc, char* argv[])
{
    std::cout << (ros::trace::compile_status() ? "Tracing enabled" : "Tracing disabled") << std::endl;
}
