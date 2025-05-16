import unittest

from eval.graph import PolicyGraphAndTrajectories


class TestDesires(unittest.TestCase):
    def setUp(self) -> None:
        transitions_file = "policygraphs/pg_test_purpose_edges.csv"
        state_file = "policygraphs/pg_test_purpose_nodes.csv"
        state_type = "Propositional"
        self.pg = PolicyGraphAndTrajectories()
        self.pg.load_graph_from_files(transitions_file, state_file, state_type)

    def test_number_of_states_with_desire(self):
        clause = {'SOMETHING'}
        action_idx = '0'
        desire = (clause, action_idx)
        expected_number_of_states_with_desire = 1
        expected_desire_fulfillment_probabability = 1.0

        action_prob_distribution, nodes_fulfilled = self.pg.compute_desire_statistics(desire)
        action_probability_in_single_state = action_prob_distribution[0]

        self.assertEqual(expected_number_of_states_with_desire, len(nodes_fulfilled))
        self.assertEqual(expected_desire_fulfillment_probabability, action_probability_in_single_state)
