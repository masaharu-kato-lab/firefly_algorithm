#!env/bin/python
import argparse
import os
import pickle
import sys

from attrdict import AttrDict #type:ignore

sys.path.append(os.path.dirname(__file__) + '/../route_planner')

def main():

    argp = argparse.ArgumentParser(description='Route binary viewer')
    argp.add_argument('input', nargs='+', type=str, help='Input binary pickle file path')
    args = argp.parse_args()


    for cinput in args.input:
        with open(cinput, mode='rb') as f:
            out_bin = pickle.load(f)

        final_states = out_bin.final_states_by_seed.values()
        values = [state.best_plan.value for state in final_states]
        print(cinput + '\t' + '\t'.join('{:.4f}'.format(v) for v in values))
        


if __name__ == '__main__':
    main()
