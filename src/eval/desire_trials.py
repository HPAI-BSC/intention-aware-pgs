import argparse
from typing import List

from domain.desire import Desire
from eval.graph import PolicyGraphAndTrajectories, Node

import csv
import numpy as np
from eval.utils import action_idx_to_name, pg_from


def get_desires(only_one_pot=False) -> List[Desire]:
    action_name_to_idx = {'Interact': '5'}
    clause = {'HELD_PLAYER(SOUP)', 'ACTION2NEAREST(SERVICE;INTERACT)'}
    action = action_name_to_idx['Interact']
    desire_to_service = Desire("desire_to_service", action, clause)

    clause = {'HELD_PLAYER(ONION)', 'ACTION2NEAREST(POT0;INTERACT)', 'POT_STATE(POT0;PREPARING)'}
    action = action_name_to_idx['Interact']
    desire_to_cook0 = Desire("desire_to_cook0", action, clause)

    clause = {'HELD_PLAYER(ONION)', 'ACTION2NEAREST(POT0;INTERACT)', 'POT_STATE(POT0;NOT_STARTED)'}
    action = action_name_to_idx['Interact']
    desire_to_start_cooking0 = Desire("desire_to_start_cooking0", action, clause)

    to_return = [desire_to_service, desire_to_cook0, desire_to_start_cooking0]

    if not only_one_pot:
        clause = {'HELD_PLAYER(ONION)', 'ACTION2NEAREST(POT1;INTERACT)', 'POT_STATE(POT1;PREPARING)'}
        action = action_name_to_idx['Interact']
        desire_to_cook1 = Desire("desire_to_cook1", action, clause)

        clause = {'HELD_PLAYER(ONION)', 'ACTION2NEAREST(POT1;INTERACT)', 'POT_STATE(POT1;NOT_STARTED)'}
        action = action_name_to_idx['Interact']
        desire_to_start_cooking1 = Desire("desire_to_start_cooking1", action, clause)

        to_return.append(desire_to_cook1)
        to_return.append(desire_to_start_cooking1)

    return to_return


def exp_desire_metrics():
    for domain in ['simple', 'random0']:
        desires = get_desires(only_one_pot=domain=='simple')
        results = {'Environment': domain}
        for disc in [11, 12,13,14]:
            results['DISC'] = disc
            x = pg_from(domain, disc)
            for desire in desires:
                d_name = desire.name
                results['desire'] = d_name
                result_stats = x.compute_desire_statistics(desire)
                # print(d_name, result_stats)
                results['prevalence'] = '/'.join([str(len(result_stats[0])), str(len(x.nodes))])
                desire_states = np.array([n.probability for n in result_stats[1]])
                desire_total_probability = desire_states.sum()
                results['desire_probability'] = desire_total_probability

                results['mean_probability'] = np.array(result_stats[0]).mean()
                results['expected_probability'] = np.dot(np.array(result_stats[0]), desire_states) \
                                                  / desire_total_probability
                node = result_stats[1][4]
                print(results)
            print()


def exp_desire_examine_states():
    desires = get_desires()
    for domain in ['unident_s']:
        results = {'Environment': domain}
        for disc in [11, 12, 13, 14]:
            results['DISC'] = disc
            x = pg_from(domain, disc)
            for d_name, desire in desires.items():
                results['desire'] = d_name
                result_stats = x.compute_desire_statistics(desire)
                print(d_name, result_stats)
                results['prevalence'] = '/'.join([str(len(result_stats[0])), str(len(x.nodes))])
                desire_states = np.array([n.probability for n in result_stats[1]])
                desire_total_probability = desire_states.sum()
                results['desire_probability'] = desire_total_probability

                results['mean_probability'] = np.array(result_stats[0]).mean()
                results['expected_probability'] = np.dot(np.array(result_stats[0]), desire_states) \
                                                  / desire_total_probability
                try:
                    node = result_stats[1][0]
                    print(d_name)
                    print(node.state_rep)
                    print({action_idx_to_name[k]: v for k, v in node.get_action_probability().items()})
                    print(results)
                    print()
                except IndexError:
                    pass
            print()
    action_probs = results


def exp_extract_metrics(args):
    from matplotlib import pyplot as plt
    for domain in args.domains:
        desires = get_desires(only_one_pot=domain == 'simple')
        results = {'Environment': domain}
        for disc in args.discretisers:
            results['DISC'] = disc
            x = pg_from(domain, disc)

            desire_name_list = [d.name for d in desires]
            total_results = {k:[] for k in ['desired_clause_probability', 'expected_action_probability']}
            for i, desire in enumerate(desires):
                d_name = desire.name
                result_stats = x.compute_desire_statistics(desire)
                print(d_name, result_stats)
                desire_states = np.array([n.probability for n in result_stats[1]])
                desire_total_probability = desire_states.sum()
                total_results['desired_clause_probability'].append(desire_total_probability)
                total_results['expected_action_probability'].append(
                    np.dot(np.array(result_stats[0]), desire_states) / desire_total_probability )
            x = np.arange(len(desire_name_list))
            width = 0.4
            for i, (attribute, value) in enumerate(total_results.items()):
                offset = width * i
                rects = plt.bar(x + offset, value, width, label=attribute)
                plt.bar_label(rects, padding=3, fmt=lambda x: '{:.3f}'.format(x))
            plt.ylabel('Probability')
            plt.title(f'Desire metrics for {domain}-D{disc}')
            desire_name_list = [d[len('desire_to_'):] for d in desire_name_list]
            plt.xticks(x + width, desire_name_list)
            plt.legend(loc='upper left', ncols=3)
            plt.ylim(0, 1.2)
            plt.savefig(f'logs/imgs/desires_{domain}-D{disc}.png')
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
        type=int,
        help="Discretisers"
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    exp_extract_metrics(args)
