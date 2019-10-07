#!env/bin/python
import tsp.file
import argparse
import distance
import output
import opu.firefly

import numpy as np
import init
import random

def main():

    n_drones_min = 1
    n_drones_max = 9

    # Parse arguments
    argp = argparse.ArgumentParser(description='Run OPU firefly algorithm')
    argp.add_argument('-s'   , '--seed'             , type=int  , default =None , help='Seed value for random in calculation')
    argp.add_argument('-is'  , '--init_seed'        , type=int  , default =None , help='Seed value for random in initialization')
    argp.add_argument('-n'   , '--number'           , type=int  , required=True , help='Number of positions')
    argp.add_argument('-g'   , '--gamma'            , type=float, required=True , help='Gamma value (beta-step coefficient)')
    argp.add_argument('-a'   , '--alpha'            , type=float, required=True , help='Alpha value (alpha-step coefficient)')
    argp.add_argument('-ba'  , '--blocked_alpha'    , type=float, default =None , help='Alpha value on fireflies are blocked (Default for do nothing)')
    argp.add_argument('-u'   , '--u_weight'         , type=float, required=True , help='Uncertainty rate value')
    argp.add_argument('-mind', '--min_distance'     , type=float, default=10000 , help='Assumed minimum distance of permutation')
    argp.add_argument('-maxd', '--max_distance'     , type=float, default=20000 , help='Assumed maximum distance of permutation')
    argp.add_argument('-t'   , '--n_iterate'        , type=int  , required=True , help='Number of iteration')
    argp.add_argument('-ndr' , '--n_drones'         , type=int  , required=True , help='Number of drones ({} - {})'.format(n_drones_min, n_drones_max))
    argp.add_argument('-icl' , '--init_clustering'  , type=str  , default =None , choices=["rm", "pam"], help="Initialization clustering method (None for no clustering, 'rm' (random medoids) or 'pam' (partitioning around medoids))")
    argp.add_argument('-ico' , '--init_construction', type=str  , default ="random", choices=["random", "nn"] help="Initialization construction method ('random' (default) or 'nn' (nearest neighbor))") 
    argp.add_argument('-incl', '--init_n_clusters'  , type=int  , default =None , help="Number of clusters when `--init_clustering` is 'k-medoids'")
    argp.add_argument('-irr' , '--init_random_rate' , type=float, default =0    , help="Rate of nodes using Random method when `--init_method` is `nn`")
    argp.add_argument('-i'   , '--input'            , type=str  , default='res/opu01.tsp', help="Input tsp filepath")
    argp.add_argument('-o'   , '--output'           , type=str  , default =None , help='Path for output log (Default for auto)')
    argp.add_argument('-q'   , '--quiet'            , action='store_true'       , help='Do not show progress to stderr')
    argp.add_argument(         '--verbose'          , action='store_true'       , help='Whether to output details for debugging')
    argp.add_argument(         '--unsafe'           , action='store_true'       , help='Whether to check validation of permutation on each iteration')
    argp.add_argument(         '--init_only'        , action='store_true'       , help='Run only initialization')
    argp.add_argument(         '--stdout'           , action='store_true'       , help='Whether output results to stdout or not (output to automatically created file)')
    argp.add_argument(         '--result_only'      , action='store_true'       , help='Output only final results to stdout')
    args = argp.parse_args()

    # Load coordinates and nodes
    (datalist, _) = tsp.file.load(args.input)
    coords = datalist['NODE_COORD_SECTION']

    if not (args.n_drones >= n_drones_min and args.n_drones <= n_drones_max):
        raise RuntimeError('Invalid number of drones. Specify an integer from {} to {}.'.format(n_drones_min, n_drones_max))

    nodes = list(coords)

    x = [0] * args.number

    clustering = init.Clustering(dist = opu.firefly.distance, n_cluster = args.n_cluster)

    nodes_of_clusters = clustering.apply(args.init_clustering)

    i_random_until = len(x) * args.random_rate

    for i in range(len(x)):
        if i < i_random_until:
            x[i] = init.randomly(nodes)
        else:
            x[i] = init_method(nodes)

    I = lambda perm : opu.firefly.luminosity(
        [tuple(coords[p]) for p in perm],
        n_drones = args.n_drones,
        u_weight = args.u_weight,
        min_distance = args.min_distance,
        max_distance = args.max_distance,
    )

    if not args.output : args.output = 'out/{date}/{datetime}.txt'

    return output.run(
        args,
        nodes    = nodes,
        x        = x,
        I        = I,
        distance = distance.hamming,
        format_x = '{x:>2}',
        format_init = '{i:>6}\t{Ix:12.8f}\t[{x}]',
        format_calc = '{t:>6}\t{Ix:12.8f}\t[{x}]',
        output_filename = args.output,
    )



if __name__ == '__main__':
    main()
