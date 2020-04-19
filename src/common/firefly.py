import random
import itertools
import functools
from dataclasses import dataclass
from copy import copy

from typing import Callable, List, Iterable, Iterator, Optional, Tuple

from .problem import Node, Value, Problem

Perm = Tuple[Node, ...]

@dataclass
class Firefly:
    id    : int
    perm  : Perm
    value : Value


@dataclass
class Movement:
    ff_target : Firefly
    ff_marked : Firefly
    ff_after  : Firefly
    ff_best   : Firefly

Movements = List[Movement]


@dataclass
class IterationState:
    n_updates_before  : int
    n_updates_current : int
    ff_best           : Firefly
    n_ff_variants     : int

IterationStates = List[IterationState]


@dataclass
class Configuration:
    n             : Optional[int] = None                      # Number of fireflies
    alpha         : float                                     # Hyper-parameter Alpha (for alpha-step)
    gamma         : float                                     # Hyper-parameter Gamma (for beta-step)
    continue_cond : Callable[[], bool]                        # Condition to continue
    alpha_shuffle : Callable[[List[int]], List[int]]          # Shuffle function for alpha step
    perm_dist     : Callable[[List[Node], List[Node]], float] # Distance function between permutations


@dataclass
class Result:
    best_perm        : Perm
    best_value       : Value
    iteration_states : IterationStates
    movements        : Movements


def optimize(
    problem       : Problem,
    cfg           : Configuration,
    cond          : Callable[[IterationStates, Movements], bool],
    initial_perms : Optional[Iterable[Perm]] = None,
) -> Result:
    
    if initial_perms is None:
        if cfg.n is None:
            raise RuntimeError('Number of fireflies is not specified.')
        initial_perms = [random.sample(problem.node_set, len(problem.node_set)) for _ in range(cfg.n)]

    fireflies = [Firefly(i, perm, problem.calc_value(perm)) for i, perm in enumerate(initial_perms, 1)]
    iteration_states:IterationStates = []
    movements:Movements = []

    while cond(iteration_states, movements):
        
        fireflies = sorted(fireflies, key=functools.cmp_to_key(
            lambda ff1, ff2: problem.is_better(ff1.value, ff2.value)
        ))
        ff_best = fireflies[0]
        n_updates_before = len(movements)
        
        for ff_target, ff_marked in itertools.combinations(fireflies.ordered, 2):

            if fireflies.is_better(ff_target, ff_marked):

                # Calculate current value of parameter
                c_beta = 1 / (1 + cfg.gamma * cfg.perm_dist(ff_target.perm, ff_marked.perm))
                c_alpha = int(random.random() * cfg.alpha + 1.0)

                # attract permutations and 
                perm_attracted = beta_step(ff_target.perm, ff_marked.perm, c_beta)
                perm_after = alpha_step(perm_attracted, c_alpha, cfg.alpha_shuffle)

                # Record movement
                ff_after = Firefly(ff_target.id, perm_after, problem.calc_value(perm_after))

                if problem.is_better(ff_after, ff_best):
                    ff_best = ff_after

                movements.append(Movement(ff_target, ff_marked, ff_after, ff_best))


        if len(movements) - n_updates_before == 0:

            for ff_target in fireflies[1:]:

                c_alpha = int(random.random() * cfg.alpha + 1.0)
                perm_after = alpha_step(ff_target.perm, c_alpha, cfg.alpha_shuffle)
                ff_after = Firefly(ff_target.id, perm_after, problem.calc_value(perm_after))

                if problem.is_better(ff_after, ff_best):
                    ff_best = ff_after

                movements.append(Movement(ff_target, ff_marked, ff_after, ff_best))

        
        n_updates_current = len(movements) - n_updates_before
        n_ff_variants = len(set(ff.perm for ff in fireflies))
    
        iteration_states.append(IterationState(n_updates_before, n_updates_current, ff_best, n_ff_variants))
        
    return Result(ff_best.perm, ff_best.value, iteration_states, movements)


# Firefly Algorithm Beta step (attract between perm1 and perm2 based on beta value)
def beta_step(perm1:Perm, perm2:Perm, prob:float) -> List[Node]:

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
def alpha_step(perm:List[Node], n_target_nodes:int, shuffle_func:Callable[[List[int]], List[int]]) -> List[Node]:

    if n_target_nodes <= 1:
        return perm

    target_indexes = random.sample(range(len(perm)), n_target_nodes)
    shuffled_target_indexes = shuffle_func(target_indexes)

    # shuffle target indexes
    new_perm = perm.copy()
    for shuffled_index, index in zip(shuffled_target_indexes, target_indexes):
        new_perm[shuffled_index] = perm[index]

    return new_perm

