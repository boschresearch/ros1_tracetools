import pickle
import sys
import subprocess
import re

from .lttng_model import *


def split_function_name(function_name, element=None):
    status, output = subprocess.getstatusoutput("echo '%s' | c++filt" % function_name)  # demangle
    match = re.search("(^/[^(]+)\(([^\(]*)\((.*)\)\+[\dxabcdef]+\) \[.*\]", output)
    if match is None:
        # print(output)
        return function_name
    clean = match.group(2).replace("_<std::allocator<void> >", "").replace("sensor_msgs::", "")
    if clean in ("ros::TopicManager::subscribe", "ros::TopicManager::addSubCallback") and element is not None:
        return "cb:%s" % element['source_name']
    return clean


class FunctionKey(object):
    def __init__(self, e, cb_ref = None):
        self.process_id = e.get('vpid', e.get('pid'))
        self.callback_ref = cb_ref if cb_ref is not None else get_callback(e)
        self.element = e

    def __hash__(self):
        return hash((self.process_id, self.callback_ref))

    def __eq__(self, other):
        return hasattr(other, "process_id") and hasattr(other, "callback_ref") and \
               self.process_id == other.process_id and self.callback_ref == other.callback_ref

    def __repr__(self):
        return "FnKey(pid=%d, cb=%d)" % (self.process_id, self.callback_ref)


class Mapper(object):
    def __init__(self):
        self.start_call = {}
        self.start_cycles = {}

        self.timer_map = {}
        # map the entry in the callback queue back to the real timer callback function
        self.timer_map = {}

        # naming info
        self.names = []
        # info callback invocations
        self.invocations = []
        # task info
        self.tasks = []
        # runtime info
        self.runtime = []
        # message_tracing
        self.mtrace = []
        # callback delays
        self.delays = []

        self.ignored_names = set()

        self.known_callbacks = set()
        self.unknown_callbacks = set()

        self.handler_map = {
            'roscpp:subscriber_callback_start': self.handle_subscriber_callback_start,
            'roscpp:subscriber_callback_end': self.handle_subscriber_callback_end,
            'roscpp:timer_added': self.handle_name_info,
            'roscpp:timer_scheduled': self.handle_timer_scheduled,
            'roscpp:callback_start': self.handle_callback_start,
            'roscpp:callback_end': self.handle_callback_end,
            'roscpp:subscriber_callback_added': self.handle_name_info,
            'roscpp:ptr_name_info': self.handle_name_info,
            'roscpp:task_start': self.handle_task_start,
            'roscpp:queue_delay': self.handle_queue_delay,
            'tf2:task_start': self.handle_task_start,
            'roscpp:message_processed': self.handle_message_processed,
            'roscpp:publisher_message_queued': self.handle_publisher_message_queued,
            'sched_stat_runtime': self.handle_sched_stat_runtime,
            'sched_stat_sleep': self.handle_sched_stat_sleep,
            'sched_stat_wait': self.handle_sched_stat_wait,
        }
        self.not_found = set()

    def handle(self, e):
        fn = self.handler_map.get(e['_name'], None)
        if fn is not None:
            name = get_name(e)
            process_id = e.get('vpid', e.get('pid'))
            task_id = e.get('vtid', e.get('tid'))
            timestamp = e['_timestamp']
            md = TraceMetaData(e["procname"], process_id, task_id, timestamp)

            fn(e, md)

    def create_trace_info(self):
        #print([(key.element['procname'], key.element['callback_ref']) for key in self.not_found])
        return TraceInfo(self.names, self.invocations, self.tasks, self.runtime, self.mtrace, self.delays)

    def handle_subscriber_callback_start(self, e, md):
        key = FunctionKey(e)
        self.start_call[key] = md.timestamp
        self.start_cycles[key] = get_cycles(e)

    def handle_queue_delay(self, e, md):
        key = FunctionKey(e)
        delay = e['_timestamp'] - (float(e['start_time_sec']) + float(e['start_time_nsec'])/1e9)*1e9
        self.delays.append(DelayInfo(md, e['queue_name'], get_callback(e), delay))

    def handle_subscriber_callback_end(self, e, md):
        key = FunctionKey(e)
        if key in self.start_call:
            start = self.start_call[key]
            duration = md.timestamp - start
            cycles = get_cycles(e) - self.start_cycles[key]
            self.invocations.append(InvocationInfo(md, get_callback(e), duration, cycles))

            # cleanup
            del self.start_call[key]
            del self.start_cycles[key]

    def handle_timer_scheduled(self, e, md):
        ref = e["callback_queue_cb_ref"]
        key = FunctionKey(e, ref)
        self.timer_map[key] = FunctionKey(e)

    def handle_callback_start(self, e, md):
        key = FunctionKey(e)
        if key not in self.known_callbacks:
            key = self.timer_map.get(key, key)

        if key in self.known_callbacks:
            self.start_call[key] = md.timestamp
            self.start_cycles[key] = get_cycles(e)
        else:
            self.not_found.add(key)

    def handle_callback_end(self, e, md):
        key = FunctionKey(e)
        if key not in self.known_callbacks:
            key = self.timer_map.get(key, key)
        if key in self.known_callbacks:
            try:
                start = self.start_call[key]
                duration = md.timestamp - start
                cycles = get_cycles(e) - self.start_cycles[key]
                self.invocations.append(InvocationInfo(md, get_callback(e), duration, cycles))

                # cleanup
                del self.start_call[key]
                del self.start_cycles[key]
                try:
                    del self.timer_map[key]
                except:
                    pass
            except KeyError as e:
                #print(e)                
                pass

    def handle_name_info(self, e, md):
        fi = FunctionInfo(md, split_function_name(get_m_name(e)), get_callback(e))
        self.names.append(fi)
        self.known_callbacks.add(FunctionKey(e))

    def handle_task_start(self, e, md):
        self.tasks.append(TaskInfo(md, get_t_name(e)))

    def handle_message_processed(self, e, md):
        self.mtrace.append(MessageTraceInfo(md, e['message_name'], get_callback(e), e['receipt_time_sec'] * 1e9 +
                                            e['receipt_time_nsec']))

    def handle_publisher_message_queued(self, e, md):
        self.mtrace.append(MessageTraceInfo(md, e['topic'], e['buffer_ref'], md.timestamp))

    def handle_sched_stat_runtime(self, e, md):
        md.node_name = e['comm']
        self.runtime.append(RuntimeStatsInfo(md, e['pid'], on_cpu=e['runtime']))

    def handle_sched_stat_wait(self, e, md):
        md.node_name = e['comm']
        self.runtime.append(RuntimeStatsInfo(md, e['pid'], wait_time=e['delay']))

    def handle_sched_stat_sleep(self, e, md):
        md.node_name = e['comm']
        self.runtime.append(RuntimeStatsInfo(md, e['pid'], sleep_time=e['delay']))


def map_roscpp(pods):
    m = Mapper()

    for e in pods:
        m.handle(e)

        #elif name in ('roscpp:trace_link',
        #              'roscpp:publisher_link_handle_message', 'roscpp:publisher_message_queued',
        #              'roscpp:subscription_message_queued', 'roscpp:subscriber_link_message_write'):
        #    # TODO add
        #    pass
        #elif name == 'roscpp:new_connection':
        #    pass
        #elif name == 'roscpp:init_node':
        #    pass
        #elif name in ('sched_switch', 'sched_wakeup', 'sched_process_exec', 'sched_migrate_task', 'sched_stat_sleep',
        #              'sched_wakeup_new', 'sched_process_fork', 'sched_stat_wait', 'sched_stat_blocked',
        #              'irq_handler_entry', 'irq_handler_exit', 'sched_stat_iowait', 'sched_process_wait',
        #              'syscall_entry_futex', 'syscall_exit_futex', 'sched_process_free', 'sched_process_exit',
        #              'nodelet:task_start', 'nodelet:init' ):
        #    # TODO add
        #    pass
        #else:
        #    ignored_names.add(name)

        #if not len(ignored_names) == 0:
        #    print(ignored_names)

    return m.create_trace_info()


def get_name(e):
    return e['_name']


def get_instructions(e):
    return e['perf_thread_instructions']


def get_t_name(e):
    return e['task_name']


def get_m_name(e):
    if get_name(e) == 'roscpp:subscriber_callback_added':
        return e['type_info']
    else:
        return e['function_name']


def get_callback(e):
    return e['callback_ref']


def get_cycles(e):
    return e['perf_thread_cycles']


replacements = (
    re.compile(r' actionlib::ActionServer<.*::([ >]+)::(.*)$'),
    re.compile(r' (b)ase_(l)ocal_(p)lanner::(.*)$')
)
#                     "base_local_planer": "blp",
#                     "ros::TopicManager::addSubCallback": None,
#                     "move_base::MoveBase": "MB",
#                     "tf::message_filter<"
#)


def simplify_fn(function_name):
    """
    Shortens function names according to a few built-in rules
    :param function_name:
    :return:
    """
    for expr in replacements:
        match = expr.match(function_name)
        if match is not None:
            function_name = "".join(match.groups())

    return function_name
