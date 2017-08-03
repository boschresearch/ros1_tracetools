#! /usr/bin/env python3
# read actions from a rosbag and them to the pandas dataframe with tracing information
#

from __future__ import print_function

import sys
import pickle
import pickle
import pandas as pd
import subprocess
import io
import tracing.trace_pandas as tp


def to_pd(action_infos):
    return pd.DataFrame(data={
        'action': [t.action for t in action_infos],
        'starts': [pd.Timestamp(t.start) for t in action_infos],
        'duration': [pd.Timedelta(t.end - t.start) for t in action_infos],
        'result': [t.result for t in action_infos],
    })


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Syntax: %s <bagfile> <tracing-info>" % sys.argv[0])
        sys.exit(-1)

    # open inputs
    with open(sys.argv[2], 'rb') as f:
        df = pickle.Unpickler(f).load()
    
    # execute secondary script (because of Python2/3 issues)
    proc = subprocess.Popen(["rosrun", "tracetools", "extract_actions.py", sys.argv[1]], stdout=subprocess.PIPE)
    
    # load data
    retcode = proc.wait()
    actions = to_pd(pickle.Unpickler(proc.stdout).load())
    if retcode != 0:
        print("Bag reader encountered an error")
        sys.exit(-1)

    # store
    df.actions = actions
    tp.dump(sys.argv[2], df)