from typing import Set


class Desire(object):
    def __init__(self, name: str, action_idx: str, clause: Set[str]):
        self.name = name
        self.action_idx = action_idx
        self.clause = clause


