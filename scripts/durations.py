#! /usr/bin/env python3

import sys
from tracing.analysis import *

import pickle

DEFAULT_NAMES = ("costmap_2d", "mayfield_planer", "move_base::")
EXCLUDE_NAMES = ("message_filters",)

if __name__ == '__main__':
    p_data     = load_as_pd(sys.argv[1])

    invocations = select_invocations(p_data, lambda fn: any([text in fn for text in DEFAULT_NAMES]) and \
        not all([text in fn for text in EXCLUDE_NAMES]))
    print(fn_durations(invocations)/1e6)
