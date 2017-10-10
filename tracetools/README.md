# TRACETOOLS


Some helpers for tracing component-based systems using LTTng.

## CONTENTS

 * src/tracetools/ is the C++ support library with functions for user-space tracing
 * src/tracing/ is analysis code using Python3 and Panda
 * scripts/setup*.sh are setup scripts which configure LTTng with the right events
 * scripts/ctf_pickle_pod.py is a converter from Babeltrace format to a pickle of plain-old-dictionaries
 * scripts/example-run-scripts is a simple example of running the whole shebang


## INSTALLATION

The package.xml does not list any dependencies by default, because 
 1. they are not in the official rosdistro, yet
 1. one of it is a kernel module that only works when CONFIG_TRACING is enabled in the kernel
 1. also you'd need a PPA for the babeltrace tool on Ubuntu 14.04 right now.

Therefore, you need to manually install them, if you want, and then set the WITH_LTTNG
option during compilation of this package.

### For LTTng

    sudo apt-add-repository ppa:lttng/ppa
    sudo apt-get update 
    sudo apt-get install lttng-tools lttng-modules-dkms babeltrace liblttng-ust-dev python3-babeltrace

### Enable tracetools

`catkin config --cmake-args -DWITH_LTTNG=ON`

