#!env/bin/python

import pickle
import argparse
import matplotlib.pyplot as plt
import sys
import os
sys.path.append(os.path.dirname(__file__) + '/../route_planner')

def main():

    argp = argparse.ArgumentParser(description='Route distribution checker')
    argp.add_argument('input', nargs='*', type=str, help='Input binary pickle files path')
    argp.add_argument('-o', '--output', type=str, default=None, help='Output figure image file path (None for display)')
    argp.add_argument('-nm', '--name', type=str, default=None, help='Name formatted text on each file')
    argp.add_argument('-t', '--title', type=str, default=None, help='Title text')
    argp.add_argument('-ud', '--use_distance', action='store_true', help='Show distance as value')
    argp.add_argument('-us', '--use_safety', action='store_true', help='Show safety as value')
    argp.add_argument('-sx', '--size_x', type=float, default=12, help='Figure size x (inch)')
    argp.add_argument('-sy', '--size_y', type=float, default=8, help='Figure size y (inch)')
    argp.add_argument('-dpi', '--dpi', type=float, default=200, help='Figure DPI (pixel per inch)')
    args = argp.parse_args()

    if args.use_distance and args.use_safety:
        raise RuntimeError('`--use_distance` and `--use_safety` cannot specified at the same time.')

    if args.use_distance:
        get_value = lambda ret: ret.best_plan.total_distance
        value_name = 'total distance'
    elif args.use_safety:
        get_value = lambda ret: ret.best_plan.average_safety
        value_name = 'average safety'
    else:
        get_value = lambda ret: ret.best_plan.value
        value_name = 'value'

    data = []
    names = []

    for cinput in args.input:

        with open(cinput, mode='rb') as f:
            out_bin = pickle.load(f)

        data.append([get_value(last_ret) for last_ret in out_bin.lasts.values()])

        if args.name is not None:
            names.append(args.name.format(**out_bin.args.__dict__))
        else:
            names.append(os.path.splitext(os.path.basename(cinput))[0])

    indexes = list(range(1, len(names)+1))

    plt.figure(figsize=(args.size_x, args.size_y))
    plt.violinplot(list(reversed(data)), indexes, points=80, vert=False, widths=0.7, showextrema=True, showmedians=True)
    plt.yticks(indexes, list(reversed(names)))
    plt.xlabel(value_name)
    if args.title: plt.title(args.title)

    if args.output:
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        plt.savefig(args.output, dpi=args.dpi)
    else:
        plt.show()

    plt.close()


if __name__ == '__main__':
    main()
