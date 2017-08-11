class TraceMetaData(object):
    process_id = None
    task_id = None
    node_name = None
    timestamp = None

    def __init__(self, node_name, process_id, task_id, timestamp):
        self.node_name = node_name
        self.process_id = process_id
        self.task_id = task_id
        self.timestamp = timestamp

class TraceEvent(object):
    def __init__(self, metadata):
        self.metadata = metadata

    @property
    def task_id(self):
        return self.metadata.task_id

    @property
    def process_id(self):
        return self.metadata.process_id

    @property
    def node_name(self):
        return self.metadata.node_name

    @property
    def timestamp(self):
        return self.metadata.timestamp


class ActionIntervalData(object):
    """Captures the extent of actions executed by the system"""
    def __init__(self, start, end, action, result):
        """
        :param md: Event metadata
        :param start: Start timestamp
        :param end: End timestamp
        :param action: Name of the action (its type), should be the same for grouping.
        :param result: True for success, false otherwise
        :param details: If specified, the instance-specific details of the action.
        """

        self.start = start
        self.end = end
        self.action = action
        self.result = result


class TaskInfo(TraceEvent):
    task_name = None

    def __init__(self, md, task_name):
        TraceEvent.__init__(self, md)
        self.task_name = task_name


class DelayInfo(TraceEvent):
    queue_name = None
    delay = 0

    def __init__(self, md, queue_name, callback_ref, delay):
        TraceEvent.__init__(self, md)
        self.queue_name = queue_name
        self.callback_ref = callback_ref
        self.delay = delay


class RuntimeStatsInfo(TraceEvent):
    node_id = None
    on_cpu = None
    sleep_time = None
    wait_time = None

    def __init__(self, md, node_id, on_cpu=None, sleep_time=None, wait_time=None):
        TraceEvent.__init__(self, md)
        self.node_id = node_id
        self.on_cpu = on_cpu
        self.sleep_time = sleep_time
        self.wait_time = wait_time


class RuntimeCPUInfo(TraceEvent):
    ref = None
    cycles_delta = None
    instructions_delta = None

    def __init__(self, md, ref, cycles_delta, instructions_delta):
        TraceEvent.__init__(self, md)
        self.ref = ref
        self.cycles_delta = cycles_delta
        self.instructions_delta = instructions_delta


class FunctionInfo(TraceEvent):
    function_name = None
    cb_ref = None
    trigger = None

    def __init__(self, md, function_name, cb_ref, trigger='unspecified'):
        """
        :param trigger: The kind of trigger -- use "time" for timers or "data" for subscriptions
        """
        TraceEvent.__init__(self, md)
        self.function_name = function_name
        self.cb_ref = cb_ref
        self.trigger = trigger

    def __eq__(self, other):
        return hasattr(other, 'function_name') and hasattr(other, 'cb_ref') and \
            self.function_name == other.function_name and self.cb_ref == other.cb_ref

    def __hash__(self):
        return hash((self.function_name, self.cb_ref, self.trigger))

    def __repr__(self):
        return "Function(name=%s, cb_ref=%s, trigger=%s)" % (self.function_name, self.cb_ref, self.trigger)


class InvocationInfo(TraceEvent):
    cb_ref = None
    duration = None
    cycles = None

    def __init__(self, md, cb_ref, duration, cycles, trace_id):
        """

        :param start:
        :param cb_ref:
        :param duration:
        :param cycles:
        :param trace_id: Identifier to distinguish to logically separate invocations of the same
            function, e.g. in separate threads.
        :return:
        """
        TraceEvent.__init__(self, md)
        self.cb_ref = cb_ref
        self.duration = duration
        self.cycles = cycles
        self.trace_id = trace_id


class MessageTraceInfo(TraceEvent):
    message_name = None
    callback_ref = None
    receipt_time = None

    def __init__(self, md, message_name, callback_ref, receipt_time):
        TraceEvent.__init__(self, md)
        self.message_name = message_name
        self.callback_ref = callback_ref
        self.receipt_time = receipt_time


class TraceInfo:
    functions = None
    invocations = None
    tasks = None
    runtime = None
    mtrace = None
    delays = None

    def __init__(self, functions, invocations, tasks, runtime, message_trace, delays, actions=None):
        self.functions = functions
        self.invocations = invocations
        self.tasks = tasks
        self.runtime = runtime
        self.mtrace = message_trace
        self.delays = delays
        self.actions = actions

    def __iter__(self):
        return (self.functions, self.invocations, self.tasks, self.runtime, self.mtrace, self.actions).__iter__()


def load_pickle(filename, map_fn, filter_fn=None):
    import pickle
    elements = []
    with open(filename, "rb") as f:
        up = pickle.Unpickler(f)
        while True:
            try:
                elements.append(up.load())
            except EOFError as e:
                break  # we're done
    # optional filter
    if filter_fn is not None:
        elements = [e for e in elements if filter_fn(e)]

    return map_fn(elements)


def load_pod(pods, map_fn, filter_fn=None):
    import pickle
    elements = []
    for pod in pods:
        up = pickle.Unpickler(f)
        while True:
            try:
                elements.append(up.load())
            except EOFError as e:
                break  # we're done
    # optional filter
    if filter_fn is not None:
        elements = [e for e in elements if filter_fn(e)]

    return map_fn(elements)
