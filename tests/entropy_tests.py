import os
import pathlib
import unittest

import numpy as np

from eval.graph import PolicyGraphAndTrajectories


class TestEntropy(unittest.TestCase):
    def setUp(self) -> None:
        transitions_file = "policygraphs/pg_test_purpose_edges.csv"
        state_file = "policygraphs/pg_test_purpose_nodes.csv"
        state_type = "Propositional"
        self.pg = PolicyGraphAndTrajectories()
        self.pg.load_graph_from_files(transitions_file, state_file, state_type)

    def test_loaded_graph_entropy_node0(self):
        expectedAgentEntropy = 0.5+0.5  # action 0 and action 1
        expectedWorldEntropy = 0  # Deterministic
        expectedGlobalEntropy = expectedAgentEntropy
        self.assertEqual(self.pg.compute_state_agent_capture_entropy(0), expectedAgentEntropy)
        self.assertEqual(self.pg.compute_state_world_capture_entropy(0), expectedWorldEntropy)
        self.assertEqual(self.pg.compute_state_global_entropy(0), expectedGlobalEntropy)

    def test_loaded_graph_entropy_node1(self):
        expectedAgentEntropy = 0  # Deterministic (always action 0)
        expectedWorldEntropy = 0.5 + 0.5  # Fully stochastic (either s0 or s1 equal prob
        expectedGlobalEntropy = expectedWorldEntropy
        self.assertEqual(self.pg.compute_state_agent_capture_entropy(1), expectedAgentEntropy)
        self.assertEqual(self.pg.compute_state_world_capture_entropy(1), expectedWorldEntropy)
        self.assertEqual(self.pg.compute_state_global_entropy(1), expectedGlobalEntropy)
