#!env/bin/python
import argparse
import os
import pickle
import sys

from attrdict import AttrDict #type:ignore
import matplotlib.pyplot as plt #type:ignore

sys.path.append(os.path.dirname(__file__) + '/../route_planner')

def main():

    argp = argparse.ArgumentParser(description='Route binary viewer')
    argp.add_argument('input', nargs='+', type=str, help='Input binary pickle file path')
    argp.add_argument('-o', '--output' , type=str, default=None, help='Output figure file path (None to display)')
    argp.add_argument('-t', '--title', type=str, default=None, help='Title text')
    argp.add_argument('-x', '--xtype', type=str, choices=['iteration', 'n_best_updates', 'n_updates'], default='iteration', help='Value type for x-value of graph')
    argp.add_argument('-y', '--ytype', type=str, choices=['value'], default='value', help='Value type for y-value of graph')
    argp.add_argument('-ms', '--marker_size', type=float, default=10, help='Scatter marker size')
    argp.add_argument('-sx', '--size_x', type=float, default=12, help='Figure size x (inch)')
    argp.add_argument('-sy', '--size_y', type=float, default=8, help='Figure size y (inch)')
    argp.add_argument('-dpi', '--dpi', type=float, default=200, help='Figure DPI (pixel per inch)')
    argp.add_argument('-gl', '--group_length', type=float, default=None, help='Group length')
    args = argp.parse_args()
    
    cmap = plt.get_cmap("tab10")
    mmap = ['o', 'x', 's', '+', 'D', 'H', 'd', 'h', '8']

    x_factory = {
        'iteration'      : lambda states: (state.best_itr  for state in states),
        'n_best_updates' : lambda states: (state.n_best_updates for state in states),
        'n_updates'      : lambda states: (state.n_updates for state in states),
    }[args.xtype]

    y_factory = {
        'value': lambda states: (state.best_plan.value for state in states),
    }[args.ytype]

    if args.output and os.path.dirname(args.output): os.makedirs(os.path.dirname(args.output), exist_ok=True)
    if not args.group_length: args.group_length = len(args.input)

    plt.figure(figsize=(args.size_x, args.size_y))
    for i, cinput in enumerate(args.input):
        with open(cinput, mode='rb') as f:
            out_bin = pickle.load(f)

        final_states = out_bin.final_states_by_seed.values()
        plt.scatter(
            [*x_factory(final_states)],
            [*y_factory(final_states)],
            color=cmap(int(i % args.group_length)),
            marker=mmap[int(i // args.group_length)],
            label=os.path.splitext(os.path.basename(cinput))[0],
            s = args.marker_size
        )
        
    plt.legend()
    if args.title is not None:
        plt.title(args.title)

    if args.output:
        plt.savefig(args.output, dpi=args.dpi)
    else:
        plt.show()

    plt.close()


if __name__ == '__main__':
    main()
