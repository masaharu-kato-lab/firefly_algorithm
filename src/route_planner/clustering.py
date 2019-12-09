import numpy as np #type:ignore
import copy

from typing import Callable, Dict, List, Tuple
Node = Tuple[int, int]


# get function (lambda) from clustering method name
def get_function(*, method:str, nodes:List[Node], n_cluster:int, dist:Callable) -> Callable:

    method = method.lower()

    if method == 'none':
        return lambda: no_clustering(nodes)

    elif method == 'rmed':
        if n_cluster is None: raise RuntimeError('Number of cluster not specified.')
        return lambda: random_medoids(nodes, n_cluster, dist)

    elif method == 'pamed':
        if n_cluster is None or dist is None: raise RuntimeError('Number of cluster or distance function not specified.')
        return lambda: partitioning_around_medoids(nodes, n_cluster, dist)

    else:
        raise RuntimeError('Unknown method name.')


def no_clustering(nodes:List[Node]):
    return [nodes]


def medoids_cluster(nodes:List[Node], medoids:List[Node], dist:Callable):

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


def random_medoids(nodes:List[Node], n_cluster:int, dist:Callable):
    clusters_nodes, _ = medoids_cluster(nodes, choice_random_medoids(nodes, n_cluster), dist)
    return clusters_nodes


def partitioning_around_medoids(nodes:List[Node], n_cluster:int, dist:Callable):

    # generate initial medoids randomly
    medoids = choice_random_medoids(nodes, n_cluster)

    while True:
        clusters_nodes, original_cost = medoids_cluster(nodes, medoids, dist)

        # change medoid on each clusters, and search best change
        best_medoids = None
        best_cost = None
        for i_cluster in range(n_cluster):
            for node in clusters_nodes[i_cluster][1:]:
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


