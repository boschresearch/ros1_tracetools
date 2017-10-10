#! /usr/bin/env python3

import sys
from tracing.analysis import *
import tracing.trace_pandas as tp
import pickle
import subprocess

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Syntax: %s pickle-file [bagfile]" % sys.argv[0])
    df = load_as_pd(sys.argv[1])
    if len(sys.argv) > 2:
        bagfile=sys.argv[2]
        proc = subprocess.Popen(["rosrun", "tracetools", "extract_actions.py", bagfile], stdout=subprocess.PIPE)
        retcode = proc.wait()
        actions = tp.actions_to_df(pickle.Unpickler(proc.stdout).load())
        if retcode == 0:
            df.actions=actions
        else:
            print("Bag reader encountered an error")

    target_filename = sys.argv[1].replace(".pickle", ".pd.pickle")
    tp.dump(target_filename, df)
    
