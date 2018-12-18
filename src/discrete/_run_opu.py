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
    argp.add_argument('-s'  , '--seed'         , type=int  , default =None , help='Seed value for random in calculation')
    argp.add_argument('-is' , '--init_seed'    , type=int  , default =None , help='Seed value for random in initialization')
    argp.add_argument('-n'  , '--number'       , type=int  , required=True , help='Number of positions')
    argp.add_argument('-g'  , '--gamma'        , type=float, required=True , help='Gamma value (beta-step coefficient)')
    argp.add_argument('-a'  , '--alpha'        , type=float, required=True , help='Alpha value (alpha-step coefficient)')
    argp.add_argument('-ba' , '--blocked_alpha', type=float, default =None , help='Alpha value on fireflies are blocked (Default for do nothing)')
    argp.add_argument('-e'  , '--eta'          , type=float, required=True , help='Eta value (distance penalization coefficient)')
    argp.add_argument('-u'  , '--urate'        , type=float, required=True , help='Uncertainty rate value')
    argp.add_argument('-t'  , '--tlen'         , type=int  , required=True , help='Number of calculation')
    argp.add_argument('-d'  , '--n_drones'     , type=int  , required=True , help='Number of drones ({} - {})'.format(n_drones_min, n_drones_max))
    argp.add_argument('-i'  , '--init'         , type=str  , default ='nn' , help='Initialization method (\'random\' , \'nn\' (nearest neighbor), or \'knn\' (k-nearest neighbor))') 
    argp.add_argument('-k'  , '--knn_k'        , type=int  , default =None , help='K value when initialization method is k-nearest neighbor')
    argp.add_argument('-q'  , '--quiet'        , action='store_true'       , help='Do not show progress to stderr')
    argp.add_argument(        '--verbose'      , action='store_true'       , help='Whether to output details for debugging')
    argp.add_argument(        '--unsafe'       , action='store_true'       , help='Whether to check validation of permutation on each iteration')
    argp.add_argument('-ns' , '--nosort'       , action='store_true'       , help='Whether not to sort fireflies on each iteration')
    argp.add_argument('-fnr', '--fill_norandom', action='store_true'       , help='Fill empty elements in permutation not randomly')
    argp.add_argument(        '--init_only'    , action='store_true'       , help='Run only initialization')
    argp.add_argument(        '--stdout'       , action='store_true'       , help='Whether output results to stdout or not (output to automatically created file)')
    args = argp.parse_args()

    # Load coordinates and nodes
    (datalist, _) = tsp.file.load('res/opu01.tsp')
    coords = datalist['NODE_COORD_SECTION']

    if not (args.n_drones >= n_drones_min and args.n_drones <= n_drones_max):
        raise RuntimeError('Invalid number of drones. Specify an integer from {} to {}.'.format(n_drones_min, n_drones_max))

    nodes = list(coords)

    x = [0] * args.number
    init_method = init.method(
        args.init,
        lambda perm : opu.firefly.distance([tuple(coords[p]) for p in perm]),
        args.init_seed,
        knn_k = args.knn_k
    )

    for i in range(len(x)):
        x[i] = init_method(nodes)


    I = lambda perm : opu.firefly.luminosity([tuple(coords[p]) for p in perm], n_drones = args.n_drones, eta = args.eta, urate = args.urate)

    return output.run(
        args,
        nodes    = nodes,
        x        = x,
        I        = I,
        distance = distance.hamming,
        format_x = '{x:>2}',
        format_init = '{i:>6}\t{Ix:12.4f}\t[{x}]',
        format_calc = '{t:>6}\t{Ix:12.4f}\t[{x}]',
        format_output_filename = 'out/{date}/{datetime}.txt',
    )



if __name__ == '__main__':
    main()