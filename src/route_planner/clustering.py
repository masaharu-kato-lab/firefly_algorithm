import numpy as np #type:ignore
import copy
import functools

from typing import Callable, Dict, List, Tuple, Iterable
Node = Tuple[int, int]


# get function (lambda) from clustering method name
def get_function(*, method:str, nodes:List[Node], n_cluster:int, dist:Callable, dist_compare:Callable) -> Callable:

    method = method.lower()

    if method == 'none':
        return lambda: no_clustering(nodes)

    elif method == 'rmed':
        if n_cluster is None: raise RuntimeError('Number of cluster not specified.')
        return lambda: random_medoids(nodes, n_cluster, dist, dist_compare)

    elif method == 'pamed':
        if n_cluster is None or dist is None: raise RuntimeError('Number of cluster or distance function not specified.')
        return lambda: partitioning_around_medoids(nodes, n_cluster, dist, dist_compare)

    else:
        raise RuntimeError('Unknown method name.')


def no_clustering(nodes:List[Node]):
    return [nodes]


def medoids_cluster(nodes:List[Node], medoids:List[Node], dist:Callable, dist_compare:Callable):

    clusters_nodes = [[medoid] for medoid in medoids]
    total_cost = 0 # sum of distance between each nodes and its medoid in each clusters

    for node in nodes:
        # calc distance from each medoids, and nearset cluster and its distance
        dists = [dist(medoid, node) for medoid in medoids]
        min_dist = min(dists, key=functools.cmp_to_key(dist_compare))
        i_clusters = [i for i, dist in enumerate(dists) if dist == min_dist]
    
        if len(i_clusters) > 1:
            raise RuntimeError('Same distance values.')
        i_cluster = i_clusters[0]

        # if len(i_clusters) > 1: print("choice one from multiple.")
        # i_cluster = np.random.choice(i_clusters) if len(i_clusters) > 1 else i_clusters[0]

        if node != clusters_nodes[i_cluster][0]:
            clusters_nodes[i_cluster].append(node)
            c_dist = dists[i_cluster]
            total_cost += c_dist[0] if isinstance(c_dist, Iterable) else c_dist

    return clusters_nodes, total_cost


def choice_random_medoids(nodes:List[Node], n_cluster:int):
    return [nodes[i] for i in np.random.choice(len(nodes), n_cluster, replace=False)]


def random_medoids(nodes:List[Node], n_cluster:int, dist:Callable, dist_compare:Callable):
    clusters_nodes, _ = medoids_cluster(nodes, choice_random_medoids(nodes, n_cluster), dist, dist_compare)
    return clusters_nodes


def partitioning_around_medoids(nodes:List[Node], n_cluster:int, dist:Callable, dist_compare:Callable):

    # generate initial medoids randomly
    medoids = choice_random_medoids(nodes, n_cluster)

    while True:
        clusters_nodes, original_cost = medoids_cluster(nodes, medoids, dist, dist_compare)

        # change medoid on each clusters, and search best change
        best_medoids = None
        best_cost = None
        for i_cluster in range(n_cluster):
            for node in clusters_nodes[i_cluster][1:]:
                c_medoids = copy.copy(medoids)
                c_medoids[i_cluster] = node
                _, c_cost = medoids_cluster(nodes, c_medoids, dist, dist_compare)
                if best_cost is None or c_cost < best_cost:
                    best_cost = c_cost
                    best_medoids = c_medoids

        # if best change does not decrease cost, terminate
        if best_cost >= original_cost: break

        medoids = best_medoids

    return clusters_nodes


