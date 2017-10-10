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
	nodelet:task_start nodelet:init tf2:task_start\
	roscpp:trace_link roscpp:ptr_name_info roscpp:ptr_call roscpp:timer_scheduled
do
	lttng enable-event -c roscpp -u $event 
done
# process context
lttng add-context -c roscpp -u \
  -t vpid -t procname \
  -t vtid -t perf:thread:instructions \
  -t perf:thread:cycles -t perf:thread:cpu-cycles

FILTER_PID=0
if [ $# -ge 1 ]
then
	echo "Filtering kernel events in PID > $1"
	FILTER_PID=$1
	echo $FILTER_PID
fi

# set up kernel scheduling and interruption events
for event in sched_kthread_stop sched_kthread_stop_ret sched_wakeup\
	sched_wakeup_new sched_switch sched_migrate_task sched_process_free\
	sched_process_exit sched_wait_task sched_process_wait \
	sched_process_fork sched_process_exec sched_stat_wait\
	sched_stat_sleep sched_stat_iowait sched_stat_blocked sched_stat_runtime\
	sched_pi_setprio irq_handler_entry irq_handler_exit \
	softirq_entry softirq_exit softirq_raise
do
	lttng enable-event -c scheduling -k $event --filter "\$ctx.pid > $FILTER_PID"
done

lttng add-context -c scheduling -k\
  -t pid -t procname \
  -t tid -t perf:cpu:cycles

