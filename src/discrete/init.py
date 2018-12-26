import numpy as np
import copy
import random


def randomly(nodes : list):
    return np.random.permutation(nodes)


def cluster(base_nodes, nodes : list, dist : callable):

    nodes_in_classes = []

    for base_node in base_nodes:
        nodes_in_classes.append([base_node])

    for node in nodes:
        class_id = np.argmin([dist([base_node, node]) for base_node in base_nodes])
        nodes_in_classes[class_id].append(node)

    return nodes_in_classes




def k_means_nearest_neighbor(nodes : list, dist : callable, k : int):
    
    base_nodes = np.random.choice(nodes, k, replace=False)

    remain_nodes = copy.copy(nodes)
    for base_node in base_nodes:
        remain_nodes.remove(base_node)

    nodes_in_classes = cluster(base_nodes, remain_nodes, dist)

    perm = []

    for nodes_in_class in nodes_in_classes:
        perm += nearest_neighbor(nodes_in_class, dist)

    return perm



def nearest_neighbor(nodes : list, dist : callable, n_random = 1):

    if not len(nodes): return []

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



def method(init_type : str, dist : callable, seed : int, *, knn_k : int):

    # Set seed value of random for initialization
    if seed == None: seed = random.randrange(2 ** 32 - 1)
    np.random.seed(seed = seed)


    if(init_type == 'random'):
        init_method = lambda nodes : randomly(nodes)

    elif(init_type == 'nn'):
        init_method = lambda nodes : nearest_neighbor(nodes, dist)

    elif(init_type == 'knn'):
        if knn_k == None: raise RuntimeError('K value for k-nearest neighbor initialization unspecified.')
        init_method = lambda nodes : k_means_nearest_neighbor(nodes, dist, knn_k)

    else:
        raise RuntimeError('Invalid name of initialization method.')


    return init_method
