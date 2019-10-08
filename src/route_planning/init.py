import numpy as np
import copy
import random
# from types import List, Dict, Tuple, Node

from typing import List, Dict, Tuple
Node = Tuple[int, int]


def generate(*,
    nodes:List[Node],
    n_firefly:int,
    clustering_method:str,
    n_cluster:int,
    nn_rate:float,
    dist_func:callable
):

    clustering_function = get_clustering_function(
        method = clustering_method,
        nodes = nodes,
        n_cluster = n_cluster,
        dist_func = dist_func,
    )

    n_init_random_build = n_firefly * (1.0 - nn_rate)

    x = [0] * n_firefly

    for i in range(len(x)):

        clusters_nodes = clustering_function()

        if i < n_init_random_build:
            x[i] = build_randomly(nodes)
        else:
            x[i] = build_single_by_nearest_neighbor(clusters_nodes, dist_func)

    return x


def get_clustering_function(*, method:str, nodes:List[Node], n_cluster:int, dist_func:callable):

    if method == None:
        return lambda: no_clustering(nodes)

    elif method == 'rm':
        return lambda: random_medoids(nodes, n_cluster, dist_func)

    elif method == 'pam':
        return lambda: partitioning_around_medoids(nodes, n_cluster, dist_func)

    else:
        raise RuntimeError('Unknown method name.')


def no_clustering(nodes:List[Node]):
    return [nodes]


def medoids_cluster(nodes:List[Node], medoids:List[Node], dist:callable):

    clusters_nodes = [[medoid] for medoid in medoids]
    total_cost = 0 # sum of distance between each nodes and its medoid in each clusters

    for node in nodes:
        # calc distance from each medoids, and nearset cluster and its distance
        dist_from_medoids = [dist(medoid, node) for medoid in medoids]
        i_cluster = np.argmin(dist_from_medoids)
        if node != clusters_nodes[i_cluster][0]:
            clusters_nodes[i_cluster].append(node)
            total_cost += dist_from_medoids[i_cluster]

    return clusters_nodes, total_cost


def choice_random_medoids(nodes:List[Node], n_cluster:int):
    return [nodes[i] for i in np.random.choice(len(nodes), n_cluster, replace=False)]


def random_medoids(nodes:List[Node], n_cluster:int, dist:callable):
    clusters_nodes, _ = medoids_cluster(nodes, choice_random_medoids(nodes, n_cluster), dist)
    return clusters_nodes


def partitioning_around_medoids(nodes:List[Node], n_cluster:int, dist:callable):

    # generate initial medoids randomly
    medoids = choice_random_medoids(nodes, n_cluster)

    while True:
        clusters_nodes, original_cost = medoids_cluster(nodes, medoids, dist)

        # change medoid on each clusters, and search best change
        best_medoids = None
        best_cost = None
        for i_cluster in range(n_cluster):
            for node in clusters_nodes[1:]:
                c_medoids = copy.copy(medoids)
                c_medoids[i_cluster] = node
                _, c_cost = medoids_cluster(nodes, c_medoids, dist)
                if best_cost is None or c_cost < best_cost:
                    best_cost = c_cost
                    best_medoids = c_medoids

        # if best change does not decrease cost, terminate
        if best_cost >= original_cost: break

        medoids = best_medoids

    return clusters_nodes

    
def build_single_by_nearest_neighbor(clusters_nodes:List[List[Node]], dist_func:callable, nn_n_random:int = 1):
    ordered_nodes = []
    for nodes in clusters_nodes:
        ordered_nodes.extend(build_by_nearest_neighbor(nodes, dist_func, nn_n_random))
    return ordered_nodes


def build_by_nearest_neighbor(nodes:List[Node], dist:callable, nn_n_random:int = 1):

    ordered_nodes = []
    remain_nodes = copy.copy(nodes)
    last_node = None

    for i_itr in range(len(nodes)):

        if i_itr < nn_n_random:
            min_id = np.random.choice(range(len(remain_nodes)))
        else:
            min_id = np.argmin([dist(last_node, node) for node in remain_nodes])
        
        last_node = remain_nodes[min_id]
        ordered_nodes.append(last_node)
        remain_nodes.pop(min_id)

    return ordered_nodes


def build_randomly(nodes:List[Node]):
    return [nodes[i] for i in np.random.permutation(len(nodes))]
