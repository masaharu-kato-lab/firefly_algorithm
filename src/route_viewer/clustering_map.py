#!env/bin/python
import pickle
import argparse
import matplotlib.pyplot as plt
import sys
import os
import json
from world import World
import random
import numpy as np

sys.path.append(os.path.dirname(__file__) + '/../route_planner')
import init
import route
import distances

def main():

    argp = argparse.ArgumentParser(description='Route binary viewer')
    argp.add_argument('-o', '--output', type=str, default=None, help='Output png image formatted file path (None:default)')
    argp.add_argument('-mi', '--mapper_input', type=str, default='res/pathdata/opu.pickle', help='Input mapper pickle file path')
    argp.add_argument('-s'  , '--seed' , type=int  , default =None    , help='Seed value for random in initialization')
    argp.add_argument('-n'  , '--number' , type=int  , default =None    , help='Number of generating')
    argp.add_argument('-cm' , '--cls_method' , type=str, required=True, choices=["none", "rmed", "pamed"], help="Clustering method in initialization, 'none' for no clustering, 'rmed' (random medoids) or 'pamed' (partitioning around medoids)")
    argp.add_argument('-cdm', '--cls_dist'   , type=str, required=True, choices=["euclid", "aster", "angle", "polar"], help="Distance method in initial clustering (only works when clustering is available)")
    argp.add_argument('-nc' , '--n_cls'      , type=int, required=True, help="Number of clusters (only works when `--cls_method` is not 'none')")
    # argp.add_argument('-bm' , '--bld_method' , type=str  , default ="cpnn"  , choices=["rnn", "cpnn"], help="Building method in initialization, 'rnn' (mix of random generation and nearest neighbor), 'cpnn' (cluster-patterned nearest neighbor)")
    # argp.add_argument('-bdm', '--bld_dist'   , type=str  , default =None    , choices=["euclid", "aster", "angle", "polar"], help="Distance method in initial building")
   
    args = argp.parse_args()

    if args.seed == None: args.seed = random.randrange(2 ** 32 - 1)
    print('seed={}'.format(args.seed))

    world = World(args.mapper_input)
    path_data = route.PathData(args.mapper_input)

    
    cmap = plt.get_cmap("tab10")
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    for ni in range(args.seed, args.seed + args.number):
        np.random.seed(seed = ni)
        cls_dist = distances.get_func(args.cls_dist, path_data = path_data)
        clusters_nodes = init.clustering.get_function(method = args.cls_method, nodes = path_data.nodes, n_cluster = args.n_cls, dist = cls_dist)()
        plt.figure()
        world.plot_world()

        for i, nodes in enumerate(clusters_nodes):
            plt.scatter(nodes[0][0], nodes[0][1], color=cmap(i), marker='x')
            plt.scatter(
                [node[0] for node in nodes[1:]],
                [node[1] for node in nodes[1:]],
                color=cmap(i), marker='o'
            )

        if args.output is not None:
            plt.savefig(args.output.format(i=ni))
        else:
            plt.show()
        plt.close()


if __name__ == '__main__':
    main()
