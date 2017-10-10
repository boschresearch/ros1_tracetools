#! /bin/bash

#FILES=$(roslaunch --files $1)
#NODES=$(grep -h type $FILES|grep -v param|sed 's/.*type=\"//'|sed 's/\([^\"]*\)\".*/\1/'|sort -u)
#LAST=$(grep -h type $FILES|grep -v param|sed 's/.*type=\"//'|sed 's/\([^\"]*\)\".*/\1/'|sort -u|tail -1)
#FILTER="( $(for n in $NODES; do echo -n '$ctx.procname ==' \"$n\"; if [ $n != $LAST ]; then echo -n ' || '; fi; done) )"

# set up ust roscpp events
for event in roscpp:new_connection roscpp:callback_added roscpp:timer_added\
	roscpp:callback_start roscpp:callback_end\
	roscpp:publisher_link_handle_message roscpp:subscription_message_queued\
	roscpp:subscriber_callback_start roscpp:subscriber_callback_end\
	roscpp:publisher_message_queued	roscpp:subscriber_link_message_write\
	roscpp:subscriber_link_message_drop roscpp:subscriber_callback_added\
	roscpp:subscriber_callback_wrapper roscpp:task_start roscpp:init_node\
	nodelet:task_start nodelet:init tf2:task_start roscpp:message_processed\
	roscpp:trace_link roscpp:ptr_name_info roscpp:ptr_call roscpp:timer_scheduled
do
	lttng enable-event -c roscpp -u $event 
done
# process context
lttng add-context -c roscpp -u \
  -t vpid -t procname \
  -t vtid -t perf:thread:instructions \
  -t perf:thread:cycles -t perf:thread:cpu-cycles


