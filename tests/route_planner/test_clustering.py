from route_planner.clustering import Clustering
import field_for_test as fl
from common_library import permutation
import itertools

n_cluster = 3
clustering = Clustering(nodes=fl.nodes, n_cluster=n_cluster, dist=fl.dist, allow_same_dist=False)

def test_no_clustering():
    assert clustering.no_clustering() == [fl.nodes]


def test_medoids_cluster():
    medoids = fl.nodes_of_str('BEI')
    ans_clusters_nodes = list(map(fl.nodes_of_str, ['BACD', 'EGH', 'IFJK']))
    ans_total_costs = [sum(fl.dist(medoid, node) for node in cluster_nodes) for medoid, cluster_nodes in zip(medoids, ans_clusters_nodes)]
    ans = [(clusters_nodes, total_cost) for clusters_nodes, total_cost in zip(ans_clusters_nodes, ans_total_costs)]
    assert clustering.medoids_cluster(medoids) == ans


def test_choice_random_medoids():
    ret = clustering.choice_random_medoids()
    assert len(ret) == n_cluster and len(set(ret)) == n_cluster and all(node in fl.nodes for node in ret)


def test_random_medoids():
    ret = clustering.random_medoids()
    assert len(ret) == n_cluster and permutation.is_valid(itertools.chain(ret), fl.nodes)


def test_partitioning_around_medoids():
    ret = clustering.partitioning_around_medoids()
    assert len(ret) == n_cluster and permutation.is_valid(itertools.chain(ret), fl.nodes)


