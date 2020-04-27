#!env/bin/python
import argparse
import os
import pickle
import sys

from attrdict import AttrDict #type:ignore

sys.path.append(os.path.dirname(__file__) + '/../route_planner')

def main():

    argp = argparse.ArgumentParser(description='Route binary viewer')
    argp.add_argument('input',    nargs='+', type=str, help='Input binary pickle file path')
    argp.add_argument('-iu'  , '--i_update', type=int, required=True, help='Target index of updates')
    args = argp.parse_args()


    for cinput in args.input:
        with open(cinput, mode='rb') as f:
            out_bin = pickle.load(f)
        values = [(bests[args.i_update] if len(bests) > args.i_update else None) for bests in out_bin.bests_by_seed.values()]
        print(cinput + '\t' + '\t'.join('{:.4f}'.format(v) for v in values))
        

if __name__ == '__main__':
    main()
