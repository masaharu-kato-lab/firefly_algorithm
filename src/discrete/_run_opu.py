#!env/bin/python
import tsp.file
import argparse
import distance
import output
import opu.firefly
import pickle

import evaluator
import settings

import numpy as np
import init
import random

def main():

    n_drones_min = 1
    n_drones_max = 9

    # Parse arguments
    argp = argparse.ArgumentParser(description='Run OPU firefly algorithm')
    argp.add_argument('-s'  , '--seed'            , type=int  , default =None , help='Seed value for random in calculation')
    argp.add_argument('-is' , '--init_seed'       , type=int  , default =None , help='Seed value for random in initialization')
    argp.add_argument('-n'  , '--number'          , type=int  , required=True , help='Number of positions')
    argp.add_argument('-g'  , '--gamma'           , type=float, required=True , help='Gamma value (beta-step coefficient)')
    argp.add_argument('-a'  , '--alpha'           , type=float, required=True , help='Alpha value (alpha-step coefficient)')
    argp.add_argument('-ba' , '--blocked_alpha'   , type=float, default =None , help='Alpha value on fireflies are blocked (Default for do nothing)')
    argp.add_argument('-u'  , '--u_weight'        , type=float, required=True , help='Uncertainty rate value (available in Jordan evaluator)')
    argp.add_argument('-mnd', '--min_distance'    , type=float, default=10000 , help='Assumed minimum distance of permutation (available in Jordan evaluator)')
    argp.add_argument('-mxd', '--max_distance'    , type=float, default=20000 , help='Assumed maximum distance of permutation (available in Jordan evaluator)')
    argp.add_argument('-t'  , '--tlen'            , type=int  , required=True , help='Number of calculation')
    argp.add_argument('-d'  , '--n_drones'        , type=int  , required=True , help='Number of drones ({} - {})'.format(n_drones_min, n_drones_max))
    argp.add_argument(        '--init'            , type=str  , default ='nn' , help="Initialization method ('random' , 'nn' (nearest neighbor), 'knn' (k-means clustering and nearest neighbor)") 
    argp.add_argument('-k'  , '--knn_k'           , type=int  , default =None , help="K value when initialization method is 'knn' or 'hknn'")
    argp.add_argument('-rr' , '--random_rate'     , type=float, default =0    , help="Rate of nodes using Random method (normally using with initialize method 'knn'")
    argp.add_argument('-i'  , '--input'           , type=str  , default='res/opu01.tsp', help="Input tsp filepath")
    argp.add_argument('-o'  , '--output'          , type=str  , default =None , help='Path for output log (Default for auto)')
    argp.add_argument('-e'  , '--evaluator'       , type=str  , default ='jordan', help="Name of path evaluator ('jordan' or 'simon') ")
    argp.add_argument('-jo' , '--json_output'     , type=str  , default =None , help='Json output filepath (available in Simon evaluator. No json output if None.)')
    argp.add_argument('-q'  , '--quiet'           , action='store_true'       , help='Do not show progress to stderr')
    argp.add_argument(        '--verbose'         , action='store_true'       , help='Whether to output details for debugging')
    argp.add_argument(        '--unsafe'          , action='store_true'       , help='Whether to check validation of permutation on each iteration')
    argp.add_argument(        '--init_only'       , action='store_true'       , help='Run only initialization')
    argp.add_argument(        '--stdout'          , action='store_true'       , help='Whether output results to stdout or not (output to automatically created file)')
    argp.add_argument(        '--result_only'     , action='store_true'       , help='Output only final results to stdout')
    args = argp.parse_args()

    args.evaluator = args.evaluator.lower()

    # Load coordinates and nodes
    if args.evaluator == 'jordan':
        if not (args.n_drones >= n_drones_min and args.n_drones <= n_drones_max):
            raise RuntimeError('Invalid number of drones. Specify an integer from {} to {}.'.format(n_drones_min, n_drones_max))

        (datalist, _) = tsp.file.load(args.input)

        coords = {}
        for index, point in datalist['NODE_COORD_SECTION'].items():
            coords[index] = tuple(point)
        
        nodes = list(coords)

    elif args.evaluator == 'simon':

        coords = {}
        for index, point in enumerate(settings.CHECKPOINT_ORDERED, start=0):
            coords[index] = point

        nodes = list(coords)
        nodes.remove(0)

    else:
        raise RuntimeError("Unknown path evaluator :" + args.evaluator)


    print("coords:", coords)
    print("nodes:", nodes)


    x = [0] * args.number
    init_method = init.method(
        args.init,
        lambda perm : opu.firefly.distance([coords[p] for p in perm]),
        args.init_seed,
        knn_k = args.knn_k
    )

    i_random_until = len(x) * args.random_rate

    for i in range(len(x)):
        if i < i_random_until:
            x[i] = init.randomly(nodes)
        else:
            x[i] = init_method(nodes)

    
    if args.evaluator == 'jordan':
        I = lambda perm : opu.firefly.luminosity(
            [coords[p] for p in perm],
            n_drones = args.n_drones,
            u_weight = args.u_weight,
            min_distance = args.min_distance,
            max_distance = args.max_distance,
        )

    elif args.evaluator == 'simon':
        ev = evaluator.Evaluator()
        I = lambda perm : ev.evaluate([coords[i] for i in ([0] + list(perm))])

    else:
        raise RuntimeError("Unknown path evaluator :" + args.evaluator)
    

    if not args.output : args.output = 'out/{date}/{datetime}.txt'

    min_x = output.run(
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

    if args.evaluator == 'simon' and args.json_output:
        ev.json_output([coords[i] for i in ([0] + list(min_x))], args.json_output)



if __name__ == '__main__':
    main()
