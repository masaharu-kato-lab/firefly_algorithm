import numpy as np
import copy
import time
import attrdict
import distance
import permutation
# from types import List, Dict, Tuple, Node

from typing import Any, List, Dict, Tuple
Node = Tuple[int, int]
Indiv = List[List[Node]]
Value = Any

# Firefly algorithm calculation class
def run(*,
    init_indivs   : List[Indiv],        # Initial individuals permutation
    init_val_of   : List[Value] = None, # Initial individuals evaluation value (optional)
    nodes         : List[Node],         # List of nodes
    calc_value    : callable,           # Objective function (originally means light intensity (luminosity) of fireflies)
    gamma         : float,              # gamma value
    alpha         : float,              # alpha value
    blocked_alpha : float = None,       # alpha value on fireflies are blocked (None to equal to normal alpha)
    continue_coef : callable,           # Number of iteration
    skip_check    : bool = False        # Skip permutation validation if true
):
    
    if blocked_alpha is None: blocked_alpha = alpha

    x = init_indivs
    val_of = init_val_of if init_val_of else list(map(calc_value, x))

    indexes = list(range(len(nodes)))

    ret = attrdict.AttrDict()
    ret.best_itr = None
    ret.best_plan = None

    t = 0
    while True:
        start_time = time.time()

        n_attracted = 0

        sorted_id = np.argsort(val_of)
        x = [x[i] for i in sorted_id]
        val_of = [val_of[i] for i in sorted_id]

        # Repeats for all combinations of fireflies
        for i in range(len(x)):
            for j in range(i):

                # Move firefly 'i' towards firefly 'j' if objective function value of 'j' is smaller than 'i'
                if val_of[i] > val_of[j]:
                    n_attracted += 1

                    beta = 1 / (1 + gamma * distance.hamming(x[i], x[j]))
                    new_beta_x = beta_step(x[i], x[j], nodes, indexes, beta)
                    x[i] = alpha_step(new_beta_x, indexes, int(np.random.rand() * alpha + 1.0))
                    val_of[i] = calc_value(x[i])

                    if not skip_check and not permutation.is_valid(x[i], nodes):
                        raise RuntimeError('Invalid permutation.')

        best_id = np.argmin(val_of)

        if n_attracted == 0:
            for i in range(len(x)):
                if(i != best_id):
                    x[i] = alpha_step(x[i], indexes, int(np.random.rand() * blocked_alpha + 1.0))
                    val_of[i] = calc_value(x[i])

                    if not skip_check and not permutation.is_valid(x[i], nodes):
                        raise RuntimeError('Invalid permutation.')
                        
            best_id = np.argmin(val_of)

        ret.elapsed_time = time.time() - start_time
        ret.c_n_attracted = n_attracted
        ret.c_itr = t

        if ret.best_plan is None or val_of[best_id] < ret.best_plan:
            ret.prev_best_itr = ret.best_itr
            ret.best_itr = t
            ret.best_id = best_id
            ret.best_plan = val_of[best_id]
            ret.best_n_attracted = n_attracted

        if not continue_coef(ret): break

        t += 1
        yield ret



# Beta step (attract between perm1 and perm2 based on beta value)
def beta_step(perm1:Indiv, perm2:Indiv, nodes:List[Node], indexes:List[int], beta:float):

    perm12 = [None] * len(perm1)
    empty_nodes   = copy.copy(nodes)
    empty_indexes = copy.copy(indexes)
    
    # calc intersection of perm1 and perm2
    for i in indexes: # DO NOT 'for i in empty_indexes'
        if(perm1[i] == perm2[i]):
            perm12[i] = perm1[i]
            empty_nodes.remove(perm12[i])
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
def alpha_step(perm:Indiv, indexes:List[int], alpha:int):

    if(alpha <= 1): return perm

    # alpha 個の index を shuffle する
    # set option 'replace=False' to avoid overlaps
    target_indexes = np.random.choice(indexes, alpha, replace=False)
    shuffled_target_indexes = np.random.permutation(target_indexes)

    # shuffle target indexes
    new_perm = copy.copy(perm)
    for shuffled_index, index in zip(shuffled_target_indexes, target_indexes):
        #new_perm[shuffled_index] = perm[index]
        new_perm[index], new_perm[shuffled_index] = new_perm[shuffled_index], new_perm[index]


    #print('a1:', new_p)
    return new_perm

