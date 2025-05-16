from eval.graph import PolicyGraphAndTrajectories
from typing import Type, Tuple, List
from pathlib import Path

action_idx_to_name = {'0': 'UP', '1': 'DOWN', '2': 'RIGHT', '3': 'LEFT', '4': 'STAY', '5': 'Interact'}

action_name_to_idx = {'Interact': '5'}


def pg_from(domain, disc):
    transitions_file, state_file = Path(f"policygraphs/pg_{domain}_{disc}_edges.csv").absolute(), \
                                   Path(f"policygraphs/pg_{domain}_{disc}_nodes.csv").absolute()
    state_type = "Propositional"
    x = PolicyGraphAndTrajectories()
    x.load_graph_from_files(transitions_file, state_file, state_type)
    return x


def get_trajectory_old(domain, disc, types: Tuple[Type, Type] = (int, str), pg=None) -> List[Tuple]:
    with open(Path(f"pg_trajectories/pg_trajectory_{domain}_{disc}.txt").absolute(), 'r') as f:
        data = f.read()
    if pg is None:
        data = data[2:-2]
        data = data.split('), (')
        data = [(e.split(', ')[0], e.split(', ')[1]) for e in data]
        data = [(types[0](s.strip("'")), types[1](a)) for s, a in data]
    else:
        pass
    return data

def get_trajectory(domain, disc, n, types: Tuple[Type, Type] = (int, str)) -> List[Tuple]:
    import json
    with open(Path(f"pg_trajectories/trajectories_{domain}_{disc}_n1500_ids.json").absolute(), 'r') as f:
        data = json.load(f)
    trajectory = data[n]
    if len(trajectory)%2: # there is a last state that should be removed
        trajectory = trajectory[:-1]
    formatted_traj = [(types[0](trajectory[i]), types[1](trajectory[i+1]))for i in range(0, len(trajectory),2)]
    print(formatted_traj)
    return formatted_traj

def load_semaphor(disc):
    transitions_file, state_file = f"policygraphs/semaphor_{disc}_edges.csv", \
                                   f"policygraphs/semaphor_{disc}_nodes.csv"
    state_type = "Propositional"
    x = PolicyGraphAndTrajectories()
    x.load_graph_from_files(transitions_file, state_file, state_type)
    return x
