import clustering
import build
import numpy as np #type:ignore
import random
import route
import distances
from typing import Callable, Dict, List, Optional, Tuple
Node = Tuple[int, int]

import permutation


def generate(args, *, path_data:route.PathData) -> List[List[Node]]:
    
    indivs = _generate(args, path_data = path_data)

    if not all([permutation.is_valid(indiv, path_data.nodes) for indiv in indivs]):
       raise RuntimeError('Invalid individuals.')
    # for i, indiv in enumerate(indivs):
    #     if not permutation.is_valid(indiv, path_data.nodes):
    #         raise RuntimeError('Invalid individuals.')

    return indivs



def _generate(args, *, path_data:route.PathData) -> List[List[Node]]:

    np.random.seed(seed = args.init_seed)
    bld_method = args.init_bld_method.lower()

    # if bld_method == 'random':
    #     return random_generate(nodes = path_data.nodes, n_indiv = args.n_indiv)

    bld_dist = distances.get_func(args.init_bld_dist, path_data = path_data) # , w_angle=args.init_bld_dist_w
    cls_dist = distances.get_func(args.init_cls_dist, path_data = path_data) # , w_angle=args.init_cls_dist_w

    if bld_method == 'rnn':
        return mix_generate(
            nodes = path_data.nodes,
            n_indiv = args.n_indiv,
            cls_method = args.init_cls_method,
            n_cluster = args.init_n_cls,
            nn_rate = args.init_bld_nn_rate,
            bld_dist = bld_dist,
            cls_dist = cls_dist,
            cls_each = args.init_cls_each
        )

    elif bld_method == 'cpnn':
        return cluster_patterned_generate(
            nodes = path_data.nodes,
            n_indiv = args.n_indiv,
            cls_method = args.init_cls_method,
            n_cluster = args.init_n_cls,
            bld_dist = bld_dist,
            cls_dist = cls_dist,
        )

    else:
        raise RuntimeError('Unknown initial building method.')



def cluster_patterned_generate(*,
    nodes:List[Node],
    n_indiv:int,
    cls_method:str,
    n_cluster:int,
    cls_dist:Callable,
    bld_dist:Callable,
):

    clusters_nodes = clustering.get_function(method = cls_method, nodes = nodes, n_cluster = n_cluster, dist = cls_dist)()

    builder = build.Builder(methods_func_dof = {
        'r': (lambda nodes: build.build_randomly(nodes), 1),
        'n': (lambda nodes: build.build_with_nearest_neighbor(nodes, bld_dist), 0),
    }, clusters_nodes = clusters_nodes)

    return builder.build_with_dof(n_indiv)



def mix_generate(*,
    nodes:List[Node],
    n_indiv:int,
    cls_method:str,
    n_cluster:int,
    cls_dist:Callable,
    bld_dist:Callable,
    nn_rate:float,
    cls_each:bool
):

    clustering_function = clustering.get_function(method = cls_method, nodes = nodes, n_cluster = n_cluster, dist = cls_dist)

    n_init_random_build = n_indiv * (1.0 - nn_rate)

    x:List[List[Node]] = []

    if not cls_each: clusters_nodes = clustering_function()

    for i in range(len(x)):

        if cls_each: clusters_nodes = clustering_function()

        if i < n_init_random_build:
            x.append(build.build_single_with_random(clusters_nodes))
        else:
            x.append(build.build_single_with_nearest_neighbor(clusters_nodes, bld_dist))

    return x



def random_generate(*, nodes:List[Node], n_indiv:int):
    x:List[List[Node]] = []
    for _ in range(len(x)):
        x.append(build.build_randomly(nodes))
    return x

