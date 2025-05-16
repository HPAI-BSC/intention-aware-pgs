import argparse
from typing import List

import numpy as np

from domain.desire import Desire
from eval.desire_trials import get_desires
from eval.utils import action_name_to_idx, pg_from


# def exp_intention_metrics():
#     for domain in ['simple']:
#         desires: List[Desire] = get_desires(only_one_pot=domain=='simple')
#         results = {'Environment': domain}
#         for disc in [11]:
#             results['DISC'] = disc
#             x = pg_from(domain, disc)
#             intention_full_nodes = set()
#             for desire in desires:
#                 d_name = desire.name
#                 results['desire'] = d_name
#                 x.register_desire(d_name, desire)
#                 intention_vals, nodes = x.compute_commitment_stats(d_name, commitment_threshold=1e-4)
#                 intention_full_nodes.update(set([n.node_id for n in nodes]))
#
#                 # print(d_name, result_stats)
#                 results['prevalence'] = '/'.join([str(len(intention_vals)), str(len(x.nodes))])
#                 int_states = np.array([n.probability for n in nodes])
#                 int_total_probability = int_states.sum()
#                 results['intention_probability'] = int_total_probability
#                 results['expected_int_probability'] = np.dot(np.array(intention_vals), int_states) \
#                                                   / int_total_probability
#                 print(results)
#             results['desire'] = 'Any'
#             results['prevalence'] = '/'.join([str(len(intention_full_nodes)), str(len(x.nodes))])
#             int_states = np.array([x.nodes[n_idx].probability for n_idx in intention_full_nodes])
#             int_total_probability = int_states.sum()
#             results['intention_probability'] = int_total_probability
#             intention_max_vals = [max(list(x.nodes[n_idx].intention.values())) for n_idx in intention_full_nodes]
#             results['expected_int_probability'] = np.dot(np.array(intention_max_vals), int_states) \
#                                                   / int_total_probability
#             print(results)
#             print()


def disc_to_string(disc):
    agent = disc[0]
    if agent=='R': return "RAg"
    if agent=='1': return "HPPO"
    if agent=='2': return "PPO1"
    if agent=='3': return "HAg"
    if agent=='4': return "PPO2"


def exp_extract_metrics(args):
    commitment_threshold = args.com_threshold
    from matplotlib import pyplot as plt
    for domain in args.domains:
        desires: List[Desire] = get_desires(only_one_pot=domain == 'simple')
        results = {'Environment': domain}
        for disc in args.discretisers:
            results['DISC'] = disc
            x = pg_from(domain, disc)
            intention_full_nodes = set()
            desire_name_list = [d.name for d in desires] + ['Any']
            total_results = {k: [] for k in ['intention_probability', 'expected_int_probability']}
            x.register_all_desires(desires)
            for desire in desires:
                d_name = desire.name
                intention_vals, nodes = x.compute_commitment_stats(d_name, commitment_threshold=commitment_threshold)
                intention_full_nodes.update(set([n.node_id for n in nodes]))

                # print(d_name, result_stats)
                results['prevalence'] = '/'.join([str(len(intention_vals)), str(len(x.nodes))])
                int_states = np.array([n.probability for n in nodes])
                int_total_probability = int_states.sum()

                total_results['intention_probability'].append(int_total_probability)
                total_results['expected_int_probability'].append(
                    np.dot(np.array(intention_vals), int_states) / int_total_probability)
            results['desire'] = 'Any'
            results['prevalence'] = '/'.join([str(len(intention_full_nodes)), str(len(x.nodes))])
            int_states = np.array([x.nodes[n_idx].probability for n_idx in intention_full_nodes])
            int_total_probability = int_states.sum()
            intention_max_vals = [max(list(x.nodes[n_idx].intention.values())) for n_idx in intention_full_nodes]
            total_results['intention_probability'].append(int_total_probability)
            total_results['expected_int_probability'].append( np.dot(np.array(intention_max_vals), int_states) \
                                                  / int_total_probability )

            x = np.arange(len(desire_name_list))
            plt.figure(figsize=(7, 3))
            width = 0.4
            for i, (attribute, value) in enumerate(total_results.items()):
                offset = width * i
                rects = plt.bar(x + offset, value, width, label=attribute)
                plt.bar_label(rects, padding=3, fmt=lambda x: '{:.3f}'.format(x))
            plt.ylabel('Probability')
            disc_journal = f"D{disc}"
            disc_aamas = disc_to_string(disc)
            disc_string = disc_aamas
            plt.title(f'Intention metrics for {disc_string} in {domain}, C = {commitment_threshold}')
            desire_name_list = [d[len('desire_to_'):] if d != 'Any' else d for d in desire_name_list]
            plt.xticks(x + width/2, desire_name_list)
            plt.legend(loc='upper left', ncols=3)
            plt.ylim(0, 1.18)
            # plt.gca().set_axis_off()
            plt.subplots_adjust(right=1.01, hspace=0, wspace=0)
            plt.margins(0,0)
            plt.savefig(f'logs/imgs/intentions_{domain}-D{disc}-C{commitment_threshold}.png',bbox_inches='tight')
            plt.show()


def exp_extract_int_rel_curves(args):
    from matplotlib import pyplot as plt
    for domain in args.domains:
        desires: List[Desire] = get_desires(only_one_pot=domain == 'simple')
        results = {'Environment': domain}
        for disc in args.discretisers:
            results['DISC'] = disc
            x = pg_from(domain, disc)
            desire_name_list = [d.name for d in desires] + ['Any']
            total_results = {k: [] for k in ['intention_probability', 'expected_int_probability']}
            x.register_all_desires(desires)
            c_thresholds = np.arange(1,0,-0.01)
            int_probability, expected_int = [], []
            for commitment_threshold in c_thresholds:
                print(commitment_threshold)
                intention_full_nodes = set()
                for desire in desires:
                    d_name = desire.name
                    intention_vals, nodes = x.compute_commitment_stats(d_name, commitment_threshold=commitment_threshold)
                    intention_full_nodes.update(set([n.node_id for n in nodes]))
                    results['prevalence'] = '/'.join([str(len(intention_vals)), str(len(x.nodes))])
                    int_states = np.array([n.probability for n in nodes])
                    int_total_probability = int_states.sum()
                    total_results['intention_probability'].append(int_total_probability)
                    total_results['expected_int_probability'].append(
                        np.dot(np.array(intention_vals), int_states) / int_total_probability)
                results['desire'] = 'Any'
                results['prevalence'] = '/'.join([str(len(intention_full_nodes)), str(len(x.nodes))])
                int_states = np.array([x.nodes[n_idx].probability for n_idx in intention_full_nodes])
                int_total_probability = int_states.sum()
                intention_max_vals = [max(list(x.nodes[n_idx].intention.values())) for n_idx in intention_full_nodes]
                expected_int_proba = np.dot(np.array(intention_max_vals), int_states) / int_total_probability
                int_probability.append(int_total_probability)
                expected_int.append(expected_int_proba)
            plt.plot(int_probability, expected_int, label=f"D{disc}")
        plt.xlabel('Probability of having any intention')
        plt.ylabel('Expected intention probability')
        agent = args.discretisers[0] // 10 if type(args.discretisers[0])==int else args.discretisers[0][0]
        plt.title(f"Evolution of 'Any' intention metrics for {domain}, Agent {agent}")
        plt.legend()
        plt.savefig(f'logs/imgs/ROC_{domain}_agent_{agent}.png')
        plt.show()


def exp_extract_int_rel_curves_AAMASversion(args):
    from matplotlib import pyplot as plt
    for domain in args.domains:
        desires: List[Desire] = get_desires(only_one_pot=domain == 'simple')
        results = {'Environment': domain}
        plt.figure(figsize=(5, 3.5))
        for disc in args.discretisers:
            results['DISC'] = disc
            x = pg_from(domain, disc)
            total_results = {k: [] for k in ['intention_probability', 'expected_int_probability']}
            x.register_all_desires(desires)
            c_thresholds = np.arange(1,0,-0.01)
            int_probability, expected_int = [], []
            for commitment_threshold in c_thresholds:
                print(commitment_threshold)
                intention_full_nodes = set()
                for desire in desires:
                    d_name = desire.name
                    intention_vals, nodes = x.compute_commitment_stats(d_name, commitment_threshold=commitment_threshold)
                    intention_full_nodes.update(set([n.node_id for n in nodes]))
                    results['prevalence'] = '/'.join([str(len(intention_vals)), str(len(x.nodes))])
                    int_states = np.array([n.probability for n in nodes])
                    int_total_probability = int_states.sum()
                    total_results['intention_probability'].append(int_total_probability)
                    total_results['expected_int_probability'].append(
                        np.dot(np.array(intention_vals), int_states) / int_total_probability)
                results['desire'] = 'Any'
                results['prevalence'] = '/'.join([str(len(intention_full_nodes)), str(len(x.nodes))])
                int_states = np.array([x.nodes[n_idx].probability for n_idx in intention_full_nodes])
                int_total_probability = int_states.sum()
                intention_max_vals = [max(list(x.nodes[n_idx].intention.values())) for n_idx in intention_full_nodes]
                expected_int_proba = np.dot(np.array(intention_max_vals), int_states) / int_total_probability
                int_probability.append(int_total_probability)
                expected_int.append(expected_int_proba)
            disc_string = disc_to_string(disc)
            for C_idx in [3*len(c_thresholds)//4, len(c_thresholds)//2, 1*len(c_thresholds)//4]:
                plt.annotate(round(c_thresholds[C_idx],2), (int_probability[C_idx], expected_int[C_idx]))
            plt.plot(int_probability, expected_int, label=disc_string)
        plt.xlabel('Attributed intention probability')
        plt.ylabel('Expected intention probability')
        plt.title(f"Evolution of 'Any' intention metrics for {domain}")
        plt.legend()
        plt.subplots_adjust(right=1.01, hspace=0, wspace=0)
        plt.margins(0,0)
        plt.savefig(f'logs/imgs/ROC_{domain}.png',bbox_inches='tight')
        plt.show()


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
        type=str,
        help="Discretisers"
    )
    parser.add_argument(
        "-cth",
        "--com_threshold",
        type=float,
        default=0.5,
        help="Commitment Threshold"
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    # exp_extract_metrics(args)
    exp_extract_int_rel_curves_AAMASversion(args)
    # exp_extract_int_rel_curves(args)
    # exp_intention_metrics(args)
