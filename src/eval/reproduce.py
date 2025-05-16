from argparse import Namespace

from eval.QA_algorithms import xai_experiment
from eval.environment_trajectory_trials import exp_extract_trajectory_metrics
from eval.intention_trials import exp_extract_metrics
from eval.intention_trials import exp_extract_int_rel_curves_AAMASversion


if __name__=='__main__':
    args=Namespace()
    # Figure 2 & 3
    args.domains = ['simple', 'random0'] # Try unident_s, random1 or random3
    args.discretisers = ['14','24','34','44']
    args.com_threshold =0.5

    # Figure 2 a & b
    exp_extract_metrics(args)
    # Figure 3
    exp_extract_int_rel_curves_AAMASversion(args)


    # Figure 4
    args.domains = ['random0'] # Try unident_s (no trajectories for random1 or 3 yet)
    args.discretisers = ['24'] # Try 14, 34, 44
    args.traj_ns = [2] # Try 14, 34, 44
    args.com_threshold =0.5
    exp_extract_trajectory_metrics(args)

    # XAI questions (text + Table 3)
    ## IMPORTANT NOTE: How answer changes a bit due to changes of the PG file reordering.
    ## It still produces a correct answer, but it is different from the paper's. (I+D+R+D+S+I instead of I+R+D+I)
    domain, disc, C_th = 'simple', '14', 0.5
    node_idx = 11
    action_idx_for_why = '5'
    stochastic_how = False
    xai_experiment(domain, disc, C_th, node_idx, action_idx_for_why, stochastic_how)
