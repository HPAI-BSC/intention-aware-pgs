import csv
import json
from collections import defaultdict
import pickle
from typing import List

import numpy as np
import tqdm

from human_aware_rl.utils import set_global_seed
from src.agents.overcooked_explainability import load_PPOAgents
from src.agents.overcooked_harl_explainability import load_PPO_HARL
from src.discretizers.overcooked import Discretizer11, Discretizer12, Discretizer13, Discretizer14
from src.discretizers.overcooked_alt import \
    Discretizer11 as Discretizer11Alt, \
    Discretizer12 as Discretizer12Alt, \
    Discretizer13 as Discretizer13Alt, \
    Discretizer14 as Discretizer14Alt
from src.environments.overcooked import \
    OvercookedSinglePlayerWrapper, OvercookedHARLSinglePlayerWrapper, OvercookedHARLSinglePlayerWrapperAltPOV
from overcookedgym.overcooked import OvercookedMultiEnv
from src.policy_graph import PolicyGraph
from src.utils.human_aware_rl.baselines_utils import ImitationAgentFromPolicy


def state_to_str(state):
    return '+'.join([x.name for x in state])


def bad_name_to_good_name(node_value: str, discretizer: int):
    # Amount of predicates that will always be there
    COMMON_PREDICATES = {
        11: 6, 12: 7, 13: 7, 14: 8
    }

    predicate_values = node_value.split('+')

    # Amount of pots in the state
    n_pots = (len(predicate_values) - COMMON_PREDICATES[discretizer]) // 2

    held_partner_present = 1 if discretizer in [12, 14] else 0
    partner_pos_present = 1 if discretizer in [13, 14] else 0

    predicate_values[0] = f'HELD_PLAYER({predicate_values[0]})'
    if held_partner_present:
        predicate_values[1] = f'HELD_PARTNER({predicate_values[1]})'

    for pot_id in range(n_pots):
        predicate_values[1+held_partner_present+pot_id] = f'POT_STATE(POT{pot_id};{predicate_values[1+held_partner_present+pot_id]})'

    for element_id, element in enumerate(['ONION', 'TOMATO', 'SOUP', 'DISH', 'SERVICE']):
        predicate_values[1+n_pots+held_partner_present+element_id] = f'ACTION2NEAREST({element};{predicate_values[1+n_pots+held_partner_present+element_id]})'

    for pot_id in range(n_pots):
        predicate_values[6+n_pots+held_partner_present+pot_id] = f'ACTION2NEAREST(POT{pot_id};{predicate_values[6+n_pots+held_partner_present+pot_id]})'

    if partner_pos_present:
        predicate_values[-1] = f'PARTNER_POSITION({predicate_values[-1]})'

    return '+'.join(predicate_values)


def extract_trajectories_from_pgs(env,
                                  agent1,
                                  agent2,
                                  discretizers1,
                                  discretizers2,
                                  nodes1,
                                  nodes2):
    global NUM_EPISODES

    all_trajectories1 = [[] for _ in discretizers1]
    all_trajectories2 = [[] for _ in discretizers2]

    for ep in tqdm.tqdm(range(NUM_EPISODES)):
        set_global_seed(ep)

        _ = env.reset()
        obs = env.base_env.state
        done = False

        trajectories1 = [
            [bad_name_to_good_name(state_to_str(disc.discretize((None, obs))), 11+id)]
             for id, (disc, nodes) in enumerate(zip(discretizers1, nodes1))
        ]
        trajectories2 = [
            [bad_name_to_good_name(state_to_str(disc.discretize((None, obs))), 11+id)]
             for id, (disc, nodes) in enumerate(zip(discretizers2, nodes2))
        ]

        while not done:

            # We get the action
            action1 = agent1.act((None, obs))
            action2 = agent2.get_action(obs)

            _, _, done, _ = env.env.step_alt(env.env, np.array([action1, action2]))
            obs = env.base_env.state

            for i, disc in enumerate(discretizers1):
                trajectories1[i].extend(
                    [action1, bad_name_to_good_name(state_to_str(disc.discretize((None, obs))), 11+i)]
                )
            for i, disc in enumerate(discretizers2):
                trajectories2[i].extend(
                    [action2, bad_name_to_good_name(state_to_str(disc.discretize((None, obs))), 11+i)]
                )

        for i, trajectory in enumerate(trajectories1):
            all_trajectories1[i].append(trajectory)
        for i, trajectory in enumerate(trajectories2):
            all_trajectories2[i].append(trajectory)

    return all_trajectories1, all_trajectories2


def get_node_info(path_to_nodes: str):
    with open(path_to_nodes, 'r+') as f:
        csv_r = csv.reader(f)

        node_info = defaultdict(lambda: -1)
        next(csv_r)

        for id, state, _ in csv_r:
            node_info[state] = id

    return node_info


def get_1x_and_3x_trajectories(layout: str):
    agent1, agent2, env = load_PPO_HARL(layout, True)
    discretizers = [
        Discretizer11(env),
        Discretizer12(env),
        Discretizer13(env),
        Discretizer14(env)
    ]
    discretizers_alt = [
        Discretizer11Alt(env),
        Discretizer12Alt(env),
        Discretizer13Alt(env),
        Discretizer14Alt(env)
    ]
    nodes1 = [
        get_node_info(f'/home/adri/Escritorio/rl/policy-graphs/policy-graph-explainability-copy/policygraphs'
                      f'/pg_{layout}_1{i}_nodes.csv')
        for i in [1, 2, 3, 4]
    ]
    nodes2 = [
        get_node_info(f'/home/adri/Escritorio/rl/policy-graphs/policy-graph-explainability-copy/policygraphs'
                      f'/pg_{layout}_3{i}_nodes.csv')
        for i in [1, 2, 3, 4]
    ]

    def step_alt(
            self,
            actions: List[np.ndarray]
    ):
        ego_rew = 0.0

        while True:
            self._players, self._obs, rews, done, info = self.n_step(np.array(actions))
            info['_partnerid'] = self.partnerids

            self._update_players(rews, done)

            ego_rew += rews[self.ego_ind] if self.ego_moved \
                else self.total_rews[self.ego_ind]

            self.ego_moved = True

            if done:
                return self._old_ego_obs, ego_rew, done, info

            if self.ego_ind in self._players:
                break

        ego_obs = self._obs[self._players.index(self.ego_ind)]
        self._old_ego_obs = ego_obs
        return ego_obs, ego_rew, done, info

    env.env.step_alt = step_alt

    trajectories1, trajectories2 = extract_trajectories_from_pgs(env,
                                                                 agent1,
                                                                 agent2,
                                                                 discretizers,
                                                                 discretizers_alt,
                                                                 nodes1,
                                                                 nodes2)
    return trajectories1, trajectories2


if __name__ == '__main__':
    NUM_EPISODES = 1500
    LAYOUTS = ['random0', 'random1', 'random3', 'simple', 'unident_s']

    for layout in LAYOUTS:
        print(f'1x-3x-{layout}')
        traj_1x, traj_3x = get_1x_and_3x_trajectories(layout)
        for i, all_trajs in enumerate(traj_1x):
            with open(f'/home/adri/Escritorio/rl/policy-graphs/policy-graph-explainability-copy/policygraphs'
                      f'/trajectories_{layout}_1{i+1}_n1500.json',
                      'w+') as f:
                json.dump(all_trajs, f)

        for i, all_trajs in enumerate(traj_3x):
            with open(f'/home/adri/Escritorio/rl/policy-graphs/policy-graph-explainability-copy/policygraphs'
                      f'/trajectories_{layout}_3{i+1}_n1500.json',
                      'w+') as f:
                json.dump(all_trajs, f)