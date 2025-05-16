from typing import List

# from pgmpy import BayesianNetwork

from eval.graph import PolicyGraphAndTrajectories, Node
import numpy as np


def get_variables_ascendent(dependence_list):
    variables = np.unique(np.array(dependence_list).flatten())
    return {var: [ascendent for ascendent, descendent in dependence_list if descendent == var] for var in variables}


class CPD_IDX:
    def __init__(self, var:str, orig_state_vars: List, dest_state_vars: List):
        self.var = var
        self.orig_vars = orig_state_vars
        self.dest_vars = dest_state_vars

    def get_values_orig(self, node: Node):
        return self._getvalues(node, self.orig_vars)

    def _getvalues(self, node, vars):
        for v in vars:
            if v == 'POT_STATE_POT0':
                pass
            else:
                pass

    @property
    def return_canonical_name(self):
        return self.var+'|'+' '.join(sorted(self.orig_vars+self.dest_vars))


class CPD_storage:
    def __init__(self, pg, action):
        self.stored_cpds = dict()
        self.pg = pg
        self.action = action

    def get_CPD(self, cpd_id: CPD_IDX):
        # cpd_id for P(A|B,C) = "A|B.C", with second part in SORTED order
        try:
            return self.stored_cpds[cpd_id.return_canonical_name]
        except KeyError:
            new_cpd = self._compute_cpd(cpd_id)
            self.stored_cpds[cpd_id] = new_cpd
            return new_cpd

    def _compute_cpd(self, cpd_id: CPD_IDX):
        for node_idx, action_to_futurestates in self.pg.transitions.items():
            try:
                future_node_probs = action_to_futurestates[self.action]
                orig_node = self.pg.nodes[node_idx]
                orig_var_vals = cpd_id.get_values_orig(orig_node)

            except KeyError:
                continue





def setup_graph(pg: PolicyGraphAndTrajectories, action: str, dependence_list: List):
    # Target model: P(s’, s|X) = P(s’a,sa,s’b, sb…|X) where s'_a and s_a are property a for a state and its successor
    dependence_list = [('A', 'C'), ('B', 'C')]
    variable_to_codependent = get_variables_ascendent(dependence_list)
    print(variable_to_codependent)

    # model = BayesianNetwork(dependence_list)

if __name__=='__main__':
    setup_graph(None, None, None)
