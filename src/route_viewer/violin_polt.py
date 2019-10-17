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
    argp.add_argument('-nm', '--name', type=str, default=None, help='Name formatted text on each file')
    argp.add_argument('-t', '--title', type=str, default=None, help='Title text')
    args = argp.parse_args()
    
    data = []
    names = []

    for cinput in args.input:

        with open(cinput, mode='rb') as f:
            out_bin = pickle.load(f)

        data.append([last_ret.best_plan.value for last_ret in out_bin.lasts.values()])
        if args.name is not None:
            names.append(args.name.format(**out_bin.args.__dict__))
        else:
            names.append(os.path.splitext(os.path.basename(cinput))[0])

    indexes = list(range(1, len(names)+1))
    plt.violinplot(data, indexes, points=80, vert=False, widths=0.7, showextrema=True, showmedians=True)
    plt.yticks(indexes, names)
    if args.title: plt.title(args.title)
    plt.show()



if __name__ == '__main__':
    main()
