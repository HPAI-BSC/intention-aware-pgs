import argparse
from typing import List

from domain.desire import Desire
from eval.desire_trials import get_desires
from eval.graph import PolicyGraphAndTrajectories, Node
from eval.intention_trials import disc_to_string
from eval.utils import get_trajectory, pg_from

import csv
import numpy as np


action_idx_to_name = {'0': 'UP', '1': 'DOWN', '2': 'RIGHT', '3': 'LEFT', '4': 'STAY', '5': 'Interact'}


def exp_extract_trajectory_metrics(args, highlight_attr_int=False, s_proba=False):
    commitment_threshold = args.com_threshold
    from matplotlib import pyplot as plt
    for domain in args.domains:  # , 'simple']:
        desires: List[Desire] = get_desires(only_one_pot=domain == 'simple')
        for disc in args.discretisers:
            x = pg_from(domain, disc)
            x.register_all_desires(desires)
            for n in args.traj_ns:
                trajectory = get_trajectory(domain, disc, n)
                desire_fulfill_track, episode_length, intention_track, prob_track = \
                    trajectory_metrics_from_real(desires, trajectory, x)
                desire_names = [d.name for d in desires]
                desire_color = {d_name: c for d_name, c in zip(desire_names, plt.cm.get_cmap('Set1').colors)}
                fig = plt.figure(figsize=(episode_length / 25, 4))
                plt.xlim(left=0, right=episode_length)
                ax = plt.gca()
                for desire in desires:
                    d_name = desire.name
                    intention_vals = [entry.get(d_name, 0) for entry in intention_track]
                    ax.plot(range(episode_length), intention_vals, label=d_name, color=desire_color[d_name],
                            linestyle='dotted')
                if highlight_attr_int:
                    intention_any = [max(timestamp_intentions.values()) if len(timestamp_intentions.values()) > 0 else 0
                                     for timestamp_intentions in intention_track]
                    ax.fill_between(range(episode_length), 0, 1, where=np.array(intention_any) >= commitment_threshold,
                                    alpha=0.5)
                    print(f"Real coverage: {np.sum(np.array(intention_any) >= commitment_threshold) / len(intention_any)}")
                ax.legend()
                ax.set_ylim(bottom=0, top=1)
                if s_proba:
                    ax2 = ax.twinx()
                    ax2.plot(range(episode_length), prob_track, label="Node Probability", color="black",
                             linestyle='solid')
                    ax2.set_ylim(bottom=0)
                for t, d_name in desire_fulfill_track.items():
                    ax.vlines(t, -0.05, 1.05, label=d_name, colors=desire_color[d_name], linestyles='-')

                agent=disc_to_string(str(disc))
                plt.title(f'Intention evolution of {agent} in {domain}-(Traj. {n})')
                # plt.subplots_adjust(left=0, right=1.01, hspace=0, wspace=0.5)
                # plt.margins(0,0)
                plt.savefig(f'logs/imgs/REV_{domain}-D{disc}-Traj{n}.png',bbox_inches='tight')
                plt.show()


def trajectory_metrics_from_real(desires, trajectory, pg):
    # trajectory = get_trajectory(domain, disc)
    intention_track = []
    prob_track = []
    desire_fulfill_track = {}
    episode_length = len(trajectory)
    for t, (n_idx, action) in enumerate(trajectory):
        if n_idx == -1:
            # print(t, "Unseen Node")
            # print(action)
            intention_track.append({d.name: -0.1 for d in desires})
            prob_track.append(0)
        else:
            current = pg.nodes[n_idx]
            prob_track.append(current.probability)
            """if t > 350 and t < 400:
                print(t, sorted(current.state_rep))
                print(action_idx_to_name[action])"""
            intention_track.append(current.intention)
            for desire in desires:
                d_name = desire.name
                clause, action_idx = desire.clause, desire.action_idx
                ret = current.check_desire(clause, action_idx)
                if ret is not None and action_idx == action:
                    print('   ', d_name, 'FULFILLED at time', t)
                    desire_fulfill_track[t] = d_name
    return desire_fulfill_track, episode_length, intention_track, prob_track


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
        "-ns",
        "--traj_ns",
        nargs="+",
        type=int,
        default=0,
        help="Which trajectories to analyse"
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    # exp_intention_metrics()
    exp_extract_trajectory_metrics(args)
