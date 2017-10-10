# bosch_arch_tracing

* [About bosch_arch_tracing](#about)
* [License and Organization](#license)
* [Maintainers and Contributors](#maintainers)
* [Build Instructions](#build)
* [Dependencies on OSS Components](#dependencies)
* [Continuous Integration](#ci)


## <a name="about"/>About bosch_arch_tracing

Generic tracing interface (with LTTng backend) and analysis tools.

This package *optionally* depends upon LTTng. If you don't specify -DWITH_LTTNG=ON, your project won't actually
generate tracing output.


## <a name="license"/>License and Organization

bosch\_arch\_tracing has been by the [RoSe](https://inside-docupedia.bosch.com/confluence/display/ROSE/) project (CR/SP02-002). We use the Apache Public License v2.0 (see LICENSE.txt).

## <a name="maintainers"/>Maintainers and Contributors

Author:

* [Luetkebohle Ingo (CR/AEA2)](https://connect.bosch.com/profiles/html/profileView.do?userid=20CD8DFB-55C3-4B2C-AD68-1C3819E3B831)
 
## <a name="build"/>Build Instructions

node\_model uses catkin to build. I strongly recommend [catkin tools](https://catkin-tools.readthedocs.io/en/latest/) but [catkin\_make](http://wiki.ros.org/catkin/commands/catkin_make) should also work.

For executing unit tests simply call `catkin run_tests` from anywhere in the catkin workspace, which will run all tests, or, alternatively, run `catkin build --this --no-deps --catkin-make-args run_tests` in your package directory, which will run your packages tests only.

## <a name="dependencies"/>Dependencies on OSS Components

ROS dependencies are listed as usual in the package.xml.

## <a name="ci"/>Continuous Integration

bosch\_arch\_tracing currently has no associated Continuous Integration job, but this should be coming soon.
