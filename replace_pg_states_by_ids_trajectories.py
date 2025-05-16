import csv
import json

import tqdm


if __name__ == '__main__':
    for LAYOUT in tqdm.tqdm(['random0', 'random1', 'random3', 'simple', 'unident_s']):
        for DISCRETIZER in tqdm.tqdm([11, 12, 13, 14, 31, 32, 33, 34]):
            node_info = {}

            with open(f'./pg_{LAYOUT}_{DISCRETIZER}_nodes.csv', 'r+') as f:
                csv_r = csv.reader(f)
                next(csv_r)

                for id, node, _ in csv_r:
                    node_info[node] = int(id)

            with open(f'../policygraphs/trajectories_{LAYOUT}_{DISCRETIZER}_n1500.json', 'r+') as f:
                trajectories = json.load(f)
            new_trajectories = []
            for trajectory in trajectories:
                new_trajectory = [node_info[s] if isinstance(s, str) else s for s in trajectory]
                new_trajectories.append(new_trajectory)

            with open(f'../policygraphs/trajectories_{LAYOUT}_{DISCRETIZER}_n1500_ids.json', 'w+') as f:
                json.dump(new_trajectories, f)