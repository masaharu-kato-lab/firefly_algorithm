import clustering
import build
import numpy as np
from typing import List, Dict, Tuple
Node = Tuple[int, int]

def generate(args, *, nodes:List[Node], dist:callable):

    if args.init_seed == None: args.init_seed = random.randrange(2 ** 32 - 1)
    np.random.seed(seed = args.init_seed)

    if args.init_building_method == 'random':
        return random_generate(nodes = nodes, n_indiv = args.n_indiv)

    if args.init_building_method == 'ann':
        return mix_generate(
            nodes = nodes,
            n_indiv = args.n_indiv,
            clustering_method = args.init_clustering_method,
            n_cluster = args.init_n_cluster,
            nn_rate = args.init_building_nn_rate,
            dist = dist,
            clustering_each = args.init_clustering_each
        )

    if args.init_building_method == 'cpnn':
        return cluster_patterned_generate(
            nodes = nodes,
            n_indiv = args.n_indiv,
            clustering_method = args.init_clustering_method,
            n_cluster = args.init_n_cluster,
            dist = dist,
        )

    
    raise RuntimeError('Unknown initial building method.')



def cluster_patterned_generate(*,
    nodes:List[Node],
    n_indiv:int,
    clustering_method:str,
    n_cluster:int,
    dist:callable,
):

    clusters_nodes = clustering.get_function(method = clustering_method, nodes = nodes, n_cluster = n_cluster, dist = dist)()

    builder = build.Builder(methods_func_dof = {
        'r': (lambda nodes: build.build_randomly(nodes), 1),
        'n': (lambda nodes: build.build_with_nearest_neighbor(nodes, dist), 0),
    }, clusters_nodes = clusters_nodes)

    return builder.build_with_dof(n_indiv)



def mix_generate(*,
    nodes:List[Node],
    n_indiv:int,
    clustering_method:str,
    n_cluster:int,
    dist:callable,
    nn_rate:float,
    clustering_each:bool
):

    clustering_function = clustering.get_function(method = clustering_method, nodes = nodes, n_cluster = n_cluster, dist = dist)

    n_init_random_build = n_indiv * (1.0 - nn_rate)

    x = [None] * n_indiv

    if not clustering_each: clusters_nodes = clustering_function()

    for i in range(len(x)):

        if clustering_each: clusters_nodes = clustering_function()

        if i < n_init_random_build:
            x[i] = build.build_randomly(nodes)
        else:
            x[i] = build_single_by_nearest_neighbor(clusters_nodes, dist_func)

    return x



def random_generate(*, nodes:List[Node], n_indiv:int):
    x = [None] * n_indiv
    for i in range(len(x)):
        x[i] = build.build_randomly(nodes)
    return x

