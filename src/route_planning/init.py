import numpy as np
import copy
import random


def generate(*, number:int, clustering_function:callable, nn_rate:float, dist_func:callable):

    n_init_random_build = number * (1.0 - nn_rate)

    x = [0] * number

    for i in range(len(x)):

        clusters_nodes = clustering_function()

        if i < n_init_random_build:
            x[i] = build_randomly(clusters_nodes)
        else:
            x[i] = build_by_nearest_neighbor(clusters_nodes, dist_func)

    return x


def get_clustering_function(*, method : str, nodes : list, n_cluster : int, dist_func:callable):

    if method == None:
        return lambda: no_clustering(nodes)

    elif method == 'rm':
        return lambda: random_medoids(nodes, n_cluster, dist_func)

    elif method == 'pam':
        return lambda: partitioning_around_medoids(nodes, n_cluster, dist_func)

    else:
        raise RuntimeError('Unknown method name.')


def no_clustering(nodes:list):
    return [nodes]


def medoids_cluster(nodes:list, medoids:list, dist:callable):

    clusters_nodes = [[base_node] for base_node in range(len(medoids))]
    total_cost = 0 # sum of distance between each nodes and its medoid in each clusters

    for node in nodes:
        # calc distance from each medoids, and nearset cluster and its distance
        dist_from_medoids = [dist(base_node, node) for base_node in medoids]
        i_cluster = np.argmin(dist_from_medoids)
        if node != clusters_nodes[i_cluster][0]:
            clusters_nodes[i_cluster].append(node)
            total_cost += dist_from_medoids[i_cluster]

    return clusters_nodes, total_cost


def choice_random_medoids(nodes:list, n_cluster:int):
    return np.random.choice(nodes, n_cluster, replace=False)


def random_medoids(nodes:list, n_cluster:int, dist:callable):
    clusters_nodes, _ = medoids_cluster(nodes, choice_random_medoids(nodes, n_cluster), dist)
    return clusters_nodes


def partitioning_around_medoids(nodes:list, n_cluster:int, dist:callable):

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

    

def build_by_nearest_neighbor(nodes : list, dist : callable, nn_n_random : int = 1):

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


def build_randomly(nodes : list):
    return np.random.permutation(nodes)

