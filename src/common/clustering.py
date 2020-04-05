import argparse
import pickle
import random
import sys

from common.graph import Graph
from typing import Any, Callable, Dict, List, Set, Tuple, Generic, Optional

Node = Generic('Node')

def main():
    argp = argparse.ArgumentParser(description='Clustering set of nodes')
    argp.add_argument('-m' , '--method'    , type=str, required=True, choices=['none', 'rmed', 'pamed'], help='Clustering method')
    argp.add_argument('-nc', '--n_clusters', type=int, help='Number of clusters')
    args = argp.parse_args()
    
    indata = pickle.load(sys.stdin.buffer)
    indata['clusters'] = clustering(args.method, indata['graph'], args.n_cluster)
    pickle.dump(indata, sys.stdout.buffer)
    return 0


def clustering(method:str, graph:Graph, n_cluster:Optional[int]) -> Dict[Node, Set[Node]]:
    if method == 'none':
        return {None: graph.node_set.copy()}
    if method == 'rmed':
        return random_k_medoids(graph, n_cluster)
    if method == 'pamed':
        return partitioning_around_medoids(graph, n_cluster)
    raise RuntimeError('No such clustering method `{}`'.format(method))


def random_k_medoids(graph:Graph, n_cluster:int) -> Dict[Node, Set[Node]]:
    return generate_clusters(graph, random.sample(graph.node_set, n_cluster))


def partitioning_around_medoids(graph:Graph, n_cluster:int) -> Dict[Node, Set[Node]]:

    # generate initial medoids randomly
    medoids = random.sample(graph.node_set, n_cluster)

    while True:
        clusters = generate_clusters(graph, medoids)

        # change medoid on each clusters, and search best change
        best_medoids = None
        best_cost = None
        for medoid, nodes in clusters.items():
            for node in nodes:
                c_medoids = medoids.copy()
                c_medoids.remove(medoid).add(node)
                _, c_cost = generate_clusters(graph, c_medoids)
                if best_cost is None or c_cost < best_cost:
                    best_cost = c_cost
                    best_medoids = c_medoids

        # if best change does not decrease cost, terminate
        if best_cost >= clusters_cost(graph, clusters): break

        medoids = best_medoids

    return clusters


def generate_clusters(graph:Graph, medoids:Set[Node]) -> Dict[Node, Set[Node]]:

    clusters = {medoid:{medoid} for medoid in medoids}

    for node in graph.node_set.difference(medoids):
        clusters[graph.nearest(node, medoids)].add(node)

    return clusters.values()


def clusters_cost(graph:Graph, clusters:Dict[Node, Set[Node]]) -> Any:
    return sum(sum(graph.dist(medoid, node) for node in nodes) for medoid, nodes in clusters.items())
