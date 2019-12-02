import copy
import time

from attrdict import AttrDict #type:ignore

import numpy as np #type:ignore

import permutation

from typing import Any, Callable, cast, Dict, List, Optional, Tuple
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
    nodes           : List[Node],         # List of nodes
    calc_value      : Callable,           # Objective function (originally means light intensity (luminosity) of fireflies)
    gamma           : float,              # gamma value
    alpha           : float,              # alpha value
    blocked_alpha   : float = None,       # alpha value on fireflies are blocked (None to equal to normal alpha)
    continue_coef   : Callable,           # Number of iteration
    skip_check      : bool = False,       # Skip permutation validation if true
    use_jordan_alpha: bool                # Use jordan's method in alpha step
) -> AttrDict:
    
    if not init_indivs: raise RuntimeError('No individuals.')

    if blocked_alpha is None: blocked_alpha = alpha

    x = init_indivs
    val_of = init_val_of if init_val_of else list(map(calc_value, x))

    state = AttrDict()
    state.itr = 0
    state.n_updates = 0
    state.best_itr = 0
    state.best_plan = val_of[np.argmin(val_of)]
    state.n_best_updates = 0
    state.elapsed_time = 0
    state.current_n_updates = 0
    yield state

    indexes = list(range(len(nodes)))
    
    n_updates = 0
    n_best_updates = 0
    best_itr = None
    best_plan = None

    t = 1
    while True:
        start_time = time.time()

        current_n_updates = 0

        sorted_id = np.argsort(val_of)
        x = [x[i] for i in sorted_id]
        val_of = [val_of[i] for i in sorted_id]

        # Repeats for all combinations of fireflies
        for i in range(len(x)):
            for j in range(i):

                # Move firefly 'i' towards firefly 'j' if objective function value of 'j' is smaller than 'i'
                if val_of[i] > val_of[j]:
                    current_n_updates += 1

                    beta = 1 / (1 + gamma * hamming(x[i], x[j]))
                    new_beta_x = beta_step(x[i], x[j], nodes, indexes, beta)
                    x[i] = alpha_step(new_beta_x, indexes, int(np.random.rand() * alpha + 1.0), use_jordan_alpha)
                    val_of[i] = calc_value(x[i])

                    if not skip_check and not permutation.is_valid(x[i], nodes):
                        raise RuntimeError('Invalid permutation.')

        best_id = np.argmin(val_of)

        if current_n_updates == 0:
            for i in range(len(x)):
                if(i != best_id):
                    x[i] = alpha_step(x[i], indexes, int(np.random.rand() * blocked_alpha + 1.0), use_jordan_alpha)
                    val_of[i] = calc_value(x[i])

                    if not skip_check and not permutation.is_valid(x[i], nodes):
                        raise RuntimeError('Invalid permutation.')
                        
            best_id = np.argmin(val_of)



        if best_plan is None or val_of[best_id] < best_plan:
            n_best_updates += 1
            best_itr = t
            best_plan = val_of[best_id]

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

        if not continue_coef(state): break

        t += 1


# Beta step (attract between perm1 and perm2 based on beta value)
def beta_step(perm1:List[Node], perm2:List[Node], nodes:List[Node], indexes:List[int], beta:float):

    perm12:List[Optional[Node]] = [None] * len(perm1)
    empty_nodes   = copy.copy(nodes)
    empty_indexes = copy.copy(indexes)
    
    # calc intersection of perm1 and perm2
    for i in indexes: # DO NOT 'for i in empty_indexes'
        if(perm1[i] == perm2[i]):
            perm12[i] = perm1[i]
            empty_nodes.remove(cast(Node, perm12[i]))
            empty_indexes.remove(i)


    # fill empty indexes in perm12
    for i in empty_indexes:

        # choose candidate node from perm1's node or perm2's based on beta value
        candidate_node = perm1[i] if(np.random.rand() > beta) else perm2[i]

        # fill with chosen candidate node if it doesn't already exist in perm12
        if(candidate_node in empty_nodes):
            perm12[i] = candidate_node
            empty_nodes.remove(candidate_node)
            empty_indexes.remove(i)


    if(len(empty_nodes)):

        # fill empty indexes randomly
        shuffled_empty_nodes = [empty_nodes[i] for i in np.random.permutation(len(empty_nodes))]
        for i, perm12_i in enumerate(empty_indexes):
            perm12[perm12_i] = shuffled_empty_nodes[i]


    return perm12



# Alpha step (randomly swap nodes in permutation based on alpha value)
def alpha_step(perm:List[Node], indexes:List[int], alpha:int, use_jordan_alpha:bool):

    if(alpha <= 1): return perm

    # alpha 個の index を shuffle する
    # set option 'replace=False' to avoid overlaps
    target_indexes = np.random.choice(indexes, alpha, replace=False)
    shuffled_target_indexes = np.random.permutation(target_indexes)

    # shuffle target indexes
    new_perm = copy.copy(perm)
    for shuffled_index, index in zip(shuffled_target_indexes, target_indexes):
        if use_jordan_alpha:
            new_perm[index], new_perm[shuffled_index] = new_perm[shuffled_index], new_perm[index]
        else:
            new_perm[shuffled_index] = perm[index]


    #print('a1:', new_p)
    return new_perm

