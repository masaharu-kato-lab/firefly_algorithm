import random
from common.graph import Graph

from typing import Any, Callable, Dict, List, Set, Tuple, Generic

Node = Generic('Node')


def no_clustering(self) -> Dict[Node, Set[Node]]:
    return {None: self.node_set.copy()}


def random_k_medoids(graph:Graph, n_cluster:int) -> Dict[Node, Set[Node]]:
    return calc_clusters(graph, random.sample(graph.node_set, n_cluster))


def partitioning_around_medoids(graph:Graph, n_cluster:int) -> List[Set[Node]]:

    # generate initial medoids randomly
    medoids = random.sample(graph.node_set, n_cluster)

    while True:
        clusters = calc_clusters(graph, medoids)

        # change medoid on each clusters, and search best change
        best_medoids = None
        best_cost = None
        for medoid, nodes in clusters.items():
            for node in nodes:
                c_medoids = medoids.copy()
                c_medoids.remove(medoid).add(node)
                _, c_cost = calc_clusters(graph, c_medoids)
                if best_cost is None or c_cost < best_cost:
                    best_cost = c_cost
                    best_medoids = c_medoids

        # if best change does not decrease cost, terminate
        if best_cost >= clusters_cost(graph, clusters): break

        medoids = best_medoids

    return clusters


def calc_clusters(graph:Graph, medoids:Set[Node]) -> Dict[Node, Set[Node]]:

    clusters = {medoid:set() for medoid in medoids}

    for node in graph.node_set.difference(medoids):
        clusters[graph.nearest(node, medoids)].add(node)

    return clusters.values()


def clusters_cost(graph:Graph, clusters:Dict[Node, Set[Node]]) -> Any:
    return sum(sum(graph.dist(medoid, node) for node in nodes) for medoid, nodes in clusters.items())
