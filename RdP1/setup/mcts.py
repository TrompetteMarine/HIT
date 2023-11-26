import numba as nb
from hit import Player, HitEnvironment
from typing import Tuple

class MonteCarloTreeSearch:
    def __init__(self, hit_environment: HitEnvironment) -> None:

        self.Q = {}
        self.P = {}
        self.V = {}
        self.N = {}

        self.cexp = 1
        self.cpuct = 1

        self.num_mcts_sims = 100
        self.max_depth = 20
        self.hit_environment = hit_environment
    
    def get_optimal_action(self, state: Tuple):
        # remaining cards could be a dictionary or a list
        remaining_cards, *features = state
        pass

    def search(self, state):
        # end return reward

        # select next action using UCT

        # search further

        # update the Q function 

        # return updated reward

        pass

