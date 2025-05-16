from pprint import pprint
from typing import List, Tuple, Set

from matplotlib import pyplot as plt

from eval.desire_trials import get_desires
from eval.utils import pg_from
from eval.graph import PolicyGraphAndTrajectories, Node

action_idx_to_name = {'0': 'UP', '1': 'DOWN', '2': 'RIGHT', '3': 'LEFT', '4': 'STAY', '5': 'Interact'}

def what_experiment(pg, node_idx, C_threshold):
    print(pg.nodes[node_idx].get_attributed_intentions(C_threshold))#.keys())

def how_experiment(pg, node_idx, desire):
    node = pg.nodes[node_idx]
    paths = node.answer_how(desires=[desire], stochastic=False)
    if paths is None:
        return
    printable_paths = {}
    for desire, path in paths.items():
        print(path)
        curr_state = node
        path_staging = []
        for action, new_state, new_intention in path[:-1]:
            a=action_idx_to_name[action]
            pred_difs = curr_state.compute_differences(new_state)
            equal, added, removed = pred_difs
            path_staging.append((a, {'Added':added, 'Removed':removed}, new_intention))
            curr_state = new_state
        path_staging.append((action_idx_to_name[path[-1][0]]))
        printable_paths[desire] = path_staging
    for desire, path in printable_paths.items():
        print(desire, "from the node description:")
        pprint(node.state_rep)
        pprint(path)


def how_stochastic(pg, node_idx, desire, C_threshold, num_paths_per_desire = 10):
    node = pg.nodes[node_idx]
    paths = node.answer_how(desire, stochastic=True, c_threshold=C_threshold, num_paths_per_desire =num_paths_per_desire)
    printable_paths = {}
    for desire in paths.keys():
        printable_paths[desire] = {'SUCCESS':[],'FAILURE':[]}
    for desire, stage in paths.items():
        for success, paths in stage.items():
            for path in paths:
                curr_state = node
                path_staging = []
                for action, new_state, new_intention in path[:-1]:
                    a = action_idx_to_name[action]
                    pred_difs = curr_state.compute_differences(new_state)
                    equal, added, removed = pred_difs
                    path_staging.append((a, {'Added': added, 'Removed': removed}, new_intention))
                    curr_state = new_state
                path_staging.append((action_idx_to_name[path[-1][0]]))
                printable_paths[desire][success].append(path_staging)
    for desire, stage in printable_paths.items():
        print(desire, "from the node description:")
        pprint(node.state_rep)
        print("Successful paths:", len(stage['SUCCESS']), "Failed paths:", len(stage['FAILURE']))
        print("Successes:")
        for path in stage['SUCCESS']:
            pprint(path)
        print("Failures:")
        for path in stage['FAILURE']:
            pprint(path)


def why_experiment(pg, node_idx, action_idx,  c_threshold):
    node = pg.nodes[node_idx]
    ints = node.answer_why(action_idx, c_threshold= c_threshold)
    # print("Intentions returned by why", ints)
    if ints == {}:
        print("Action does not seem intentional.")
    for d, info in ints.items():
        print(f'I want to do {action_idx_to_name[action_idx]} for the purpose of furthering {d} as', end=' ')
        if info['expected'] > 0:
            print(f"it is expected to increase my intention by {info['expected']:.2f}")
        elif info['expected'] == 0:
            print(f"it will keep my intention of fulfilling it the same.")
        else:
            print(f"it has a {info['prob_increase']:.2f} probability of an expected intention "
                  f"increase of {info['expected_pos_increase']:.2f}")

def xai_experiment(domain, disc, C_th, node_idx, action_idx_for_why, stochastic_how=False):
    x: PolicyGraphAndTrajectories = pg_from(domain, disc)
    desires = get_desires(only_one_pot=domain=='simple')
    for desire in desires:
        x.register_desire(desire)
    what_experiment(x, node_idx=node_idx, C_threshold = C_th)
    if stochastic_how:
        how_stochastic(x, node_idx=node_idx, desire = [desires[0]], C_threshold=0.5)
    else:
        how_experiment(x, node_idx=node_idx, desire = desires[0])
    why_experiment(x, node_idx=node_idx, action_idx=action_idx_for_why, c_threshold = C_th)


if __name__ == '__main__':
    domain, disc = 'simple', '14'
    C_th, node_idx, action_idx_for_why = 0.5, 11, '5'
    xai_experiment(domain, disc, C_th, node_idx, action_idx_for_why)