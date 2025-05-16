import numpy as np


class CartpoleDiscretizer:
    def __init__(self):
        self.predicate_space = {
            'position': {'farL', 'nearMid', 'farR'},
            'velocity': {'l', 'r'},
            'angle': {'standUp', 'stuckL', 'stuckR', 'fallingL', 'fallingR', 'stabL', 'stabR'}
        }

    def discretize(self, state: np.ndarray, to_dict=False):
        pos = state[0]
        vel = state[1]
        ang = state[2]
        velAtT = state[3]

        if -2 < pos < 2:
            pos_predicate = 'nearMid'
        elif pos < 0:
            pos_predicate = 'farL'
        else:
            pos_predicate = 'farR'

        if vel < 0:
            mov_predicate = 'l'
        else:
            mov_predicate = 'r'

        stuckVel = 0.1
        standAng = 0.0005
        pole_predicate = ''
        if -standAng < ang < standAng:
            pole_predicate = 'standUp'
        elif ang < 0 and -stuckVel < velAtT < stuckVel:
            pole_predicate = 'stuckL'
        elif ang > 0 and -stuckVel < velAtT < stuckVel:
            pole_predicate = 'stuckR'
        elif ang < 0 and velAtT < 0:
            pole_predicate = 'fallingL'
        elif ang < 0 and velAtT > 0:
            pole_predicate = 'stabR'
        elif ang > 0 and velAtT > 0:
            pole_predicate = 'fallingR'
        elif ang > 0 and velAtT < 0:
            pole_predicate = 'stabL'

        if to_dict:
            return {'position': pos_predicate, 'velocity': mov_predicate, 'angle': pole_predicate}
        else:
            return pos_predicate, mov_predicate, pole_predicate

    def dict_to_tuple(self, predicates: dict):
        if isinstance(predicates, tuple): return predicates
        return predicates['position'], predicates['velocity'], predicates['angle']

    def tuple_to_dict(self, predicates: tuple):
        if isinstance(predicates, dict): return predicates
        return {'position': predicates[0], 'velocity': predicates[1], 'angle': predicates[2]}