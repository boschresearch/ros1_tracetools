#! /bin/bash -x

SESSION_NAME=turtlebot-run-$RANDOM
if [ "$1" != "" ]
then
	BASE=$(basename -s .yaml $1)
	SESSION_NAME="$SESSION_NAME-$BASE"
	export LAUNCH_ARGS="move_base_param_file:=$1"
fi

# set up
lttng stop # could also use destroy, if you don't care about the session afterwards
SESSION=$(lttng create $SESSION_NAME|grep ^Traces|awk '{print $6}')

LAUNCH="turtlebot_stdr perf_sim.launch $LAUNCH_ARGS"

# this captures roscpp events only
$HOME/src/ros_ws/src/ros_comm/tools/rostrace/scripts/setup-lttng-roscpp.sh # "$LAUNCH"

export LD_LIBRARY_PATH=$HOME/src/ros_ws/devel/lib:$LD_LIBRARY_PATH 
lttng start

# run experiment
roslaunch $LAUNCH

# stop
lttng stop

# load
rosrun tracetools ctf_pickle_pod.py $SESSION $HOME/Temp/$(basename $SESSION).pickle 

#$@

