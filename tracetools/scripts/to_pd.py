#! /usr/bin/env python3

import sys
from tracing.analysis import *
from tracing.trace_pandas import ti2pd
from tracing.ros_mapping import map_roscpp
import pickle

if __name__ == '__main__':
    df = load_as_pd(sys.argv[1])
    
    target_filename = sys.argv[2] if len(sys.argv) > 2 else sys.argv[1].replace(".pickle", ".pd.pickle")
    with open(target_filename, "wb") as f:
        dumper = pickle.Pickler(f)
        dumper.dump(df)
