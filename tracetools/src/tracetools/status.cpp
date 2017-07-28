#include <iostream>
#include <tracetools/tracing_tools.h>

int main(int argc, char* argv[])
{
    std::cout << (ros::TracingTools::lttng_status() ? "LTTNG enabled" : "LTTNG disabled") << std::endl;
}