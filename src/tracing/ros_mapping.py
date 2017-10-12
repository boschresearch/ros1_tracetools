# Copyright (c) 2016, 2017 - for information on the respective 
# copyright owner see the NOTICE file and/or the repository 
# https://github.com/bosch-robotics-cr/tracetools.git
#
#  Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import pickle
import sys
import subprocess
import re
from collections import defaultdict

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
        return "FnKey(pid=%d, cb=%x)" % (self.process_id, self.callback_ref)


class Mapper(object):
    def __init__(self):
        self.start_md = {}
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
        # ids of queue keys created from subscription_message_queued, to be ignored in regular call_start
        self.queue_keys = set()
        # ids we have not found, with counts on how oftne
        self.missing_keys = defaultdict(list)


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
            'roscpp:subscription_message_queued': self.handle_subscription_message_queued
        }
        self.not_found = set()

    def _add_fi(self, e, md, function_name, cb_ref, key, trigger=None):
        if trigger is None:
            trigger = 'unspecified'
            if e['_name'] == "roscpp:subscriber_callback_added":
                trigger = 'data'
            elif e['_name'] == "roscpp:timer_added":
                trigger = 'time'

        # print(e['_name'], trigger)
        fi = FunctionInfo(md, function_name, cb_ref, trigger)
        if key in self.known_callbacks:
            idx = -1
            try:
                idx = self.names.index(fi)
            except ValueError:
                for i, v in enumerate(self.names):
                    if v.cb_ref == cb_ref:
                        idx = i
                        break

            if idx != -1:
                if self.names[idx].trigger == 'unspecified':
                    self.names[idx].trigger = trigger
                name = self.names[idx].function_name
                bogus_names = (
                "ros::TopicManager::subscribe", "ros::TopicManager::addSubCallback", "message_filters::Connection")
                if name in (function_name,) + bogus_names:
                    self.names[idx].function_name = function_name
                elif function_name in bogus_names:
                    pass
                else:
                    print("Duplicate", function_name, v.function_name)

                # ignore repeated additions, if name was present
                return
        self.names.append(fi)
        self.known_callbacks.add(key)

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
        num_unfinished = len(self.start_md)
        if num_unfinished > 0:
            print("%d unfinished invocations ignored" % num_unfinished)
        return TraceInfo(self.names, self.invocations, self.tasks, self.runtime, self.mtrace, self.delays)

    def handle_subscription_message_queued(self, e, md):
        key = FunctionKey(e, e['queue_ref'])
        self.queue_keys.add(key)
        #print("Added %s" % key)
        
    def handle_subscriber_callback_start(self, e, md):
        key = FunctionKey(e)
        self.start_md[key] = md
        self.start_cycles[key] = get_cycles(e)

    def handle_subscriber_callback_end(self, e, md):
        key = FunctionKey(e)
        if key in self.start_md:
            start_md = self.start_md[key]
            duration = md.timestamp - start_md.timestamp
            cycles = get_cycles(e) - self.start_cycles[key]
            trace_id =  get_trace_id(e)
            self.invocations.append(InvocationInfo(start_md, get_callback(e), duration, cycles, trace_id))

            # cleanup
            del self.start_md[key]
            del self.start_cycles[key]

    def handle_queue_delay(self, e, md):
        key = FunctionKey(e)
        delay = e['_timestamp'] - (float(e['start_time_sec']) + float(e['start_time_nsec']) / 1e9) * 1e9
        self.delays.append(DelayInfo(md, e['queue_name'], get_callback(e), delay))

    def handle_timer_scheduled(self, e, md):
        ref = e["callback_queue_cb_ref"]
        # this is the key that will appear in callback_start
        call_key = FunctionKey(e, ref)
        # but this is the key we have in known_callbacks
        real_key = FunctionKey(e)
        if real_key not in self.known_callbacks:
            print("Warning: Timer %s not in known callbacks" % real_key)
            cb_ref = real_key.callback_ref
            self._add_fi(e=e, md=md, function_name="timer-auto-%s" % cb_ref, cb_ref=cb_ref,
                         key=real_key, trigger='time')
        self.timer_map[call_key] = real_key

    def handle_callback_start(self, e, md):
        key = FunctionKey(e)
        if key in self.timer_map:
            key = self.timer_map[key]
            if key not in self.known_callbacks:
                print("Timer key %s not in known_callbacks on start -- must not happen!" % key)
        # ignore if subscription-related
        elif key in self.queue_keys:
            return 

        # handle functions we didn't get name_info for
        if key not in self.known_callbacks:
            if get_trace_id(e) != 0:
                cb_ref = get_callback(e)
                self._add_fi(e, md, "%s::%d" % (e['procname'], cb_ref), cb_ref, key)
            else:
                pass#self.not_found.add(e)
                
        self.start_md[key] = md
        self.start_cycles[key] = get_cycles(e)
        
    def handle_callback_end(self, e, md):
        key = FunctionKey(e)
        if key in self.timer_map:
            key = self.timer_map[key]
        elif key in self.queue_keys:
            #self.queue_keys.discard(key)
            return
        
        if key not in self.known_callbacks:
            self.missing_keys[key].append(e)
            #print("Callback %x found neither in known_callbacks nor in timer_map" % key.callback_ref)
            return
        
        try:
            start_md = self.start_md[key]
            duration = md.timestamp - start_md.timestamp
            cycles = get_cycles(e) - self.start_cycles[key]
            trace_id = get_trace_id(e)
            self.invocations.append(InvocationInfo(start_md, key.callback_ref, duration, cycles, trace_id))

            # cleanup
            del self.start_md[key]
            del self.start_cycles[key]
            try:
                del self.timer_map[key]
            except:
                pass
        except KeyError as e:
            print("No start time for", e)
    
    def handle_name_info(self, e, md):
        self._add_fi(e, md, split_function_name(get_m_name(e)), get_callback(e), FunctionKey(e))

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

    print("Missing callbacks: ", "\n".join(["%s\t%d" % (key, len(value)) for key, value in m.missing_keys.items()]))
    return m.create_trace_info()


def get_name(e):
    return e['_name']


def get_instructions(e):
    return e['perf_thread_instructions']


def get_t_name(e):
    return e['task_name']

def get_trace_id(e):
    tid = 0
    if 'trace_id' in e:
        tid =  e['trace_id']
    elif 'tracing_id' in e: # so much for consistency...
        tid = e['tracing_id'] 

    return tid

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
