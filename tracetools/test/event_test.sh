#! /bin/bash

if lttng list | grep -q "active"
then 
    lttng destroy
fi
lttng create
lttng enable-event -u roscpp:init_node
lttng start
rosrun tracetools tracetools_test
lttng stop

lttng view | grep roscpp:init_node | grep '"tracetools test"'
RET=$?
echo $RET

lttng destroy

exit $RET