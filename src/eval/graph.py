import csv
import functools
from typing import Callable, List, Set, Iterable, Tuple, Dict, Any, Union

import numpy as np
from tqdm import tqdm

from domain.desire import Desire
from domain.node import Node, PropoNode


class PolicyGraphAndTrajectories:
    TRANSITION_NODE_SOURCE = 0
    TRANSITION_NODE_DEST = 1
    TRANSITION_NODE_ACTION = 2
    TRANSITION_NODE_PROB = 3

    def __init__(self, verbose=False):
        self.transitions: Dict = {}
        # self.transitions = {n_idx: {action1:{dest_node1: P(dest1, action1|n_idx), ...}
        self.nodes: List = []
        # self.transitions = [Node1, Node2...]
        self._min_transition_prob: float = 0.
        self.verbose=verbose

    def load_graph_from_files(self, transitions_file, state_file, state_type):
        if state_type == 'Propositional':
            self._load_propo_states(state_file)
        self._load_transitions(transitions_file)
        self.__verify()
        self._min_transition_prob = 0.
        # TODO: Refactor this, e.g. create "structure" class
        for node in self.nodes:
            node.nodes = self.nodes
            node.transitions = self.transitions

    def compute_node_probability(self):
        pass

    def compute_information_loss(self, node_pair):
        pass

    def get_coinciders_into_descendants(self, node):
        pass

    def get_action_probability(self, node_idx):
        try:
            p_dist = self.transitions[node_idx]
            action_prob_distro = dict()
            for action_idx, dest_state_distr in p_dist.items():
                action_prob_distro[action_idx] = sum([p for p in dest_state_distr.values()])
            return action_prob_distro
        except KeyError:
            if self.verbose:
                print(f'Warning: State {node_idx} has no sampled successors which were asked for')
            return dict()

    def compute_likelihood(self, trajectory_data: List[List[Tuple[Union[str, int], Union[int, str]]]]) -> float:
        loglikelihood = 0
        for trajectory in trajectory_data:
            loglikelihood -= np.log2(self.nodes[int(trajectory[0][0])].probability)
            for i, (node_idx, action) in enumerate(trajectory):
                if i >= len(trajectory) - 1:
                    break
                next_state = trajectory[i + 1][0]
                try:
                    loglikelihood -= np.log2(self.transitions[node_idx][action][next_state])
                except KeyError as ex:
                    # In case of an unseen transition assume the worst possible probability
                    loglikelihood -= np.log2(self.min_trasition_prob)
        return loglikelihood


    @property
    def min_trasition_prob(self):
        if self._min_transition_prob == 0:
            self._min_transition_prob = np.array(
                [v for a in self.transitions.values() for b in a.values() for v in b.values()]).min()
        return self._min_transition_prob


    def compute_entropy(self, type: str):
        if type == 'global':
            selected_entropy = self.compute_state_global_entropy
        elif type == 'agent':
            selected_entropy = self.compute_state_agent_capture_entropy
        elif type == 'world':
            selected_entropy = self.compute_state_world_capture_entropy
        else:
            raise NotImplementedError()
        entropy = 0
        for n_idx in self.transitions.keys():
            entropy += self.nodes[n_idx].probability * selected_entropy(n_idx)
        return entropy


    def compute_intentional_entropy(self, type: str, weight_factor=3):
        if type == 'global':
            selected_entropy = self.compute_state_global_entropy
        elif type == 'agent':
            selected_entropy = self.compute_state_agent_capture_entropy
        elif type == 'world':
            selected_entropy = self.compute_state_world_capture_entropy
        else:
            raise NotImplementedError()
        entropy = 0
        total_intention = 0
        for n_idx in self.transitions.keys():
            node_entropy = self.nodes[n_idx].probability * selected_entropy(n_idx)
            intention = self.nodes[n_idx].max_intention()
            total_intention += intention*self.nodes[n_idx].probability
            intention_impact = weight_factor*intention
            entropy += node_entropy*(1+intention_impact)/(1+weight_factor)
        return entropy, total_intention

    def compute_selective_entropy(self, accept_func: Callable[['Node'], bool], type: str):
        if type == 'global':
            selected_entropy = self.compute_state_global_entropy
        elif type == 'agent':
            selected_entropy = self.compute_state_agent_capture_entropy
        elif type == 'world':
            selected_entropy = self.compute_state_world_capture_entropy
        else:
            raise NotImplementedError()
        entropy = 0
        total_prob = 0
        for n_idx in self.transitions.keys():
            if accept_func(self.nodes[n_idx]):
                node_prob = self.nodes[n_idx].probability
                entropy += node_prob * selected_entropy(n_idx)
                total_prob += node_prob
        return entropy/total_prob, entropy, total_prob

    def compute_state_global_entropy(self, node_idx):
        # H_g(s) = sum forall (s',a) in transitions from s P(s', a|s) *log P(s', a|s)
        node_transitions = self.transitions[node_idx]
        accumulated_entropy = 0
        for action, action_trans in node_transitions.items():
            for v in action_trans.values():
                assert v > 0
                accumulated_entropy -= v*np.log2(v)
        return accumulated_entropy

    def compute_state_world_capture_entropy(self, node_idx):
        # H_w(s) = sum forall (a) in transitions from s P(a|s)*forall (s' in transitions from s,a)
        #                                       [P(s'|a,s)] *log [P(s'|a,s)]
        node_transitions = self.transitions[node_idx]
        accumulated_expected_entropy = 0
        for action, action_trans in node_transitions.items():
            p_a__s = np.array([v for v in action_trans.values()]).sum()  # P(a|s)
            assert p_a__s > 0
            accumulated_entropy = 0
            for p_ss_a__s in action_trans.values():  # P(s',a|s)
                assert p_ss_a__s > 0
                p_ss__a_s = p_ss_a__s/p_a__s  # P(s'|s,a)
                accumulated_entropy -= p_ss__a_s * np.log2(p_ss__a_s)
            accumulated_expected_entropy += p_a__s*accumulated_entropy
        return accumulated_expected_entropy

    def compute_state_agent_capture_entropy(self, node_idx):
        # H_a(s) = sum forall (a) in transitions from s P(a|s)*log P(a|s) =
        #  sum forall(a) ... sum s' [P(s',a|s)] *log (sum s' [P(s',a|s)])
        node_transitions = self.transitions[node_idx]
        accumulated_entropy = 0
        for action, action_trans in node_transitions.items():
            p_a_s = np.array([v for v in action_trans.values()]).sum() # P(a|s)
            assert p_a_s > 0
            accumulated_entropy -= p_a_s*np.log2(p_a_s)
        return accumulated_entropy

    def _load_transitions(self, transitions_file):
        with open(transitions_file, 'r') as f:
            reader = csv.reader(f)
            next(reader)
            self.transitions = {}

            for row in reader:
                src = int(row[self.TRANSITION_NODE_SOURCE])
                act = row[self.TRANSITION_NODE_ACTION]
                dest = int(row[self.TRANSITION_NODE_DEST])
                prob = float(row[self.TRANSITION_NODE_PROB])
                src_node = self.transitions.get(src, {})
                act_node = src_node.get(act, {})
                act_node[dest] = prob
                src_node[act] = act_node
                self.transitions[src] = src_node
                self.nodes[dest].coinciders.add(src)

    def _load_propo_states(self, state_file):
        with open(state_file, 'r') as f:
            reader = csv.reader(f)
            next(reader)

            self.nodes = [PropoNode(int(n_id), float(p), state_rep, self.nodes, self.transitions, self) for n_id, state_rep, p in reader]

    def compute_desire_statistics(self, desire):
        action_prob_distribution = []
        nodes_fulfilled = []
        clause, action_idx = desire.clause, desire.action_idx
        for node in self.nodes:
            p = node.check_desire(clause, action_idx)
            if p is not None:
                action_prob_distribution.append(p)
                nodes_fulfilled.append(node)

        return action_prob_distribution, nodes_fulfilled

    def register_desire(self, desire: Desire):
        for node in self.nodes:
            p = node.check_desire(desire.clause, desire.action_idx)
            if p is not None:
                node.propagate_intention(desire, p)
                # node.increase_desire(desire, p)

    def register_all_desires(self, desires: List[Desire]):
        for desire in desires:
            self.register_desire(desire)

    def compute_commitment_stats(self, desire_name, commitment_threshold):
        intention_score = []
        nodes_with_intent = []
        for node in tqdm(self.nodes):
            intention = node.intention.get(desire_name, 0)
            if intention >= commitment_threshold:
                intention_score.append(intention)
                nodes_with_intent.append(node)
        return intention_score, nodes_with_intent

    def __verify(self):
        for node in self.nodes:
            try:
                p_dist = self.transitions[node.node_id]
                total_proba = 0
                for action_trans in p_dist.values():
                    for p in action_trans.values():
                        total_proba += p
                if total_proba > 1+1e-5:
                    raise ValueError(f"Exceeding Probability at node {node.node_id}: {total_proba}")
            except KeyError:
                if self.verbose:
                    print(f'Warning: State {node.node_id} has no sampled successors in the edge file')
        pass
