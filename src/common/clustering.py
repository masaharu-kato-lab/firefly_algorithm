import argparse
import pickle
import random
import sys
from dataclasses import dataclass

import pipeit

from common.graph import Graph
from typing import Any, Callable, Dict, List, Set, Tuple, Generic, Optional

Node = Generic('Node')
Dist = Generic('Dist')

def main():
    argp = argparse.ArgumentParser(description='Clustering set of nodes')
    argp.add_argument('-m' , '--method'    , type=str, required=True, choices=['rmed', 'pamed'], help='Clustering method')
    argp.add_argument('-nc', '--n_clusters', type=int, help='Number of clusters')
    args = argp.parse_args()


    clustering_functions = {
        'rmed'  : random_k_medoids,
        'pamed' : partitioning_around_medoids,
    }

    pipeit.pipeit_with_data(
        args,
        lambda indata, outdata: outdata.cluster_set = clustering_functions[args.method](indata.graph, args.n_clusters)
    )



@dataclass
class Cluster(Generic[Node]):
    medoid : Node
    nodes  : Set[Node] = set()

    def add(self, node:Node):
        self.nodes.add(node)


class ClusterSet(Generic[Node, Dist]):

    @classmethod
    def init_with_medoids(cls, graph:Graph[Node, Dist], medoids:Set[Node]):
        return cls.__new__()._init_with_medoid(graph, medoids)


    def _init_with_medoids(self, graph:Graph[Node, Dist], medoids:Set[Node]):
        self.clusters_by_medoid = {medoid:{medoid} for medoid in medoids}
        self.cost:float = 0
        for node in graph.node_set.difference(medoids):
            nearest_medoid, nearest_medoid_dist = graph.nearest_and_its_dist(node, medoids)
            self.clusters_by_medoid[nearest_medoid].add(node)
            self.cost += nearest_medoid_dist


    def __iter__(self):
        return self.clusters_by_medoid.items()

    def medoid_of(self, medoid:Node):
        return self.clusters_by_medoid[medoid]



def random_k_medoids(graph:Graph, n_cluster:int) -> ClusterSet:
    return ClusterSet.init_with_medoids(graph, random.sample(graph.node_set, n_cluster))


def partitioning_around_medoids(graph:Graph, n_cluster:int) -> ClusterSet:

    # generate initial medoids randomly
    medoids = set(random.sample(graph.node_set, n_cluster))
    cluster_set = ClusterSet.init_with_medoids(graph, medoids)

    while True:
        # change medoid on each clusters, and search best change
        best_new_cluster_set = None

        for cluster in cluster_set:
            existing_medoids = medoids - {cluster.medoid}
            for node in cluster.nodes:
                new_cluster_set = ClusterSet.init_with_medoids(graph, existing_medoids | {node})
                if best_new_cluster_set is None or new_cluster_set.cost < best_new_cluster_set.cost:
                    best_new_cluster_set = new_cluster_set

        # if best change does not decrease cost, terminate
        if best_new_cluster_set.cost >= cluster_set.cost: break

        cluster_set = best_new_cluster_set

    return cluster_set

