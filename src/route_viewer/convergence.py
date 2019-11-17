#!env/bin/python
from collections import defaultdict
import argparse
import os
import pickle

from attrdict import AttrDict #type:ignore
import matplotlib.pyplot as plt #type:ignore

def main():

    argp = argparse.ArgumentParser(description='Route binary viewer')
    argp.add_argument('input' , nargs='+', type=str, help='Input binary pickle file path (multiple)')
    argp.add_argument('-o', '--output' , type=str, default=None, help='Output figure file directory (None to display)')
    argp.add_argument('-imin', '--itr_min' , type=int, default = 0  , help='Minimum iteration')
    argp.add_argument('-imax', '--itr_max' , type=int, required=True, help='Maximum iteration')
    argp.add_argument('-iinv', '--itr_inv' , type=int, default =10  , help='Interval of iteration')
    argp.add_argument('-sx', '--size_x', type=float, default=12, help='Figure size x (inch)')
    argp.add_argument('-sy', '--size_y', type=float, default=8, help='Figure size y (inch)')
    argp.add_argument('-dpi', '--dpi', type=float, default=200, help='Figure DPI (pixel per inch)')
    argp.add_argument('-t', '--title', type=str, default=None, help='Title formatted text')
    args = argp.parse_args()
    
    if args.output: os.makedirs(args.output, exist_ok=True)

    values_on_itrs = defaultdict(lambda: []) 

    for cinput in args.input:
        print(cinput)

        with open(cinput, mode='rb') as f:
            out_bin = pickle.load(f)

        itrs = list(range(args.itr_min, args.itr_max, args.itr_inv))

        for states in out_bin.states_by_seed.values():
            for itr in itrs:
                state = states[itr]
                values_on_itrs[state.itr].append(state.best_plan.value)

    plt.figure(figsize=(args.size_x, args.size_y))
    plt.violinplot(values_on_itrs, itrs, points=80, vert=True, widths=0.7, showextrema=True, showmedians=True)   
    if args.title: plt.title(args.title)

    if args.output:
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        plt.savefig(args.output, dpi=args.dpi)
    else:
        plt.show()

    plt.close()


if __name__ == '__main__':
    main()
