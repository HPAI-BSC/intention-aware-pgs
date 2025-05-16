import csv
import json
import pickle

import tqdm

from src.policy_graph import PolicyGraph


if __name__ == '__main__':

    for LAYOUT in tqdm.tqdm(['random0', 'random1', 'random3', 'simple', 'unident_s']):
        for DISCRETIZER in tqdm.tqdm([11, 12, 13, 14, 31, 32, 33, 34]):

            with open(f'./policygraphs/trajectories_{LAYOUT}_{DISCRETIZER}_n1500.json', 'r+') as f:
                trajectories = json.load(f)

            pg = PolicyGraph()

            all_states = set([s
                              for trajectory in trajectories
                              for s in trajectory
                              if isinstance(s, str)])
            for state in all_states:
                pg.add_node(state, weight=0)

            for trajectory in trajectories:
                states_in_trajectory = [s for s in trajectory if isinstance(s, str)]
                state_frequencies = {s: states_in_trajectory.count(s) for s in states_in_trajectory}

                for state in state_frequencies:
                    pg.nodes[state]['weight'] += state_frequencies[state]
            for trajectory in trajectories:
                pointer = 0
                while (pointer + 1) < len(trajectory):
                    state_from, action, state_to = trajectory[pointer:pointer + 3]
                    if not pg.has_edge(state_from, state_to, key=action):
                        pg.add_edge(state_from, state_to, key=action, weight=0)
                    pg[state_from][state_to][action]['weight'] += 1
                    pointer += 2

            pgn = pg.get_normalized_graph()

            with open(f'./actually_good_pgs/pg_{LAYOUT}_{DISCRETIZER}.pickle', 'wb') as f:
                pickle.dump(pg, f, protocol=pickle.HIGHEST_PROTOCOL)
            with open(f'./actually_good_pgs/pg_{LAYOUT}_{DISCRETIZER}n.pickle', 'wb') as f:
                pickle.dump(pgn, f, protocol=pickle.HIGHEST_PROTOCOL)

            node_info = {}
            with open(f'./actually_good_pgs/pg_{LAYOUT}_{DISCRETIZER}_nodes.csv', 'w+') as f:
                csv_w = csv.writer(f)
                csv_w.writerow(['id', 'value', 'p(s)'])
                for i, node in enumerate(pg.nodes):
                    node_info[node] = i
                    csv_w.writerow([i, node, pgn.nodes[node]['weight']])
            with open(f'./actually_good_pgs/pg_{LAYOUT}_{DISCRETIZER}_edges.csv', 'w+') as f:
                csv_w = csv.writer(f)
                csv_w.writerow(['from', 'to', 'action', "p(s'a|s)"])
                for edge in pg.edges:
                    state_from, state_to, action = edge
                    csv_w.writerow([node_info[state_from], node_info[state_to], action,
                                    pgn[state_from][state_to][action]['weight']])