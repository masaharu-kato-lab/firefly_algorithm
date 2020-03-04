import numpy as np #type:ignore
import copy

from typing import Callable, Dict, List, Tuple
Node = Tuple[int, int]



class Clustering:

    def __init__(self, *, nodes:List[Node], n_cluster:int, dist:Callable, allow_same_dist:bool):
        self.nodes = nodes
        self.n_cluster = n_cluster
        self.dist = dist
        self.allow_same_dist = allow_same_dist


    # get function (lambda) from clustering method name
    def get_function(self, method:str) -> Callable:

        method = method.lower()

        if method == 'none':
            return lambda: self.no_clustering()

        elif method == 'rmed':
            # if self.n_cluster is None: raise RuntimeError('Number of cluster not specified.')
            return lambda: self.random_medoids()

        elif method == 'pamed':
            # if self.n_cluster is None or self.dist is None: raise RuntimeError('Number of cluster or distance function not specified.')
            return lambda: self.partitioning_around_medoids()

        else:
            raise RuntimeError('Unknown method name.')


    def no_clustering(self) -> List[List[Node]]:
        return [self.nodes]


    def medoids_cluster(self, medoids:List[Node]) -> Tuple[List[List[Node]], float]:

        clusters_nodes = [[medoid] for medoid in medoids]
        total_cost = 0 # sum of distance between each self.nodes and its medoid in each clusters

        for node in self.nodes:
            # calc distance from each medoids, and nearset cluster and its distance
            dists = np.array([self.dist(medoid, node) for medoid in medoids])
            i_clusters = np.where(dists == dists.min())[0]
            if len(i_clusters) > 1:
                if not self.allow_same_dist: raise RuntimeError('Same distance of self.nodes is not allowed.')
                i_cluster = np.random.choice(i_clusters)
            else:
                i_cluster = i_clusters[0]


            if node != clusters_nodes[i_cluster][0]:
                clusters_nodes[i_cluster].append(node)
                total_cost += dists[i_cluster]

        return clusters_nodes, total_cost


    def choice_random_medoids(self) -> List[Node]:
        return [self.nodes[i] for i in np.random.choice(len(self.nodes), self.n_cluster, replace=False)]


    def random_medoids(self) -> List[List[Node]]:
        clusters_nodes, _ = self.medoids_cluster(self.choice_random_medoids())
        return clusters_nodes


    def partitioning_around_medoids(self):

        # generate initial medoids randomly
        medoids = self.choice_random_medoids()

        while True:
            clusters_nodes, original_cost = self.medoids_cluster(medoids)

            # change medoid on each clusters, and search best change
            best_medoids = None
            best_cost = None
            for i_cluster in range(self.n_cluster):
                for node in clusters_nodes[i_cluster][1:]:
                    c_medoids = copy.copy(medoids)
                    c_medoids[i_cluster] = node
                    _, c_cost = self.medoids_cluster(c_medoids)
                    if best_cost is None or c_cost < best_cost:
                        best_cost = c_cost
                        best_medoids = c_medoids

            # if best change does not decrease cost, terminate
            if best_cost >= original_cost: break

            medoids = best_medoids

        return clusters_nodes


