#!env/bin/python
import argparse
import pickle
import sys
import os

from attrdict import AttrDict #type:ignore

from typing import Any, Callable, Dict, Iterable, Iterator, List

sys.path.append(os.path.dirname(__file__) + '/../route_planner')

def main():

    argp = argparse.ArgumentParser(description='Route binary viewer')
    argp.add_argument('input'                 , type=str, nargs='+',     help='Input binary pickle file path')
    argp.add_argument('-xmax', '--x_max'      , type=int, required=True, help='Maximum X value')
    argp.add_argument('-xinv', '--x_interval' , type=int, required=True, help='X value interval')
    argp.add_argument('-ts'  , '--target_seed', type=int, default = 0  , help='Target seed value')
    args = argp.parse_args()

    xlist = range(0, args.x_max+1, args.x_interval)
    
    # print x value (number of updates)
    print('\t'.join(['{:20}'.format(''), *('{:>10}'.format(x) for x in xlist)]))

    for _input in args.input:

        name = '{} (seed={})'.format(os.path.splitext(os.path.basename(_input))[0], args.target_seed)

        with open(_input, mode='rb') as f:
            binary = pickle.load(f)

        variants = binary.variants_by_seed[args.target_seed]
        print('\t'.join(['{:20}'.format(name), *('{:10.03f}'.format(variants[x]) for x in xlist)]))



if __name__ == '__main__':
    main()
