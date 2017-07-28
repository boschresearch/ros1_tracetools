#include <iostream>

int main(int argc, char* argv[])
{
    #ifdef WITH_LTTNG
    std::cout << "LTTNG support is ON" << std::endl;
    #else
    std::cout << "LTTNG support is OFF" << std::endl;
    #endif
}