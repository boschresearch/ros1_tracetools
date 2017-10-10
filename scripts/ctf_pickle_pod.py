#!/usr/bin/env python3
# Simple script to convert CTF data into a pickle file containing plain-old-datastructures (dicts with the elements
# fields)
#

__author__ = 'ingo'

from tracing.ctf_converter import convert
from pickle import Pickler

if __name__ == '__main__':
    import sys

    names = None
    if len(sys.argv) > 3:
        names = sys.argv[3].split(",")
        for info_name in ("roscpp:ptr_name_info", "roscpp:task_start", "roscpp:init_node", "tf2:task_start", "roscpp:timer_added"):
          names.append(info_name)

    with open(sys.argv[2], "wb") as f:
        p = Pickler(f, protocol=4)
        convert(sys.argv[1], p, names)
