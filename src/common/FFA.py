import random
import itertools
import functools
from dataclasses import dataclass
from copy import copy

from typing import Callable, List, Iterable, Iterator, Optional, Tuple

import problem

Node = int
Value = float
Problem = problem.Problem[Node, Value]
Perm = Tuple[Node, ...]

@dataclass
class Firefly:
    id    : int
    perm  : Perm
    value : Value


@dataclass
class FFAParams:
    n             : Optional[int] = None                      # Number of fireflies
    alpha         : float                                     # Hyper-parameter Alpha (for alpha-step)
    gamma         : float                                     # Hyper-parameter Gamma (for beta-step)
    continue_cond : Callable[[], bool]                        # Condition to continue
    alpha_shuffle : Callable[[List[int]], List[int]]          # Shuffle function for alpha step
    perm_dist     : Callable[[List[Node], List[Node]], float] # Distance function between permutations


@dataclass
class Movement:
    ff_target : Firefly
    ff_marked : Firefly
    ff_after  : Firefly
    ff_best   : Firefly


@dataclass
class IterationState:
    n_updates_before  : int
    n_updates_current : int
    ff_best           : Firefly
    n_ff_variants     : int


@dataclass
class State:
    best_perm        : Perm
    best_value       : Value
    iteration_states : List[IterationState]
    movements        : List[Movement]

    # def copy(self):
    #     return State(best_perm, best_value, iteration_states.copy(), movements.copy())


@dataclass
class Settings:
    ffa_params    : FFAParams
    cond          : Callable[[State], bool]
    initial_perms : Optional[Iterable[Perm]] = None


class Optimizer:

    def __init__(self, problem:Problem):
        self.problem = problem


    def optimize(self, stgs:Settings) -> State:
       
        cond = stgs.cond
        ffa_params = stgs.ffa_params
        initial_perms = stgs.initial_perms

        if initial_perms is None:
            if ffa_params.n is None:
                raise RuntimeError('Number of fireflies is not specified.')
            initial_perms = [random.sample(self.problem.node_set, len(self.problem.node_set)) for _ in range(ffa_params.n)]

        self.fireflies = [Firefly(i, perm, self.problem.calc_value(perm)) for i, perm in enumerate(initial_perms, 1)]
        self.ff_best = max(self.fireflies, key=self.problem.good_order_key)
        self.iteration_states = [IterationState(0, 0, self.ff_best, self.ff_variant())]
        self.movements:List[Movement] = []

        while cond(self.state()):
            n_movements_before = len(self.movements)

            for ff_target, ff_marked in itertools.combinations(self.ff_sorted(), 2):
                if self.fireflies.is_better(ff_target, ff_marked):
                    self.move_ff(ff_target, attract_perms(ff_target.perm, ff_marked.perm, ffa_params), ff_marked)

            if len(self.movements) - n_movements_before == 0:
                for ff in self.fireflies[1:]:
                    self.move_ff(ff, shuffle_perm(ff.perm, ffa_params))

            self.iteration_states.append(IterationState(
                n_movements_before,
                len(self.movements) - n_movements_before,
                self.ff_best,
                self.ff_variant()
            ))
            
        return self.state()


    def move_ff(self, ff_target:Firefly, perm_after:Perm, ff_marked:Optional[Firefly]=None): 
        ff_after = Firefly(ff_target.id, perm_after, self.problem.calc_value(perm_after))
        if self.problem.is_better(ff_after, self.ff_best):
            ff_best = ff_after
        self.movements.append(Movement(ff_target, ff_marked, ff_after, ff_best))


    def ff_sorted(self) -> List[Firefly]:
        return sorted(self.fireflies, key=self.problem.good_order_key)


    def ff_variant(self) -> int:
        return len(set(ff.perm for ff in self.fireflies))


    def state(self) -> State:
        return State(self.ff_best.perm, self.ff_best.value, self.iteration_states, self.movements)




# Firefly normal attraction
def attract_perms(perm_target:Perm, perm_marked:Perm, ffa_params:FFAParams) -> Perm:
    c_beta = 1 / (1 + ffa_params.gamma * ffa_params.perm_dist(perm_target, perm_marked))
    return shuffle_perm(beta_step(perm_target, perm_marked, c_beta), ffa_params)


def shuffle_perm(perm:Perm, ffa_params:FFAParams) -> Perm:
    c_alpha = int(random.random() * ffa_params.alpha + 1.0)
    return alpha_step(perm, c_alpha, ffa_params.alpha_shuffle)


# Firefly Algorithm Beta step (attract between perm1 and perm2 based on beta value)
def beta_step(perm1:Perm, perm2:Perm, prob:float) -> Perm:

    perm12:List[Optional[Node]] = [node1 if node1 == node2 else None for node1, node2 in zip(perm1, perm2)]
    remains = set(perm1).difference(set(node for node in perm12 if node))
    empties:List[int] = []

    # fill empty indexes in perm12
    for i in [i for i in range(len(perm12)) if perm12[i]]:

        # choose candidate node from perm1's node or perm2's based on beta value
        candidate_node = perm1[i] if random.random() > prob else perm2[i]

        # fill with chosen candidate node if it doesn't already exist in perm12
        if candidate_node in remains:
            perm12[i] = candidate_node
            remains.remove(candidate_node)
            empties.append(i)

    # fill remain indexes randomly
    if remains:
        shuffled_remains = random.sample(remains, len(remains))
        for i, perm12_i in enumerate(empties):
            perm12[perm12_i] = shuffled_remains[i]

    return perm12


# Firefly Algorithm Alpha step (randomly swap node_set in permutation based on alpha value)
def alpha_step(perm:List[Node], n_target_nodes:int, shuffle_func:Callable[[List[int]], List[int]]) -> Perm:

    if n_target_nodes <= 1:
        return perm

    target_indexes = random.sample(range(len(perm)), n_target_nodes)
    shuffled_target_indexes = shuffle_func(target_indexes)

    # shuffle target indexes
    new_perm = perm.copy()
    for shuffled_index, index in zip(shuffled_target_indexes, target_indexes):
        new_perm[shuffled_index] = perm[index]

    return new_perm

