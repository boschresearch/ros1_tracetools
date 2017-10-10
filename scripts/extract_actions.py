#! /usr/bin/env python2
#
# Reads actions from a bag file. Has to be a secondary script because 
# of Python2/Python3 issues within rosbag
#

import sys
import rosbag
import pickle
from actionlib_msgs.msg import GoalStatus
from tracing.lttng_model import ActionIntervalData

if __name__ == '__main__':
    bagfile = rosbag.Bag(sys.argv[1])
    
    active_actions = {}
    completed_actions = {}
    
    # scan bagfile for actions
    for topic, msg, t in bagfile.read_messages():
        # feedback messages contain status info
        if topic.endswith("/feedback") or topic.endswith("/result"):
            if hasattr(msg, "status"):
                key = msg.status.goal_id.id
                status = msg.status.status
                action = "/".join(topic.split("/")[1:-1])
                # keep the first message with an active status, to remember its start time
                if status == GoalStatus.ACTIVE and key not in active_actions:
                    #print(msg)
                    active_actions[key] = (action, msg)
                elif status in (GoalStatus.SUCCEEDED, GoalStatus.ABORTED, GoalStatus.RECALLED, GoalStatus.PREEMPTED):
                    if key not in active_actions and key not in completed_actions:
                        #print("Got end for unknown action", msg)
                        continue
                    action, start = active_actions[key]
                    completed_actions[key] = ActionIntervalData(start.header.stamp.to_time() * 1e9,
                        msg.header.stamp.to_time() * 1e9, action, msg.status.status == GoalStatus.SUCCEEDED)
                    del active_actions[key]

    #print to_pd(completed_actions.values())
    # dump data on stdout
    pickle.Pickler(sys.stdout).dump(completed_actions.values())
    sys.stdout.flush()
    