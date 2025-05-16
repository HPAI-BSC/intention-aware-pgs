import argparse

from eval.desire_trials import get_desires, pg_from
import numpy as np

def exp1():
    for domain in ['random0']:  # ['simple', 'random0', 'unident_s']: # []:
        desires = get_desires(only_one_pot=domain == 'simple')
        results = {'Environment': domain}
        for disc in [11, 12, 13, 14]:
            results['DISC'] = disc
            x = pg_from(domain, disc)
            x.register_all_desires(desires)

            results['H_a'], _ = x.compute_intentional_entropy("agent", weight_factor=10)
            results['H_w'], results['total_intent'] = x.compute_intentional_entropy("world", weight_factor=10)

            print(results)

def exp1_plot(args):
    from matplotlib import pyplot as plt
    weight_factor = args.intention_weight
    for domain in args.domains:
        desires = get_desires(only_one_pot=domain == 'simple')
        results = {'Environment': domain}
        total_results = {'H_a': [], 'H_w': [], 'intent': [], 'H': []}
        for disc in args.discretisers:
            results['DISC'] = disc
            x = pg_from(domain, disc)
            x.register_all_desires(desires)

            results['H_a'], _ = x.compute_intentional_entropy("agent", weight_factor=weight_factor)
            results['H_w'], results['total_intent'] = x.compute_intentional_entropy("world", weight_factor=weight_factor)
            results['H'] = results['H_a']+results['H_w']
            total_results['H_a'].append(results['H_a'])
            total_results['H_w'].append(results['H_w'])
            total_results['H'].append(results['H'])
            total_results['intent'].append(results['total_intent'])
            print(results)
        x = np.arange(len(args.discretisers))
        width = 0.2
        for i, (attribute, value) in enumerate(total_results.items()):
            offset = width * i
            rects = plt.bar(x + offset, value, width, label=attribute)
            plt.bar_label(rects, padding=3, fmt=lambda x: '{:.3f}'.format(x))
        plt.ylabel('Entropy')
        plt.title(f'Intentional Entropy metrics for {domain} at weight factor {weight_factor}')
        plt.xticks(x + width, [str(x) for x in args.discretisers])
        plt.legend()
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
    parser.add_argument(
        "-cth",
        "--com_threshold",
        type=float,
        default=0.5,
        help="Commitment Threshold"
    )
    parser.add_argument(
        "-w",
        "--intention_weight",
        type=float,
        default=10,
        help="Commitment Threshold"
    )
    return parser.parse_args()


if __name__=='__main__':
    args = get_args()
    exp1_plot(args)
