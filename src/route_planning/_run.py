#!env/bin/python
import argparse
import numpy as np
import random

import firefly_with_log
import path
import init

def main():

    # Parse arguments
    argp = argparse.ArgumentParser(description='Run OPU firefly algorithm')
    argp.add_argument('-s'   , '--seed'         , type=int  , default =None , help='Seed value for random in calculation')
    argp.add_argument('-is'  , '--init_seed'    , type=int  , default =None , help='Seed value for random in initialization')
    argp.add_argument('-n'   , '--number'       , type=int  , required=True , help='Number of positions')
    argp.add_argument('-g'   , '--gamma'        , type=float, required=True , help='Gamma value (beta-step coefficient)')
    argp.add_argument('-a'   , '--alpha'        , type=float, required=True , help='Alpha value (alpha-step coefficient)')
    argp.add_argument('-ba'  , '--blocked_alpha', type=float, default =None , help='Alpha value on fireflies are blocked (Default for do nothing)')
    argp.add_argument('-sw'  , '--safety_weight', type=float, required=True , help='Weight value of safety on objective function')
    argp.add_argument('-mind', '--min_distance' , type=float, default=10000 , help='Assumed minimum distance of permutation')
    argp.add_argument('-maxd', '--max_distance' , type=float, default=20000 , help='Assumed maximum distance of permutation')
    argp.add_argument('-t'   , '--n_iterate'    , type=int  , required=True , help='Number of iteration')
    argp.add_argument('-ndr' , '--n_drones'     , type=int  , required=True , help='Number of drones')
    argp.add_argument('-i'   , '--input'        , type=str  , default='res/pathdata/opu.pickle', help="Input pathdata pickle filepath")
    argp.add_argument('-o'   , '--output'       , type=str  , default =None , help='Path for output log (Default for auto)')

    argp.add_argument('-icm' , '--init_clustering_method', type=str  , default =None , choices=["rm", "pam"], help="Initialization clustering method (None for no clustering, 'rm' (random medoids) or 'pam' (partitioning around medoids))")
    argp.add_argument('-inc' , '--init_n_cluster'        , type=int  , default =None , help="Number of clusters when `--init_clustering` is 'k-medoids'")
    argp.add_argument('-innr', '--init_nn_rate', type=float, default =0    , help="Rate of nodes using nearest neighbor when building path")

    argp.add_argument('-q' ,'--quiet'      , action='store_true'       , help='Do not show progress to stderr')
    argp.add_argument(      '--verbose'    , action='store_true'       , help='Whether to output details for debugging')
    argp.add_argument(      '--unsafe'     , action='store_true'       , help='Whether to check validation of permutation on each iteration')
    argp.add_argument(      '--init_only'  , action='store_true'       , help='Run only initialization')
    argp.add_argument(      '--stdout'     , action='store_true'       , help='Whether output results to stdout or not (output to automatically created file)')
    argp.add_argument(      '--result_only', action='store_true'       , help='Output only final results to stdout')
    args = argp.parse_args()

    # Load coordinates and nodes
    path_data = path.PathData(args.input)
    nodes = path_data.nodes
    dist_func = path_data.distance

    x = init.generate(
        nodes = path_data.nodes,
        number = args.number,
        clustering_method = args.init_clustering_method,
        n_cluster = args.init_n_cluster,
        nn_rate = args.init_nn_rate,
        dist_func = dist_func
    )

    # print(x)
    # exit()

    I = lambda perm : path.calc_evaluation_value(
        [perm],
        path_data = path_data,
        n_drones = args.n_drones,
        safety_weight = args.safety_weight,
        distance_range = range(args.min_distance, args.max_distance)
    )

    if not args.output : args.output = 'out/{date}/{datetime}.txt'

    return firefly_with_log.run(
        args,
        nodes    = nodes,
        x        = x,
        I        = I,
        format_x_elm = '{elm:>2}',
        format_init = '{i:>6}\t{Ix:12.8f}\t[{x}]',
        format_calc = '{t:>6}\t{Ix:12.8f}\t[{x}]',
        output_filename = args.output,
    )



if __name__ == '__main__':
    main()
