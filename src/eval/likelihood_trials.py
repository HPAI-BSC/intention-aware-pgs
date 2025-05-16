from eval.graph import PolicyGraphAndTrajectories, Node
from eval.utils import get_trajectory, pg_from
import numpy as np


def exp_extract_metrics():
    for domain in ['random0', 'simple']:
        for disc in [11, 12, 13, 14]:
            trajectory = get_trajectory(domain, disc)
            x = pg_from(domain, disc)

            print(f'\tLog-likelihood for pg_trajectory_{domain}_{disc}.txt: {x.compute_likelihood([trajectory])}')


if __name__ == '__main__':
    exp_extract_metrics()




