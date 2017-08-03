__author__ = 'ingo'

__all__ = ['pickle2pd', 'merge_names']

import pickle
import pandas as pd
import subprocess
import re
from .lttng_model import *
from .ros_mapping import map_roscpp


class TracePD(object):
    functions = None
    invocations = None
    tasks = None
    runtime = None
    mtrace = None
    delays = None

    def __init__(self, functions, invocations, tasks, runtime, message_trace, delays):
        self.functions = functions
        self.invocations = invocations
        self.tasks = tasks
        self.runtime = runtime
        self.mtrace = message_trace
        self.delays = delays

    def by_node(self, nodename):
        task_id = self.tasks.loc
        self.invocations.merge(
            self.tasks,
            left_on="task_id",
            right_on="task_id")


def ti2pd(ti):
    """Convert an lttng_model.TraceInfo structure to a Pandas data-frame"""
    function_tasks = [t.task_id for t in ti.functions]
    function_addrs = [t.cb_ref for t in ti.functions]
    functions_df = pd.DataFrame(data={
        'function_name': [t.function_name for t in ti.functions],
        'callback': function_addrs,
        'task_id': function_tasks,
    }, index=[function_tasks, function_addrs])

    # filter out functions where we didn't get a meaningful name
    functions_df = functions_df[functions_df['function_name'] != "ros::TopicManager::subscribe"]

    invocations_timestamps = [pd.Timestamp(t.timestamp) for t in ti.invocations]
    invocation_tasks = [t.task_id for t in ti.invocations]
    invocation_cbs = [t.cb_ref for t in ti.invocations]
    invocations_df = pd.DataFrame(data={
        'starts': invocations_timestamps,
        'node': [t.node_name for t in ti.invocations],
        'task_id': invocation_tasks,
        'callback': invocation_cbs,
        'duration': [t.duration for t in ti.invocations],
        'cycles': [t.cycles for t in ti.invocations]
    }, index=invocations_timestamps)

    task_nodes = [t.node_name for t in ti.tasks]
    task_ids = [t.task_id for t in ti.tasks]
    tasks_df = pd.DataFrame(data={
        'task_id': task_ids,
        'task_name': [t.task_name for t in ti.tasks],
        'node': task_nodes
    }, index=task_ids)

    runtime_timestamps = [pd.Timestamp(t.timestamp) for t in ti.runtime]
    runtime_df = pd.DataFrame(data={
        'timestamp': runtime_timestamps,
        'node_id': [t.node_id for t in ti.runtime],
        'task_id': [t.task_id for t in ti.runtime],
        'on_cpu': [t.on_cpu for t in ti.runtime],
        'sleep_time': [t.sleep_time for t in ti.runtime],
        'wait_time': [t.wait_time for t in ti.runtime],
    }, index=runtime_timestamps)

    mtrace_timestamps = [pd.Timestamp(t.timestamp) for t in ti.mtrace]
    mtrace_df = pd.DataFrame(data={
        'timestamp': mtrace_timestamps,
        'message_name': [t.message_name for t in ti.mtrace],
        'callback_ref': [t.callback_ref for t in ti.mtrace],
        'receipt_time': [pd.Timestamp(t.receipt_time) for t in ti.mtrace]
    }, index=mtrace_timestamps)

    delays_timestamps = [pd.Timestamp(t.timestamp) for t in ti.delays]
    delays_df = pd.DataFrame(data={
        'delay': [t.delay for t in ti.delays],
        'queue_name': [t.queue_name for t in ti.delays],
        'callback_ref': [t.callback_ref for t in ti.delays],
        'node_name': [t.node_name for t in ti.delays],
        'task_id': [t.task_id for t in ti.delays],
    }, index=delays_timestamps)

    return TracePD(functions_df, invocations_df, tasks_df, runtime_df, mtrace_df, delays_df)


def pickle2pd(filename, map_fn):
    return ti2pd(load_pickle(filename, map_fn))



def merge_names(trace_pd):
    return pd.merge(trace_pd.invocations, trace_pd.functions, left_on=("callback", "task_id"),
                    right_on=("callback", "task_id"), how="left", sort=False).\
        merge(trace_pd.tasks, left_on="task_id", right_on="task_id", how="left", sort=False)


def task_statistics(trace_pd):
    """

    :param trace_pd:
    :type trace_pd: TracePD
    :return:
    """
    pass

