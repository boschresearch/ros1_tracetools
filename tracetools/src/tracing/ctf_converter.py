import babeltrace
from pickle import Pickler
import time

__all__ = ['convert']

# CTF internal fields that we don't need
LTT_FIELDS = ('timestamp_end', 'stream_id', 'timestamp_begin', 'v', 'cpu_id', 'uuid', 'packet_size', 'magic', 'id',
              'events_discarded')

DISCARD = "events_discarded"


def element_to_pod(ctf_element):
    """
    Convert name, timestamp, and all other keys except those in LTT_FIELDS into a dictionary.
    :param ctf_element: The element to convert
    :type ctf_element: babeltrace.Element
    :return:
    :return type: dict
    """
    pod = {'_name': ctf_element.name, '_timestamp': ctf_element.timestamp}
    if hasattr(ctf_element, DISCARD) and ctf_element[DISCARD] > 0:
        print(ctf_element[DISCARD])
    for key in [key for key in ctf_element.keys() if key not in LTT_FIELDS]:
        pod[key] = ctf_element[key]
    return pod


def pickle(target_filename, elements):
    print("Dumped %d elements to %s" % (len(elements), target_filename))


class ListTarget:
    def __init__(self):
        self.contents = []

    def dump(self, pod):
        return self.contents.append(pod)


def convert(tracename, target, names=None):
    """
    Loads trace events and dumps them to the given target using pickle.
    :param tracename: The directory to load the traces from
    :param target_filename: The filename to write to
    :return: None
    """
    # add traces
    tc = babeltrace.TraceCollection()

    print("Importing %s" % tracename)
    tc.add_traces_recursive(tracename, "ctf")

    count = 0
    count_written = 0
    count_pid_matched = 0
    traced = set()

    PID_KEYS = ("vpid", "pid")

    start_time = time.time()

    for event in tc.events:
        count += 1
        pid = None
        for key in PID_KEYS:
            if key in event.keys():
                pid = event[key]
                break

        towrite = False
        if names is None or event.name in names:
            if event.name.startswith("roscpp:"):
                # remember ROS processes
                if event.name == "roscpp:init_node":
                    traced.add(pid)
                towrite = True
            elif pid in traced:
                towrite = True
                count_pid_matched += 1

            if towrite:
                target.dump(element_to_pod(event))
                count_written += 1

        # for long traces, give an intermediate output
        if count % 100000 == 0:
            print("%8.2f Converted %10d of %10d elements (%10d matched by PID)"
                  % (time.time() - start_time, count_written, count, count_pid_matched))

    print("%d elements in total" % count)
