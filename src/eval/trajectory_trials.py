import argparse
from typing import List

from domain.desire import Desire
from eval.desire_trials import get_desires
from eval.graph import PolicyGraphAndTrajectories

import csv
import numpy as np


def pg_from(domain, disc):
    transitions_file, state_file = f"policygraphs/pg_{domain}_{disc}_edges.csv", \
                                   f"policygraphs/pg_{domain}_{disc}_nodes.csv"
    state_type = "Propositional"
    x = PolicyGraphAndTrajectories()
    x.load_graph_from_files(transitions_file, state_file, state_type)
    return x

action_idx_to_name = {'0': 'UP', '1': 'DOWN', '2': 'RIGHT', '3': 'LEFT', '4': 'STAY', '5': 'Interact'}

def exp_extract_metrics(args):
    np.random.seed(args.seed)
    commitment_threshold = args.com_threshold
    from matplotlib import pyplot as plt
    for domain in args.domains:
        desires: List[Desire] = get_desires(only_one_pot=domain == 'simple')
        for disc in args.discretisers:
            x = pg_from(domain, disc)
            x.register_all_desires(desires)
            ini_state = x.nodes[0]
            current = ini_state
            intention_track = []
            desire_fulfill_track = {}
            episode_length = 100
            state_list = []
            for t in range(episode_length):
                current_intentions = current.intention
                intention_track.append(current_intentions)
                try:
                    next_action, next_state_id = current.sample_next_state()
                    state_list.append(next_state_id)
                    print('\t', current.state_rep)
                    print(current_intentions)
                    print(action_idx_to_name[next_action])
                    for desire in desires:
                        d_name = desire.name
                        clause = desire.clause
                        action_idx = desire.action_idx
                        ret = current.check_desire(clause, action_idx)
                        if ret is not None and action_idx == next_action:
                            print('   ', d_name, 'FULFILLED')
                            desire_fulfill_track[t] = d_name
                    current = x.nodes[next_state_id]
                except ValueError:
                    print(f'Episode ended earlier due to childless-state: {current.node_id}')
                    break

            desire_names = [d.name for d in desires]
            desire_color = {d_name: c for d_name, c in zip(desire_names, plt.cm.get_cmap('Set1').colors)}
            for desire in desires:
                d_name = desire.name
                intention_vals = [entry.get(d_name, 0) for entry in intention_track]
                plt.plot(range(episode_length), intention_vals, label=d_name, color=desire_color[d_name],
                         linestyle='dotted')
            plt.legend()
            for t, d_name in desire_fulfill_track.items():
                plt.vlines(t, -0.05, 1.05, label=d_name, colors=desire_color[d_name], linestyles='-')
            plt.title(f'Simulated Intention evolution in {domain}-D{disc}')
            plt.show()
        print(state_list)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-do",
        "--domains",
        nargs="+",
        type=str,
        help="Domains to analyse"
    )
    parser.add_argument(
        "-dc",
        "--discretisers",
        nargs="+",
        type=int,
        help="Discretisers"
    )
    parser.add_argument(
        "-cth",
        "--com_threshold",
        type=float,
        default=0.5,
        help="Commitment Threshold"
    )
    parser.add_argument(
        "-s",
        "--seed",
        type=int,
        default=42,
        help="Random seed for sampling"
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    # exp_intention_metrics()
    exp_extract_metrics(args)
