#! /bin/bash

if lttng list | grep -q "active"
then 
    lttng destroy
fi
lttng create
lttng enable-event -u roscpp:init_node
lttng add-context -u -t perf:thread:cycles
lttng start
rosrun tracetools tracetools_test
lttng stop

lttng view | grep roscpp:init_node | grep '"tracetools test"'
RET=$?
if [ $RET != 0 ]
then
    echo "No performance data recovered, maybe you're missing perf event permssions? Try 'sudo sysctl kernel.perf_event_paranoid=0'"
fi

lttng destroy

exit $RET