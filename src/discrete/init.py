import numpy as np
import copy
import random


class Clustering:

    def __init__(*, nodes : list, dist : callable, n_cluster : int):
        self.nodes = nodes
        self.dist = dist
        self.n_cluster = n_cluster


    def medoids_cluster(self, medoids : list):

        clusters_nodes = [[base_node] for base_node in range(len(medoids))]
        total_cost = 0 # sum of distance between each nodes and its medoid in each clusters

        for node in self.nodes:
            # calc distance from each medoids, and nearset cluster and its distance
            dist_from_medoids = [self.dist(base_node, node) for base_node in medoids]
            i_cluster = np.argmin(dist_from_medoids)
            if node != clusters_nodes[i_cluster][0]:
                clusters_nodes[i_cluster].append(node)
                total_cost += dist_from_medoids[i_cluster]

        return clusters_nodes, total_cost


    def choice_random_medoids(self):
        return np.random.choice(self.nodes, self.n_cluster, replace=False)


    def random_medoids(self):
        clusters_nodes, _ =  medoids_cluster(self.choice_random_medoids())
        return clusters_nodes


    def partitioning_around_medoids(self):

        # generate initial medoids randomly
        medoids = self.choice_random_medoids()

        while True:
            clusters_nodes, original_cost = medoids_cluster(medoids)

            # change medoid on each clusters, and search best change
            best_medoids = None
            best_cost = None
            for i_cluster in range(self.n_cluster):
                for node in clusters_nodes[1:]:
                    c_medoids = copy.copy(medoids)
                    c_medoids[i_cluster] = node
                    _, c_cost = medoids_cluster(c_medoids)
                    if best_cost is None or c_cost < best_cost:
                        best_cost = c_cost
                        best_medoids = c_medoids

            # if best change does not decrease cost, terminate
            if best_cost >= original_cost: break

            medoids = best_medoids

        return clusters_nodes

        
    def apply(self, method_name : str):

        if method_name == None:
            nodes_list = nodes

        elif method_name == 'rm':
            nodes_list = self.random_medoids()

        elif method_name == 'pam':
            nodes_list = self.partitioning_around_medoids()

        else:
            raise RuntimeError('Unknown method name.')

        return nodes_list



def nearest_neighbor(target_nodes : list, dist : callable, nn_n_random : int = 1):

    ordered_nodes = []
    remain_nodes = copy.copy(target_nodes)
    last_node = None

    for i_itr in range(len(target_nodes)):

        if i_itr < nn_n_random:
            min_id = np.random.choice(range(len(remain_nodes)))
        else:
            min_id = np.argmin([dist(last_node, node) for node in remain_nodes])
        
        last_node = remain_nodes[min_id]
        ordered_nodes.append(last_node)
        remain_nodes.pop(min_id)

    return ordered_nodes

