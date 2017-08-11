"""Analysis of lttng_model data."""
__author__ = 'Luetkebohle Ingo (CR/AEX3)'

import numpy as np
import pandas as pd
import time
from tracing.trace_pandas import ti2pd
from tracing.ros_mapping import map_roscpp
import pickle

def load(filename):
    with open(filename, "rb") as f:
        up = pickle.Unpickler(f)
        return up.load()
    
def load_as_pd(filename):
    data = load(filename)
    if "pd.pickle" in filename:
        return data
    else:
        return ti2pd(map_roscpp(data))    

def select_invocations(pd_df, fn_selector=lambda _: True, fields=("duration", "cycles")):
    """Merges invocations and functions table, and returns all function invocations where the function_name 
        is selected by the given selector function (default: all)"""
    cbs = pd.Series(data=[index for index, row in pd_df.functions.\
                            iterrows() if fn_selector(row["function_name"])]).unique()
    return pd_df.functions.loc[cbs].merge(pd_df.invocations, on='callback').\
        loc[:,("function_name", ) + fields]

def fn_durations(fi_pd, stats=[np.sum, np.median, np.std], sort_key=("duration", "sum")):
    """Compute median and standard deviation of aggregated invocation data."""
    return fi_pd.groupby('function_name').agg(stats).\
        sort_values(by=sort_key, ascending=False)