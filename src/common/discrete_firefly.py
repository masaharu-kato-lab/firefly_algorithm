import time
import random
import itertools
from attrdict import AttrDict
from common import permutation

from typing import Any, Callable, cast, Set, Dict, List, Optional, Tuple
Node = Tuple[int, int]
Value = Any


def hamming(seq1, seq2):
    L = len(seq1)
    if L != len(seq2):
        raise ValueError("expected two strings of the same length")
    if L == 0:
        return 0  # equal
    return sum(c1 != c2 for c1, c2 in zip(seq1, seq2))


# Firefly algorithm calculation class
def run(*,
    init_indivs     : List[List[Node]],   # Initial individuals permutation
    init_val_of     : List[Value] = None, # Initial individuals evaluation value (optional)
    node_set        : Set[Node],          # Set of node
    calc_value      : Callable[[List[Node]], Any],  # Objective function (originally means light intensity (luminosity) of fireflies)
    ff_dist         : Callable[[List[Node], List[Node]], Any],
    gamma           : float,              # gamma value
    alpha           : float,              # alpha value
    blocked_alpha   : float = None,       # alpha value on fireflies are blocked (None to equal to normal alpha)
    continue_coef   : Callable,           # Number of iteration
    skip_check      : bool = False,       # Skip permutation validation if true
    alpha_shuffle   : Callable[[List[int]], List[int]] # Use jordan's method in alpha step
) -> AttrDict:
    
    if not init_indivs: raise RuntimeError('No individuals.')

    if blocked_alpha is None: blocked_alpha = alpha

    fireflies = init_indivs
    values = init_val_of if init_val_of else list(map(calc_value, fireflies))

    state = AttrDict()
    state.itr = 0
    state.n_updates = 0
    state.best_itr = 0
    state.best_plan = min(range(len(values)), key=lambda i:values[i])
    state.n_best_updates = 0
    state.elapsed_time = 0
    state.current_n_updates = 0
    yield state

    indexes = list(range(len(node_set)))
    
    n_updates = 0
    n_best_updates = 0
    best_itr = None
    best_plan = None

    t = 1
    while continue_coef(state):
        start_time = time.time()

        current_n_updates = 0

        sorted_id = sorted(range(len(values)), key=lambda i:values[i])
        fireflies = [fireflies[i] for i in sorted_id]
        values = [values[i] for i in sorted_id]

        # Repeats for all combinations of fireflies
        # Move firefly 'i' towards firefly 'j' if objective function value of 'j' is smaller than 'i'
        for i, ff_i, ff_j in ((i, fireflies[i], fireflies[j]) for i, j in itertools.combinations(range(len(fireflies)), 2) if values[i] > values[j]):
            current_n_updates += 1
            new_beta_x = beta_step(ff_i, ff_j, 1 / (1 + gamma * ff_dist(ff_i, ff_j)))
            fireflies[i] = alpha_step(new_beta_x, int(random.random() * alpha + 1.0), alpha_shuffle)

        best_id = min(range(len(values)), key=lambda i:values[i])


        if best_plan is None or values[best_id] < best_plan:
            n_best_updates += 1
            best_itr = t
            best_plan = values[best_id]

        n_updates += current_n_updates


        state = AttrDict()
        state.itr = t
        state.n_updates = n_updates
        state.best_itr = best_itr
        state.best_plan = best_plan
        state.n_best_updates = n_best_updates
        state.elapsed_time = time.time() - start_time
        state.current_n_updates = current_n_updates

        yield state
        t += 1


# Beta step (attract between perm1 and perm2 based on beta value)
def beta_step(perm1:List[Node], perm2:List[Node], prob:float):

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


# Alpha step (randomly swap node_set in permutation based on alpha value)
def alpha_step(perm:List[Node], alpha:int, shuffle:Callable[[List[int]], List[int]]):

    if(alpha <= 1): return perm

    # alpha 個の index を shuffle する
    # set option 'replace=False' to avoid overlaps
    target_indexes = random.sample(range(len(perm)), len(perm))
    shuffled_target_indexes = shuffle(target_indexes)

    # shuffle target indexes
    new_perm = perm.copy()
    for shuffled_index, index in zip(shuffled_target_indexes, target_indexes):
        new_perm[shuffled_index] = perm[index]

    return new_perm

