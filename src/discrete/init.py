import numpy as np
import copy

def nearest_naver(nodes : list, dist : callable, *, n_random = 1):
    perm = []
    remain_nodes = copy.copy(nodes)

    for _ in range(n_random):
        node = np.random.choice(remain_nodes)
        perm.append(node)
        remain_nodes.remove(node)

    while(len(remain_nodes)):
        min_id = np.argmin([dist(np.concatenate([perm, [node]])) for node in remain_nodes])
        
        perm.append(remain_nodes[min_id])
        remain_nodes.pop(min_id)

    return perm
