#! /usr/bin/env python3

import unittest
import tracing.experiment as exp
import subprocess

PKG = 'tracetools'


class ExperimentRunnerTest(unittest.TestCase):
    SESSION_NAME="my_testing_session"

    def setUp(self):
        # destroy any left-overs, but don't care if it goes badly
        subprocess.call(["lttng", "destroy"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.experiment = exp.TraceExperiment(["rosrun", "test_tools", "test_echo"],
                                              userspace_events=exp.ROSCPP_TRACE_EVENTS)

    def tearDown(self):
        subprocess.call(["lttng", "destroy"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def test_create(self):
        self.experiment.create()
        subprocess.check_call(["lttng", "enable-event", "-u", "roscpp:node_init"], stdout=subprocess.PIPE)

    def test_create_name(self):
        self.experiment.create(self.SESSION_NAME)
        output = subprocess.check_output(["lttng", "list"], universal_newlines=True)
        self.assertTrue(self.SESSION_NAME in output)

    def test_trace(self):
        self.experiment.create()
        self.experiment.run()
        result = self.experiment.collect_data()
        self.assertGreater(len(result), 0)


if __name__ == '__main__':
    import rostest

    rostest.rosrun(PKG, "test_experiment_runner", ExperimentRunnerTest)
