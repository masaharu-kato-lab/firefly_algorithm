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
    argp.add_argument('-s' , '--seed'         , type=int  , default =None , help='Seed value for random in calculation')
    argp.add_argument('-is', '--init_seed'    , type=int  , default =None , help='Seed value for random in initialization')
    argp.add_argument('-n' , '--number'       , type=int  , required=True , help='Number of positions')
    argp.add_argument('-g' , '--gamma'        , type=float, required=True , help='Gamma value (beta-step coefficient)')
    argp.add_argument('-a' , '--alpha'        , type=float, required=True , help='Alpha value (alpha-step coefficient)')
    argp.add_argument('-ba', '--blocked_alpha', type=float, default =None , help='Alpha value on fireflies are blocked (Default for do nothing)')
    argp.add_argument('-e' , '--eta'          , type=float, required=True , help='Eta value (distance penalization coefficient)')
    argp.add_argument('-t' , '--tlen'         , type=int  , required=True , help='Number of calculation')
    argp.add_argument('-d' , '--n_drones'     , type=int  , required=True , help='Number of drones ({} - {})'.format(n_drones_min, n_drones_max))
    argp.add_argument(       '--verbose'      , action="store_true"       , help='Whether to output details for debugging')
    argp.add_argument(       '--stdout'       , action="store_true"       , help='Whether output results to stdout or not (output to automatically created file)')
    args = argp.parse_args()

    # Load coordinates and nodes
    (datalist, _) = tsp.file.load('res/opu01.tsp')
    coords = datalist['NODE_COORD_SECTION']

    if not (args.n_drones >= n_drones_min and args.n_drones <= n_drones_max):
        raise RuntimeError('Invalid number of drones. Specify an integer from {} to {}.'.format(n_drones_min, n_drones_max))

    nodes = list(coords)



    # Set seed value of random
    if args.init_seed == None: args.init_seed = random.randrange(2 ** 32 - 1)
    np.random.seed(seed = args.init_seed)


    I = lambda perm : opu.firefly.luminosity([tuple(coords[p]) for p in perm], n_drones = args.n_drones, eta = args.eta)
    x = [0] * args.number

    for i in range(len(x)):
        x[i] = init.nearest_naver(nodes, I)


    return output.run(
        args,
        nodes    = nodes,
        x        = x,
        I        = I,
        distance = distance.hamming,
    )



if __name__ == '__main__':
    main()
