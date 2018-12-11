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
#    argp.add_argument('-irn' , '--init_random_number', type=int  , default =1    , help='Number of randomly choosen nodes in initialization')
    args = argp.parse_args()

    # Load coordinates and nodes
    (datalist, _) = tsp.file.load('res/opu01.tsp')
    coords = datalist['NODE_COORD_SECTION']

    nodes = list(coords)


    # Set seed value of random
    if args.init_seed == None: args.init_seed = random.randrange(2 ** 32 - 1)
    np.random.seed(seed = args.init_seed)

    init_dist = lambda perm : opu.firefly.distance([tuple(coords[p]) for p in perm])
    



    print('Benchmark nearest naver initialization')
    print('{}'.format(vars(args)))

    for n_init_random in range(1, len(nodes)+1):
        
        x = [0] * args.number

        for i in range(len(x)):
            x[i] = init.nearest_naver(nodes, init_dist, n_init_random)

        dist_x = list(map(init_dist, x))
        ave_Ix = np.average(dist_x)
        print('{:>3} {:14.6f}'.format(n_init_random, ave_Ix))



if __name__ == '__main__':
    main()
