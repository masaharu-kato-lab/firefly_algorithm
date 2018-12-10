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
    argp = argparse.ArgumentParser(description='Benchmark nearest naver initialization')
    argp.add_argument('-is', '--init_seed'           , type=int  , default =None , help='Seed value for random in initialization')
    argp.add_argument('-n' , '--number'              , type=int  , required=True , help='Number of positions')
    argp.add_argument('-irn' , '--init_random_number', type=int  , default =1    , help='Number of randomly choosen nodes in initialization')
    argp.add_argument('-e' , '--eta'                 , type=float, required=True , help='Eta value (distance penalization coefficient)')
    argp.add_argument('-d' , '--n_drones'            , type=int  , required=True , help='Number of drones ({} - {})'.format(n_drones_min, n_drones_max))
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

    Ix = list(map(I, x))
    ave_Ix = np.average(Ix)




    print('Benchmark nearest naver initialization')
    print('{}'.format(vars(args)))
    print('{:14.6f}'.format(ave_Ix))


if __name__ == '__main__':
    main()
